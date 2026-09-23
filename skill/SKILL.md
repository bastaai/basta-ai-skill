---
name: basta
description: Integration with Basta auction and marketplace (ecommerce) APIs. Use when users want to create auctions, manage sales, handle bidding, or build a storefront (products, carts, checkout, orders, fulfillment) using Basta's GraphQL APIs — the auction Management API and Client API, and the Marketplace Shop API and Admin API. Trigger on requests involving auctions, sales, items, bids, bidders, real-time auction updates, make-an-offer/negotiation, buy-now, Dutch (descending-clock) auctions, consignments, live-sale clerking, or ecommerce products, variants, collections, carts, orders, and checkout.
---

# Basta API Integration

## Overview

Basta is an API-first commerce engine spanning two product surfaces: **Auctions** (sales,
items, bidding, dynamic pricing) and a **Marketplace** (a full ecommerce stack — products,
variants, carts, checkout, orders, fulfillment, payments, promotions, tax, shipping). This
skill provides workflows for integrating with Basta's four GraphQL APIs across both
surfaces.

## API Architecture

Basta provides **four** GraphQL APIs across two surfaces.

### Auction APIs

**Management API** (`https://management.api.basta.app`)
- Server-side, authenticated operations
- Create and manage sales/auctions
- Configure items, pricing, bid rules
- Generate bidder tokens
- Authentication: `x-account-id` and `x-api-key` headers

**Client API** (`https://client.api.basta.app`)
- Public-facing, client-side operations
- Browse auctions and items
- Place bids (with bidder token)
- Real-time updates via WebSocket subscriptions
- Authentication: Optional JWT bidder tokens

### Marketplace (ecommerce) APIs

**Shop API** (`https://marketplace.api.basta.app/shop/graphql`, playground at `/shop`)
- Public storefront operations: browse products/collections, search, build a cart, checkout
- Guest and authenticated shoppers; customer profile and order history
- Authentication: `MARKETPLACE-ACCOUNT-ID` header (required) + optional `Authorization: Bearer <JWT>`; guest carts via `x-marketplace-session` ⇄ `marketplace_session` cookie

**Admin API** (`https://marketplace.api.basta.app/admin/graphql`, playground at `/admin`)
- Dashboard operations: manage catalog, orders, fulfillment, payments/refunds, customers, promotions, shipping, tax, zones, settings, images
- Authentication: `x-account-id` + `x-api-key`, **or** `ory_kratos_session` cookie. Every operation also takes an `accountId: String!` argument
- API version: `2026-02`

See `references/marketplace_shop_api.md` and `references/marketplace_admin_api.md` for the
full Marketplace schemas. The auction workflows below cover the Management/Client APIs.

## Core Workflows

Basta provides **two flexible workflows** for managing items and sales:

**Workflow A: Direct Item Creation**
1. Create standalone items with `createItem`
2. Create sale
3. Add existing items to sale with `addItemToSale`
4. Publish sale

**Workflow B: Integrated Creation**
1. Create sale
2. Create items directly in sale with `createItemForSale`
3. Publish sale

### 1. Creating a Sale

Use Management API to create a sale:

```graphql
mutation CreateSale {
  createSale(accountId: "ACCOUNT_ID", input: {
    title: "Auction Title"
    description: "Auction description"
    currency: "USD"
    bidIncrementTable: {
      rules: [
        { lowRange: 0, highRange: 100000, step: 1000 }
      ]
    }
    closingMethod: OVERLAPPING
    closingTimeCountdown: 60000  # milliseconds
  }) {
    id
    status
  }
}
```

### 2a. Creating Standalone Items (Workflow A)

Create reusable items independent of any sale:

```graphql
mutation CreateItem {
  createItem(accountId: "ACCOUNT_ID", input: {
    title: "Item Title"
    description: "Item description"
    startingBid: 1000  # cents
    reserve: 50000     # cents
  }) {
    id
    title
    status
  }
}
```

### 2b. Adding Existing Items to Sale (Workflow A)

Add previously created items to a sale:

