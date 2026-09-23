# Management API Reference

**Base URL:** `https://management.api.basta.app`

**Authentication:** All requests require headers:
```json
{
  "x-account-id": "YOUR_ACCOUNT_ID",
  "x-api-key": "YOUR_API_KEY"
}
```

## Core Mutations

### createSale

Create a new auction sale.

**Input:**
- `title` (String!) - Sale title
- `description` (String) - Sale description
- `currency` (String!) - Currently only "USD" supported
- `bidIncrementTable` (BidIncrementTableInput) - Bid increment rules
- `closingMethod` (ClosingMethod!) - Only OVERLAPPING supported
- `closingTimeCountdown` (Int) - Time extension in milliseconds

**Returns:** Sale object with `id` and `status`

**Example:**
```graphql
mutation CreateSale {
  createSale(accountId: "ACCOUNT_ID", input: {
    title: "Estate Sale"
    description: "Fine art and antiques"
    currency: "USD"
    bidIncrementTable: {
      rules: [
        { lowRange: 0, highRange: 1000, step: 50 }
        { lowRange: 1000, highRange: 10000, step: 100 }
        { lowRange: 10000, highRange: 100000, step: 500 }
      ]
    }
    closingMethod: OVERLAPPING
    closingTimeCountdown: 120000
  }) {
    id
    status
    title
    currency
  }
}
```

### createItem

Create a standalone item that can be added to sales later.

**Input:**
- `title` (String!) - Item title
- `description` (String) - Item description
- `startingBid` (Int!) - Starting bid in cents
- `reserve` (Int) - Reserve price in cents

**Returns:** Item object

**Example:**
```graphql
mutation CreateStandaloneItem {
  createItem(accountId: "ACCOUNT_ID", input: {
    title: "Vintage Guitar"
    description: "1959 Les Paul Standard"
    startingBid: 500000  # $5,000
    reserve: 2000000     # $20,000
  }) {
    id
    title
    status
  }
}
```

### addItemToSale

Add an existing item to a sale.

**Input:**
- `saleId` (ID!) - Parent sale ID
- `itemId` (ID!) - Existing item ID (from `createItem`)
- `allowedBidTypes` ([BidType!]) - Allowed bid types (e.g., MAX, NORMAL)
- `openDate` (DateTime!) - When bidding opens
- `closingDate` (DateTime!) - When closing period begins

**Returns:** SaleItem object

