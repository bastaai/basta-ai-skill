# Client API Reference

**Base URL:** `https://client.api.basta.app`

**Authentication:** Optional JWT bidder token for mutations
```json
{
  "Authorization": "Bearer BIDDER_TOKEN"
}
```

## Queries

### sale

Get public sale information (no auth required).

**Arguments:**
- `saleId` (ID!) - Sale ID

**Example:**
```graphql
query ViewSale {
  sale(saleId: "sale_abc123") {
    id
    title
    description
    status
    items {
      edges {
        node {
          id
          title
          description
          currentBid
          bidCount
          status
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

### item

Get individual item details.

**Arguments:**
- `saleId` (ID!) - Parent sale ID
- `itemId` (ID!) - Item ID

**Example:**
```graphql
query ViewItem {
  item(saleId: "sale_abc123", itemId: "item_xyz789") {
    id
    title
    description
    currentBid
    bidCount
    status
    myBidStatus {
      isWinning
      maxBid
      currentBid
    }
    dates {
      openDate
      closingStart
      closingEnd
    }
  }
}
```

## Mutations

### bidOnItem

Place a bid on an item. **Requires bidder token.**

**Input:**
- `saleId` (ID!) - Sale ID
- `itemId` (ID!) - Item ID
- `amount` (Int!) - Bid amount in cents
- `type` (BidType!) - MAX or NORMAL

**Returns:** Union type - BidPlacedSuccess or BidPlacedError

**Example:**
```graphql
# Headers: { "Authorization": "Bearer bidder_token_here" }
mutation PlaceBid {
  bidOnItem(
    saleId: "sale_abc123"
    itemId: "item_xyz789"
    amount: 1500000  # $15,000
    type: MAX
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

**Error Codes:**
- `BID_TOO_LOW` - Bid doesn't meet minimum increment
- `ITEM_CLOSED` - Item no longer accepting bids
- `INVALID_TOKEN` - Bidder token invalid or expired
- `UNAUTHORIZED` - Missing or invalid authorization

## Subscriptions

Connect to `wss://client.api.basta.app/query` using graphql-ws protocol.

### Authentication

Send bidder token in connection init:

```json
{
  "type": "connection_init",
  "payload": {
    "token": "BIDDER_TOKEN"
  }
}
```

### saleActivity (recommended)

Subscribe to real-time sale and item updates. Returns a union type `SaleActivity = Sale | Item` — each message is either a sale-level or item-level update. This is the preferred subscription; `itemChanged` is deprecated.

**Arguments:**
- `saleId` (ID!) - Sale ID
- `itemIdFilter` (ItemIdsFilter) - Optional filter for specific items

**Example (all activity):**
```graphql
subscription WatchSale {
  saleActivity(saleId: "sale_abc123") {
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

**Example (filtered to specific items):**
```graphql
subscription WatchItems {
  saleActivity(
    saleId: "sale_abc123"
    itemIdFilter: { itemIds: ["item_1", "item_2"] }
  ) {
    ... on Sale { id status }
    ... on Item { id status currentBid totalBids leaderId }
  }
}
```

Sale-level updates are always included regardless of the item filter.

## Type Definitions

### BidPlacedSuccess
- `amount` (Int!) - Bid amount placed
- `bidStatus` (String!) - "winning", "outbid", etc.
- `date` (DateTime!) - When bid was placed
- `bidType` (BidType!) - MAX or LIVE

### BidPlacedError
- `errorCode` (String!) - Error code
- `error` (String!) - Human-readable error message

### MyBidStatus
- `isWinning` (Boolean!) - Whether bidder is currently winning
- `maxBid` (Int) - Bidder's maximum bid (for MAX bids)
- `currentBid` (Int) - Current bid amount

### SaleActivity (Union)
`union SaleActivity = Sale | Item`

Returns either a `Sale` or `Item` object on each subscription event. Use inline fragments to handle both types.

### ItemIdsFilter (Input)
- `itemIds` ([ID!]) - List of item IDs to filter subscription events

## WebSocket Connection

**Protocol:** graphql-ws
**Ping/Pong:** Automatic keep-alive every 10 seconds

**Connection Flow:**

1. Connect to `wss://client.api.basta.app/query`

2. Send connection_init with token:
```json
{
  "type": "connection_init",
  "payload": {
    "token": "BIDDER_TOKEN"
  }
}
```

3. Subscribe to updates:
```json
{
  "id": "1",
  "type": "subscribe",
  "payload": {
    "query": "subscription { saleActivity(saleId: \"...\") { ... on Sale { id status } ... on Item { id status currentBid totalBids } } }"
  }
}
```

4. Receive updates:
```json
{
  "id": "1",
  "type": "next",
  "payload": {
    "data": {
      "saleActivity": { ... }
    }
  }
}
```

**JavaScript Example:**

```javascript
import { createClient } from 'graphql-ws';

const client = createClient({
  url: 'wss://client.api.basta.app/query',
  connectionParams: () => ({
    token: bidderToken
  })
});

client.subscribe({
  query: `
    subscription {
      saleActivity(saleId: "sale_abc") {
        ... on Sale {
          id
          status
        }
        ... on Item {
          id
          currentBid
          totalBids
          status
          leaderId
        }
      }
    }
  `
}, {
  next: (data) => console.log('Update:', data),
  error: (err) => console.error('Error:', err),
  complete: () => console.log('Complete')
});
```

## Fees & Registrations (read-only)

The Client API exposes auction fees and the bidder's own registrations for display; both
are **configured/managed on the Management API**, not here.

**Fees** — `Sale.feeRules: [FeeRule!]!` and `SaleItem.feeRules: [FeeRule!]!` return the
effective fees (e.g. Buyer's Premium). Each `FeeRule` has `name`, `type`
(`PERCENTAGE`/`AMOUNT`), `value` (`500` = 5%; `1000` = $10 minor units), `lowerLimit`,
`upperLteLimit`, and `calculationType` (`FLAT`/`PROGRESSIVE`).

**Registrations** — there is **no self-registration mutation**; a server registers bidders
via the Management API. The Client API reads:
- `Sale.userSaleRegistrations: [UserSaleRegistration!]!` — the authenticated user's sale
  registration(s): `registrationType` (`ONLINE`/`PHONE`/`PADDLE`/`AGGREGATOR`), `status`
  (`PENDING`/`ACCEPTED`/`REJECTED`), `policyResults`, `identifier`, phone numbers.
- `Item.userItemRegistrations: [UserItemRegistration!]!` — their item-level registrations.
- `Sale.bidRestrictions { acceptedRegistrationRequired, phoneRegistrationOpen }` — use this
  to decide whether the UI must require an accepted registration before allowing a bid.
- Bid results carry `registration: UserSaleRegistration` (null for pre-registration bids).

> See `references/fees_and_registrations.md` for the complete cross-API reference.

## Watchlist / Favourites, Highlights & Metafields

**Favourite (watchlist)** — bidders favourite sales, items, and accounts:
- `subscribeToSale(saleId): UserSaleSubscription!` / `unsubscribeFromSale(saleId): ID!`
- `subsribeToItem(saleId, itemId): UserSaleItemSubscription!` / `unsubscribeFromItem(saleId, itemId): ID!` — note the field name `subsribeToItem` is misspelled in the schema; use it verbatim.
- `subscribeToAccount(accountId): UserAccountSubscription!` / `unsubscribeFromAccount(accountId): ID!`
- `Sale.isUserSubscribed: Boolean!`, `Item.isUserSubscribed: Boolean!`

**Highlighted items** (read-only) — `Sale.highlighted: HighlightedItemConnection!`
(`edges { node: Item!, position }`) and `Item.highlight: ItemHighlight { enabled, position }`.

**Metafields** (read-only) — `Sale`/`Item` expose
`metafields(input: GetMetafieldsInput): [MetafieldsConnection!]!` and
`metafield(input: GetMetafieldInput!): Metafield`. `Metafield { id, key, value, valueType }`;
on the Client API results are wrapped in `MetafieldsConnection` (`edges`, `nodes`, `pageInfo`).

> See `references/watchlist_highlights_metafields.md` for the full cross-API reference.

## Best Practices

**Bidding:**
- Always check `__typename` to handle success/error responses
- Validate bid amounts client-side before submitting
- Show clear error messages for each error code
- Implement debouncing for rapid bid attempts

**Subscriptions:**
- Reconnect on connection loss
- Handle ping/pong timeouts
- Unsubscribe when components unmount
- Throttle UI updates for high-frequency events

**Performance:**
- Cache sale/item queries appropriately
- Use polling for less critical updates
- Batch multiple item queries when possible
- Implement optimistic UI updates for bids