```graphql
mutation AddItemToSale {
  addItemToSale(accountId: "ACCOUNT_ID", input: {
    saleId: "SALE_ID"
    itemId: "ITEM_ID"  # From createItem
    allowedBidTypes: [MAX]
    openDate: "2024-02-01T15:00:00Z"
    closingDate: "2024-02-01T16:00:00Z"
  }) {
    id
    status
    dates {
      openDate
      closingStart
      closingEnd
    }
  }
}
```

### 2c. Creating Items Directly in Sale (Workflow B)

Create and add items to a sale in one operation:

```graphql
mutation CreateItemForSale {
  createItemForSale(accountId: "ACCOUNT_ID", input: {
    saleId: "SALE_ID"
    title: "Item Title"
    description: "Item description"
    startingBid: 1000  # cents
    reserve: 50000     # cents
    allowedBidTypes: [MAX]
    openDate: "2024-02-01T15:00:00Z"
    closingDate: "2024-02-01T16:00:00Z"
  }) {
    id
    status
    dates {
      openDate
      closingStart
      closingEnd
    }
  }
}
```

### 3. Publishing the Sale

```graphql
mutation PublishSale {
  publishSale(accountId: "ACCOUNT_ID", input: {
    saleId: "SALE_ID"
  }) {
    id
    status
  }
}
```

### 4. Creating Bidder Tokens

Generate JWT tokens for bidders:

```graphql
mutation CreateBidderToken {
  createBidderToken(accountId: "ACCOUNT_ID", input: {
    metadata: {
      userId: "user-123"
      ttl: 60  # minutes
    }
  }) {
    token
    expiration
  }
}
```

### 5. Placing Bids

Use Client API with bidder token. Basta supports two bid types:

**MaxBid (Proxy Bidding):**
- User sets maximum amount willing to pay
- Auction engine automatically bids incrementally
- Winning amount may be lower than max
- Engine reacts to counter-bids up to max amount

**NormalBid (Direct Bidding):**
- One-time bid at specified amount
- Must align with bid increment table
- Does not react to counter-bids

```graphql
# Headers: { "Authorization": "Bearer BIDDER_TOKEN" }
mutation BidOnItem {
  bidOnItem(
    saleId: "SALE_ID"
    itemId: "ITEM_ID"
    amount: 10000  # cents
    type: MAX       # or NORMAL
  ) {
    __typename
    ... on BidPlacedSuccess {
      amount
      bidStatus
      date
      bidType
    }
    ... on BidPlacedError {
      errorCode
      error
    }
  }
}
```

## Real-time Updates (saleActivity Subscription)

Both APIs support a `saleActivity` GraphQL subscription over WebSocket for real-time sale and item updates.

The subscription returns a **union type** `SaleActivity = Sale | SaleItem`, meaning each message is either a full `Sale` update or a `SaleItem` update. Use inline fragments (`... on Sale`, `... on SaleItem`) to handle both.

### Management API Subscription

**Endpoint:** `wss://management.api.basta.app/query`
**Protocol:** graphql-ws

Authenticate via HTTP headers on the WebSocket upgrade request (same as regular API calls):
```
x-account-id: YOUR_ACCOUNT_ID
x-api-key: YOUR_API_KEY
```

```graphql
subscription {
  saleActivity(accountId: "ACCOUNT_ID", saleId: "SALE_ID") {
    ... on Sale {
      id
      title
      status
    }
    ... on SaleItem {
      id
      title
      status
      currentBid
      totalBids
      leaderId
      dates {
        openDate
        closingStart
        closingEnd
      }
    }
  }
}
```

### Client API Subscription

**Endpoint:** `wss://client.api.basta.app/query`
**Protocol:** graphql-ws

Connect with bidder token in `connection_init` payload:

```json
{
  "type": "connection_init",
  "payload": {
    "token": "BIDDER_TOKEN"
  }
}
```

```graphql
subscription {
  saleActivity(saleId: "SALE_ID") {
    ... on Sale {
      id
      title
      status
    }
    ... on Item {
      id
      title
      status
      currentBid
      totalBids
      leaderId
      dates {
        openDate
        closingStart
        closingEnd
      }
    }
  }
}
```

### Filtering by Item IDs