**Example:**
```graphql
mutation AddExistingItem {
  addItemToSale(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    itemId: "item_xyz789"
    allowedBidTypes: [MAX]
    openDate: "2024-06-01T10:00:00Z"
    closingDate: "2024-06-07T20:00:00Z"
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

### createItemForSale

Create an item and add it to a sale in one operation.

**Input:**
- `saleId` (ID!) - Parent sale ID
- `title` (String!) - Item title
- `description` (String) - Item description
- `startingBid` (Int!) - Starting bid in cents
- `reserve` (Int) - Reserve price in cents
- `allowedBidTypes` ([BidType!]) - Allowed bid types (e.g., MAX, NORMAL)
- `openDate` (DateTime!) - When bidding opens
- `closingDate` (DateTime!) - When closing period begins

**Returns:** SaleItem object

**Example:**
```graphql
mutation CreateAndAddItem {
  createItemForSale(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    title: "Vintage Guitar"
    description: "1959 Les Paul Standard"
    startingBid: 500000  # $5,000
    reserve: 2000000     # $20,000
    allowedBidTypes: [MAX]
    openDate: "2024-06-01T10:00:00Z"
    closingDate: "2024-06-07T20:00:00Z"
  }) {
    id
    title
    status
    dates {
      openDate
      closingStart
      closingEnd
    }
  }
}
```

### removeItemFromSale

Remove an item from a sale without deleting it.

**Input:**
- `saleId` (ID!) - Sale ID
- `itemId` (ID!) - Item ID to remove

**Returns:** Success status

**Example:**
```graphql
mutation RemoveItem {
  removeItemFromSale(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    itemId: "item_xyz789"
  }) {
    success
  }
}
```

### publishSale

Publish a sale to make it live. After publishing, Basta manages the lifecycle.

**Input:**
- `saleId` (ID!) - Sale to publish

**Returns:** Sale object with updated status

**Example:**
```graphql
mutation Publish {
  publishSale(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
  }) {
    id
    status
    items {
      edges {
        node {
          id
          status
        }
      }
    }
  }
}
```

### createBidderToken

Generate a JWT token for a bidder.

**Input:**
- `metadata.userId` (String!) - Bidder's user ID
- `metadata.ttl` (Int!) - Token time-to-live in minutes

**Returns:** Token string and expiration timestamp

**Example:**
```graphql
mutation GenerateToken {
  createBidderToken(accountId: "ACCOUNT_ID", input: {
    metadata: {
      userId: "user_xyz789"
      ttl: 180  # 3 hours
    }
  }) {
    token
    expiration
  }
}
```

## Core Queries

### sale

Retrieve sale details.

**Arguments:**
- `accountId` (String!) - Your account ID
- `id` (ID!) - Sale ID

**Example:**
```graphql
query GetSale {
  sale(accountId: "ACCOUNT_ID", id: "sale_abc123") {
    id
    title
    status
    currency
    bidIncrementTable {
      rules {
        lowRange
        highRange
        step
      }
    }
    items {
      edges {
        node {
          id
          title
          status
          currentBid
          dates {
            openDate
            closingStart
            closingEnd
          }
        }
      }
    }
  }
}
```

### sales

List all sales for an account.

**Arguments:**
- `accountId` (String!) - Your account ID
- `first` (Int) - Limit results
- `after` (String) - Cursor for pagination

**Example:**
```graphql
query ListSales {
  sales(accountId: "ACCOUNT_ID", first: 10) {
    edges {
      node {
        id
        title
        status
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Type Definitions

### Sale
- `id` (ID!)
- `title` (String!)
- `description` (String)
- `status` (SaleStatus!) - UNPUBLISHED, PUBLISHED, OPEN, CLOSED
- `currency` (String!)
- `bidIncrementTable` (BidIncrementTable)
- `closingMethod` (ClosingMethod!)
- `closingTimeCountdown` (Int)
- `items` (ItemConnection)

### SaleItem
- `id` (ID!)
- `title` (String!)
- `description` (String)
- `status` (ItemStatus!) - UNPUBLISHED, PUBLISHED, OPEN, CLOSING, CLOSED
- `startingBid` (Int!)
- `reserve` (Int)
- `currentBid` (Int)
- `bidCount` (Int)
- `allowedBidTypes` ([BidType!])
- `dates` (ItemDates!)

### BidIncrementTable
- `rules` ([BidIncrementRule!]!)

### BidIncrementRule
- `lowRange` (Int!)
- `highRange` (Int!)
- `step` (Int!)

### ItemDates
- `openDate` (DateTime!)
- `closingStart` (DateTime!)
- `closingEnd` (DateTime!)

## Subscriptions

### saleActivity

Real-time subscription for sale-related events. Streams both `Sale` and `SaleItem` updates over WebSocket.

**Arguments:**
- `accountId` (String!) - Your account ID
- `saleId` (ID!) - Sale to subscribe to
- `itemIdFilter` (ItemIdsFilter) - Optional filter to only receive updates for specific items

**Returns:** `SaleActivity!` — a union type that can be either a `Sale` or `SaleItem`

**Union Type:**
```graphql
union SaleActivity = Sale | SaleItem
```

**ItemIdsFilter Input:**
```graphql
input ItemIdsFilter {
  itemIds: [ID!]
}
```

**Example (subscribe to all activity on a sale):**
```graphql
subscription {
  saleActivity(accountId: "ACCOUNT_ID", saleId: "sale_abc123") {
    ... on Sale {
      id
      title
      status
      closingTimeCountdown
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

**Example (subscribe to specific items only):**
```graphql
subscription {
  saleActivity(
    accountId: "ACCOUNT_ID"
    saleId: "sale_abc123"
    itemIdFilter: { itemIds: ["item_1", "item_2"] }
  ) {
    ... on Sale {
      id
      status
    }
    ... on SaleItem {
      id
      status
      currentBid
      totalBids
      leaderId
    }
  }
}
```

**WebSocket Connection:**

Endpoint: `wss://management.api.basta.app/query`
Protocol: `graphql-ws`

Authentication is via HTTP headers on the WebSocket upgrade request (same as regular API calls):
```
x-account-id: YOUR_ACCOUNT_ID
x-api-key: YOUR_API_KEY
```

**Key SaleItem fields available in subscription:**
- `id` (ID!) - Item ID
- `title` (String) - Item title
- `status` (ItemStatus!) - Current item status
- `currentBid` (Int) - Current bid amount in cents
- `currentMaxBid` (Int) - Current max bid amount (only set when leading bid is a max bid)
- `totalBids` (Int!) - Number of bids placed
- `leaderId` (String) - User ID of current leader
- `reserve` (Int) - Reserve price in cents
- `startingBid` (Int) - Starting bid in cents
- `dates` (ItemDates!) - Open, closing start, and closing end timestamps

## Enums

### SaleStatus
- UNPUBLISHED - Not yet published
- PUBLISHED - Published but not yet open
- OPEN - Currently accepting bids
- CLOSED - No longer accepting bids

### ItemStatus
- UNPUBLISHED
- PUBLISHED
- OPEN
- CLOSING - In closing countdown period
- CLOSED

### ClosingMethod
- OVERLAPPING - Items can close at different times

### BidType
- MAX - Maximum bid (proxy bidding)
- NORMAL - Direct bid at specific amount

## Fees

The Management API configures buyer/seller fees (e.g. Buyer's Premium, Platform Fee)
through an **account → sale → item** cascade — item overrides sale overrides account.

- **Account defaults:** `createAccountFee` / `updateAccountFee` / `deleteAccountFee`
  (permission `WRITE_ACCOUNT`) operate on `AccountFee` records.
- **Sale overrides:** `createSaleFee` / `updateSaleFee` / `deleteSaleFee`, plus
  `resetSaleFees` (revert a sale to account defaults). Return `FeeRule` (`WRITE_SALE`).
- **Item overrides:** `createSaleItemFee` / `updateSaleItemFee` / `deleteSaleItemFee`.
- **Reading effective fees:** `Sale.feeRules: [FeeRule!]!` (+ `Sale.hasDefaultSaleFees`)
  and `SaleItem.feeRules: [FeeRule!]!`; each `FeeRule` carries `source`
  (`ACCOUNT`/`SALE`/`ITEM`). Order lines expose `fees` (buyer) and `sellerFees`.

Each fee has `type` (`PERCENTAGE`/`AMOUNT`), `value` (`500` = 5%; `1000` = $10 in minor
units), `lowerLimit` (exclusive), optional `upperLteLimit` (inclusive), and
`calculationType` (`FLAT` or `PROGRESSIVE`).

```graphql
mutation {
  createSaleFee(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123", name: "Buyer's Premium",
    type: PERCENTAGE, value: 2000, lowerLimit: 0, calculationType: FLAT
  }) { id name value source }
}
```

## Registrations

Bidders are registered to a sale (and optionally to specific items), gated by registration
policies (CEL expressions) and `Sale.bidRestrictions`. Registration is **operator-driven
via this Management API** — the Client API only reads the bidder's own registrations.

- **Registrations:** `createSaleRegistration`, `acceptSaleRegistration`,
  `rejectSaleRegistration`, `deleteSaleRegistration` (all `WRITE_SALE`). Type is
  `ONLINE`/`PHONE`/`PADDLE`/`AGGREGATOR`; status `PENDING`→`ACCEPTED`/`REJECTED`.
- **Item registrations:** `createSaleItemRegistration` / `deleteSaleItemRegistration`.
- **Policies:** `createSaleRegistrationPolicy`, `updateSaleRegistrationPolicy`,
  `attachSaleRegistrationPolicies`, `detachSaleRegistrationPolicies` (no delete — detach
  instead). A policy is a CEL `rule` with `code`, `description`, `isDefault`.
- **Queries:** `saleRegistrations(filter: SaleRegistrationsQueryFilter, …)`,
  `saleRegistrationPolicies(…)`, plus `Sale.registrations` / `Sale.registrationPolicies`.

```graphql
mutation {
  createSaleRegistration(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123", userId: "user_123", type: ONLINE
  }) { id status }
}
```

> See `references/fees_and_registrations.md` for the full fee + registration reference
> (all types, inputs, enums, calculation semantics, and Client API read-side).

## Watchlist, Highlighted Items & Metafields

- **Watchlist** — read who has favourited a sale/item: `Sale.watchlist(input: SaleWatchlistInput)`
  and `SaleItem.watchlist(input: SaleItemWatchlistInput)` return paginated
  `*WatchlistConnection`s of entries (`userId`, `createdAt`). Bidders favourite via the
  Client API (`subscribeToSale` etc.).
- **Highlighted items** — `SaleItem.highlight: ItemHighlight { enabled, position }`;
  `Sale.highlighted: HighlightedSaleItemConnection!` lists them ordered by position. Set
  `highlight: ItemHighlightInput` on item create/update, and reorder atomically with
  `reorderHighlightedItems(input: ReorderHighlightedItemsInput { saleId, itemIds })`
  (`WRITE_SALE`).
- **Metafields** — arbitrary key/value data on Account/Sale/Item/SaleItem. Read via
  `metafields(input: {keys})` / `metafield(input: {key})`; write with
  `setMetafields(metafields: [SetMetafieldInput!]!)` (≤10 at a time) and
  `deleteMetafield(input: DeleteMetafieldInput)` (`WRITE_METAFIELDS`). Value types:
  single-line or rich text.

> See `references/watchlist_highlights_metafields.md` for the full reference across both APIs.

## Offers & Buy-Now (seller side)

The operator side of the buyer make-an-offer flow (buyers negotiate via the Client API's
`makeOffer`/`counterOffer`/`acceptCounter`/`withdrawOffer`). All amounts are minor currency
units with an ISO-4217 `currency` string.

**Configure & decide offers:**
- `setItemOfferConfig(input: SetItemOfferConfigInput!): ItemOfferConfig!` (`WRITE_ITEM`) —
  enable/disable offers on an item and set an **auto-accept threshold** and per-offer TTL.
  `input`: `itemId`, `enabled`, `autoAcceptAmount`/`autoAcceptCurrency` (+ `clearAutoAccept`),
  `offerTtlSeconds` (+ `clearOfferTtl`).
- `acceptOffer(offerId): Offer!` / `rejectOffer(offerId): Offer!` (`WRITE_ITEM`) — decide a
  pending offer as admin.
- `counterOffer(offerId, amount, currency, message): Offer!` — counter as the seller.
- Reads: `offer(offerId): Offer!`, `itemOffers(itemId, first, after, status): OffersConnection!`,
  `offers(filter: OffersFilter, …): OffersConnection!` (account-wide), `itemOfferConfig(itemId): ItemOfferConfig` (`READ_ITEM`).

The Management `Offer` adds seller-side fields over the client one: `buyerUserId`/`buyer:
UserInfo`, `item: ItemBanner`, `decidedByUserId`, `decidedByActor: OfferActor`
(`OFFER_ACTOR_ADMIN` / `OFFER_ACTOR_CONSIGNOR`).

**Buy-Now:**
- `setItemBuyNowConfig(input: SetItemBuyNowConfigInput!): SaleItem!` (`WRITE_SALE`) —
  enable/disable a fixed buy-now `price`/`currency` on a sale item.
- `buyItem(input: BuyItemInput!): SaleItem!` (`WRITE_SALE`) — **terminal**: buy an item
  outright on behalf of a buyer (`buyerUserId`, `expectedPrice`, `currency`). Closes the item,
  marks it sold, and creates a payments order. The acting admin is never the buyer.

## Dutch Auctions (descending-clock) & SaleV2

Operator side of Basta's Dutch (descending-clock) auction format. Sales are polymorphic via
`SaleV2` (English `Sale` or `DutchSale`). Buyers accept the clock via the Client API's
`placeDutchBid`.

- `createDutchSale(input: CreateDutchSaleInput!): DutchSale!` / `updateDutchSale(input: UpdateDutchSaleInput!): DutchSale!`
- `createDutchItemForSale(input: CreateDutchItemForSaleInput!): DutchSaleItem!` /
  `updateDutchSaleItem(input: UpdateDutchSaleItemInput!): DutchSaleItem!` — a Dutch lot carries
  `availableUnits` and a price-drop `schedule` (`startingAmount` + dated `drops`).
- `saleV2(id: ID!, saleIdType: SaleIDType): SaleV2!` / `salesV2(accountId, first, after, filter, …): SaleV2Connection!` —
  read sales of any format; use inline fragments (`... on DutchSale`).

See the Client API reference for the full Dutch lot/price/bid shapes.

## Consignments

A **consignment** groups items a consignor entrusts to the auction house, with its own fee
rules, consignor(s), and staff. All mutations require `WRITE_CONSIGNMENT` (reads `READ_CONSIGNMENT`).

**Records:**
- `createConsignment(input: CreateConsignmentInput!): Consignment!` — `input`: `name`,
  `description`, `externalId` (unique per account), `feeRules: [ConsignmentFeeRuleInput!]!`,
  `consignorUserIds: [String!]` (first = main consignor; Basta `User.id`s), and
  `consignmentStaffUserIds: [String!]` (first = lead; Ory Kratos identity ids, same space as
  `DashboardMember.userId`). *(`consignorUserId`/`idType` are deprecated single-consignor fields.)*
- `updateConsignment(input: UpdateConsignmentInput!): Consignment!` — **full replace**: a field
  left out is cleared.
- `deleteConsignment(consignmentId): Consignment!` — rejected while items are still linked.

**Item ↔ consignment:**
- `setItemConsignment(input: { itemId, consignmentId, reassign })` — `reassign: true` moves an
  already-linked item; default rejects it.
- `clearItemConsignment(itemId): Item!` — no-op if unlinked.

**Consignors & staff:**
- `addConsignors` / `removeConsignors` / `setMainConsignor` (auto-adds the user if needed).
- `addConsignmentStaff` / `removeConsignmentStaff` (removing the lead promotes a remaining
  member) / `setConsignmentStaffLead`.

**Reads:** `consignment(consignmentId)`, `consignmentByShortId(shortId)` (`shortId` format
`CN<YY><M><D><SUFFIX>`, unique per account), `consignments(…): ConsignmentsConnection!`,
`consignorItems(consignorUserId, …): ItemsConnection!`, plus the consignor social graph
(`consignorFollowers`, `userFollowing`, `consignorFollowerCount`).

- **Consignment:** `id`, `shortId`, `accountId`, `name`, `description`, `externalId`,
  `consignors: [Consignor!]!` (`{ userId, isMain, user }`), `staff: [ConsignmentStaff!]!`
  (`{ userId, isLead, name, email }`), `feeRules: [ConsignmentFeeRule!]!`, `charges(…)`,
  `created`/`modified`/`createdByUserId`/`modifiedByUserId`.

## Live-Sale Clerking (LIVE sale type)

Auctioneer/clerk operations for a running **LIVE** sale. All require `WRITE_SALE` and a valid
auctioneer session cookie; they act on the current lot.

- `passLiveItem(input: PassLiveItemInput!): SaleItem!` — pass the lot (to processing; raises
  the reserve if it was met). `input`: `saleId`, `itemId`, `transitionToUpcomingLot`.
- `sellLiveItem(input: SellLiveItemInput!): SaleItem!` — sell the lot (lowers the reserve if
  it was unmet).
- `sellLiveItemToBid(input: SellLiveItemToBidInput!): SellLiveItemToBidResult!` — sell to a
  **pinned bid id** (item must be in `ITEM_LIVE`). Returns a typed error union
  (`SellLiveItemToBidError { errorCode: BID_NOT_HIGHEST }`) when the pinned bid is no longer
  the leader, so the UI can recover without polling.
- `addLiveStreamToSale(input): LiveStream!` (idempotent) / `deleteLiveStreamFromSale(input): Boolean!`
  — attach/detach a live video stream.