Both APIs accept an optional `itemIdFilter` to limit updates to specific items:

```graphql
subscription {
  saleActivity(
    accountId: "ACCOUNT_ID"  # Management API only
    saleId: "SALE_ID"
    itemIdFilter: { itemIds: ["item_1", "item_2"] }
  ) {
    ... on Sale { id status }
    ... on SaleItem { id status currentBid totalBids leaderId }
  }
}
```

Sale-level updates are always included regardless of the item filter.

## Webhooks

Basta can notify your application when events occur via webhooks. Configure webhooks in the admin portal settings.

**Webhook Structure:**
```json
{
  "idempotencyKey": "UNIQUE_STRING",
  "actionType": "EVENT_TYPE",
  "data": { }
}
```

**Event Types:**

**BidOnItem** - Sent when a bid is placed:
```json
{
  "bidId": "...",
  "saleId": "...",
  "itemId": "...",
  "userId": "...",
  "amount": 500,
  "maxAmount": 500,
  "saleState": {
    "newLeader": "...",
    "currentBid": 600,
    "currentMaxBid": 600
  },
  "reactiveBids": [...]
}
```

**SaleStatusChanged** - Sent when sale status changes:
```json
{
  "saleId": "...",
  "saleStatus": "OPEN"
}
```

**ItemsStatusChanged** - Sent when item statuses change:
```json
{
  "saleId": "...",
  "itemStatusChanges": [{
    "itemId": "...",
    "itemStatus": "CLOSING",
    "saleState": {...}
  }]
}
```

## Auction Fees & Registrations

Two operator-side auction capabilities, both managed through the **Management API**:

**Fees** — buyer/seller charges (e.g. Buyer's Premium, Platform Fee) resolved through an
**account → sale → item** cascade (item overrides sale overrides account). Configure with
`createAccountFee` / `createSaleFee` / `createSaleItemFee` (+ update/delete, and
`resetSaleFees`). Read effective fees via `Sale.feeRules` / `SaleItem.feeRules` (each
`FeeRule` has a `source`); placed-order `OrderLine`s expose `fees` and `sellerFees`. Fee
`value` is `500` = 5% (`PERCENTAGE`) or `1000` = $10 (`AMOUNT`, minor units), with
`FLAT`/`PROGRESSIVE` bracket calculation.

**Registrations** — bidders are registered to a sale (types `ONLINE`/`PHONE`/`PADDLE`/
`AGGREGATOR`; status `PENDING`→`ACCEPTED`/`REJECTED`) and gated by `Sale.bidRestrictions`
and CEL-based registration policies. Use `createSaleRegistration` → `acceptSaleRegistration`
/ `rejectSaleRegistration`, per-item `createSaleItemRegistration`, and policy
create/update/attach/detach mutations. **Registration is operator-driven via the Management
API** — the Client API only exposes the bidder's own registrations
(`Sale.userSaleRegistrations`, `bidRestrictions`) read-only.

See `references/fees_and_registrations.md` for the full reference.

## Watchlist, Highlighted Items & Metafields

Three auction merchandising/personalisation features spanning both auction APIs:

- **Watchlist / favourites** — bidders favourite sales/items/accounts on the **Client API**
  (`subscribeToSale`, `subsribeToItem` *(sic — misspelled in schema)*, `subscribeToAccount`,
  + `unsubscribe*`; `isUserSubscribed`). Operators read the resulting watchlist on the
  **Management API** (`Sale.watchlist`, `SaleItem.watchlist`).
- **Highlighted items** — feature items on a sale page, ordered by `position`. Set
  `highlight` on item create/update and reorder with `reorderHighlightedItems`; read via
  `Sale.highlighted` / `SaleItem.highlight` (`Item.highlight` on the Client API).
- **Metafields** — arbitrary key/value custom data on Account/Sale/Item/SaleItem
  (single-line or rich text). Read with `metafields`/`metafield`; write (Management API)
  with `setMetafields` (≤10 at a time) and `deleteMetafield`.

See `references/watchlist_highlights_metafields.md` for the full reference.

## Offers, Buy-Now, Dutch Auctions & Live Sales

Beyond classic English (ascending) bidding, the auction APIs support:

- **Make-an-offer (negotiation)** — buyers privately negotiate a price on the **Client API**
  (`makeOffer`, `counterOffer`, `acceptCounter`, `withdrawOffer`, `offer`). Operators
  configure and decide on the **Management API** (`setItemOfferConfig` with an auto-accept
  threshold, `acceptOffer`/`rejectOffer`/`counterOffer`, read via `itemOffers`/`offers`).
  This is separate from the Marketplace Shop API's offers (same names, different endpoint).
- **Buy-Now** — a fixed price to buy outright: `setItemBuyNowConfig` and the terminal
  `buyItem` (on behalf of a buyer; creates a payments order) on the Management API.
- **Dutch (descending-clock) auctions** — lots start high and drop on a schedule until a
  buyer accepts. Buyers call `placeDutchBid` (Client API; `amount` must equal the current
  clock price or it's rejected with `PRICE_MISMATCH`). Operators use `createDutchSale` /
  `createDutchItemForSale`. Sales are polymorphic via `saleV2`/`salesV2` and `SaleV2`
  (`... on DutchSale`); real-time via `saleActivityV2`.
- **Live-sale clerking** — for `LIVE` sales, auctioneer ops `passLiveItem`, `sellLiveItem`,
  `sellLiveItemToBid` (pin a bid id), and live-stream attach/detach (Management API).
- **Notification preferences** — buyers opt in/out per event+channel with
  `setMyNotificationPreferences` (Client API).

See `references/client_api.md` and `references/management_api.md` for full signatures.

## Marketplace (Ecommerce) Workflows

The Marketplace engine is a full ecommerce stack, separate from the auction APIs. It can
stand alone or mirror auction items into purchasable variants (a `ProductVariant`'s
`customFields.bastaItemId` links it back to an auction item).

### Storefront (Shop API)

Typical browse → cart → checkout flow (send `MARKETPLACE-ACCOUNT-ID` on every request;
add `Authorization: Bearer <JWT>` for logged-in shoppers):

1. **Discover** — `products`, `collections`, `facets`, or `search` (full-text + facet /
   collection / price filters, with aggregations for filter UIs). `searchAsync` is a
   Typesense-index-backed variant search (typo tolerance, `filterBy`/`orderBy`, facet
   stats) that is faster but eventually consistent.
2. **Build the cart** — `addItemToOrder(productVariantId, quantity)` (a guest cart is
   auto-created), `adjustOrderLine`, `removeOrderLine`, `applyCouponCode`. Read the cart
   with `activeOrder`.
3. **Address & shipping** — `setOrderShippingAddress` (or `…FromUser` for a saved
   address), then `eligibleShippingMethods` → `setOrderShippingMethod`.
4. **Customer & checkout** — `setCustomerForOrder` (guest) then
   `transitionOrderToState("ArrangingPayment")`. Use `nextOrderStates` to discover legal
   transitions. All money is in minor units (cents), with net (`price`) and gross
   (`priceWithTax`) variants.

```graphql
# Headers: MARKETPLACE-ACCOUNT-ID: <account>   (+ optional Authorization: Bearer <jwt>)
mutation { addItemToOrder(productVariantId: "var_123", quantity: 1) { id totalWithTax } }
```

**Make-an-offer (negotiation).** For variants linked to a Basta auction item, authenticated
buyers can negotiate: `makeOffer` → seller counters (out of band) → buyer `counterOffer` /
`acceptCounter` / `declineOffer`. Read with `myOffers`, `offer(id)`, or `ProductVariant.offers`.
`awaitingParty` tracks whose turn it is. See `references/marketplace_shop_api.md`.

### Dashboard (Admin API)

Every Admin query/mutation takes `accountId: String!`. Capabilities: catalog
(`createProduct`, `createProductVariants`, `createProductVariantFromItem` to mint a variant
from a Basta auction item, option groups, collections, facets), order management (`orders`,
`transitionOrderToState`, `addManualPaymentToOrder`, `refundOrder`, `addFulfillmentToOrder`),
customers, promotions, shipping methods, shipping classes (`createShippingClass`, referenced
by a method's `allowedShippingClassIds`), tax categories/rates, zones/countries, marketplace
settings, read-only buyer offers (`ProductVariant.offers`), and a two-step image upload
(`createMarketplaceUploadUrl` → PUT → `upsertMarketplaceImage`).

```graphql
mutation CreateProduct($a: String!) {
  createProduct(accountId: $a, input: {
    name: "Field Notebook", slug: "field-notebook", enabled: true
  }) { id slug }
}
```

**Order state machine:** `Draft`/`AddingItems` → `ArrangingPayment` → `PaymentAuthorized`
→ `PaymentSettled` → (`PartiallyShipped`→`Shipped`, `PartiallyDelivered`→`Delivered`) ·
`Cancelled` · `Modifying`/`ArrangingAdditionalPayment`. Stock is deducted on entry to
`PaymentSettled` and restored on cancellation. See `references/marketplace_admin_api.md`.

## Implementation Guidelines

**Workflow Selection:**
- **Use Workflow A (createItem + addItemToSale)** when:
  - Items need to be reused across multiple sales
  - Building an item catalog/inventory system
  - Items are created before sales are scheduled
- **Use Workflow B (createItemForSale)** when:
  - Items are specific to a single sale
  - Creating items and sales in one flow
  - Simpler integration requirements

**Item Reusability:**
- Items created with `createItem` can be added to multiple sales
- Use `removeItemFromSale` to remove items without deleting them
- Update items with `updateItem` to modify across all sales

**Authentication:**
- Store API credentials securely
- Generate bidder tokens server-side only
- Include proper headers in all Management API requests

**Error Handling:**
- Check `__typename` for union return types
- Handle `BidPlacedError` responses
- Implement retry logic for network failures

**Rate Limits:**
- Management API: Use batch operations where possible
- Client API: Cache query results appropriately
- WebSocket: Implement reconnection logic

**Testing:**
- Test in GraphQL Playground: https://management.api.basta.app
- Verify bidder token generation and expiration
- Test WebSocket connections before production
- Test both workflows to understand which fits your use case

## Key Concepts

**Sale:** Container for one or more items being auctioned

**Item:** Individual lot within a sale

**Bid Increments:** Rules defining minimum bid increases

**Closing Method:** OVERLAPPING - items can close at different times

**Closing Time Countdown:** Time extension when bids arrive near closing

**Reserve:** Minimum price for item to sell

**Starting Bid:** Initial bid amount

**Bidder Token:** JWT granting permission to bid on behalf of a user

## Common Pitfalls

**Using the wrong mutation combination:**
- ❌ Wrong: Call `addItemToSale` with an item created via `createItemForSale`
- ✅ Correct: Use `addItemToSale` only with items created via `createItem`

**Missing sale context for item additions:**
- ❌ Wrong: Call `createItemForSale` or `addItemToSale` without a valid `saleId`
- ✅ Correct: Create sale first, then add/create items with the returned `saleId`

**Not understanding item lifecycle:**
- Items created with `createItem` are reusable across sales
- Items created with `createItemForSale` are tied to that specific sale
- Use `removeItemFromSale` to detach items without deletion

**Forgetting to publish:**
- Sales remain in `UNPUBLISHED` status until `publishSale` is called
- Items won't accept bids until the sale is published

## References

For detailed API schemas and examples:

**Auctions:**
- `references/management_api.md` - Complete auction Management API reference
- `references/client_api.md` - Complete auction Client API reference
- `references/fees_and_registrations.md` - Fee cascade (account/sale/item) and sale/item registrations across both auction APIs
- `references/watchlist_highlights_metafields.md` - Watchlist/favourites, highlighted items, and metafields across both auction APIs
- `references/webhooks.md` - Comprehensive webhooks guide with implementation examples

**Marketplace (ecommerce):**
- `references/marketplace_shop_api.md` - Storefront Shop API reference (products, search, cart, checkout)
- `references/marketplace_admin_api.md` - Dashboard Admin API reference (catalog, orders, fulfillment, promotions, tax)

**General:**
- `references/glossary.md` - Basta terminology and concepts
