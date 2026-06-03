# Watchlist, Highlighted Items & Metafields (Auction APIs)

Three auction merchandising/personalisation features that span the **Management API**
(`management.api.basta.app`, operator-side) and the **Client API**
(`client.api.basta.app`, bidder-side).

---

## Part 1 — Watchlist / Favourites

Users can **favourite** (watchlist) an account, a sale, or an item. Bidders perform these
actions on the **Client API**; operators read the resulting **watchlist** (the set of
users who favourited) on the **Management API**.

### Client API (bidder actions)

| Mutation | Returns | Notes |
|----------|---------|-------|
| `subscribeToSale(saleId: String!)` | `UserSaleSubscription!` | Favourite a sale. |
| `unsubscribeFromSale(saleId: String!)` | `ID!` | |
| `subsribeToItem(saleId: String!, itemId: String!)` | `UserSaleItemSubscription!` | Favourite an item. ⚠️ The field name is literally `subsribeToItem` (misspelled in the schema) — use it verbatim. |
| `unsubscribeFromItem(saleId: String!, itemId: String!)` | `ID!` | |
| `subscribeToAccount(accountId: String!)` | `UserAccountSubscription!` | Follow a creator/account. |
| `unsubscribeFromAccount(accountId: String!)` | `ID!` | |

Read-side on the Client API:
- `Sale.isUserSubscribed: Boolean!` and `Item.isUserSubscribed: Boolean!` — whether the
  authenticated user has favourited that sale/item.

> "Subscribe", "favourite", and "watchlist" all refer to the same underlying relationship.

### Management API (read who favourited)

- `Sale.watchlist(input: SaleWatchlistInput): SaleWatchlistConnection!`
- `SaleItem.watchlist(input: SaleItemWatchlistInput): SaleItemWatchlistConnection!`

`SaleWatchlistInput` / `SaleItemWatchlistInput`: `first: Int = 20`, `after: String`,
`direction: PaginationDirection = BACKWARDS` (newest first). Each entry
(`SaleWatchlistEntry` / `SaleItemWatchlistEntry`, both implement `Node`) has `id`,
`userId`, and `createdAt`.

```graphql
query SaleWatchers {
  sale(accountId: "ACCOUNT_ID", id: "sale_abc123") {
    watchlist(input: { first: 50 }) {
      edges { node { userId createdAt } }
      pageInfo { hasNextPage endCursor }
    }
  }
}
```

---

## Part 2 — Highlighted Items

Highlighting features specific items on a sale page, ordered by `position` (lower numbers
appear first).

### Management API

- **Read:** `SaleItem.highlight: ItemHighlight` where
  `ItemHighlight { enabled: Boolean!, position: Int! }`. The sale exposes the ordered set
  via `Sale.highlighted: HighlightedSaleItemConnection!`
  (`edges { node: SaleItem!, position: Int! }`).
- **Set per item:** the item create/update inputs accept
  `highlight: ItemHighlightInput { enabled: Boolean!, position: Int! }` (e.g. when creating
  or updating a sale item).
- **Reorder:** `reorderHighlightedItems(accountId, input: ReorderHighlightedItemsInput!): HighlightedSaleItemConnection!`
  (`WRITE_SALE`). `ReorderHighlightedItemsInput { saleId, itemIds: [String!]! }` — `itemIds`
  must contain **exactly all currently-highlighted items** for the sale; positions are
  assigned sequentially from 0 in list order.

```graphql
mutation Reorder {
  reorderHighlightedItems(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    itemIds: ["item_3", "item_1", "item_2"]   # item_3 → position 0, etc.
  }) {
    edges { node { id title } position }
  }
}
```

### Client API (read-only)

- `Sale.highlighted: HighlightedItemConnection!` (`edges { node: Item!, position: Int! }`)
- `Item.highlight: ItemHighlight` (`{ enabled, position }`)

---

## Part 3 — Metafields

Metafields are arbitrary **key/value** custom data attached to an entity. They let you
store integration-specific or display data on accounts, sales, items, and sale items.

### Value & entity types

- `MetafieldValueType`: `METAFIELD_VALUE_TYPE_SINGLE_LINE_TEXT`, `METAFIELD_VALUE_TYPE_RICH_TEXT`
- `MetafieldEntityType` (Management API): `METAFIELD_ENTITY_TYPE_SALE`,
  `METAFIELD_ENTITY_TYPE_ITEM`, `METAFIELD_ENTITY_TYPE_SALE_ITEM`,
  `METAFIELD_ENTITY_TYPE_ACCOUNT`

### Management API

`Metafield { id, key, value, valueType, entityType }`.

- **Read** (available on Account, Sale, Item, and SaleItem types):
  - `metafields(input: GetMetafieldsInput!): [Metafield!]!` — `GetMetafieldsInput { keys: [String!] }`, returns at most 10.
  - `metafield(input: GetMetafieldInput!): Metafield` — `GetMetafieldInput { key: String! }`.
- **Write:**
  - `setMetafields(accountId: String!, metafields: [SetMetafieldInput!]!): [Metafield!]!`
    (`WRITE_METAFIELDS`) — create or update, **at most 10 at a time**.
    `SetMetafieldInput { entityType, entityId, key, value, valueType }`.
  - `deleteMetafield(accountId: String!, input: DeleteMetafieldInput!): Boolean!`
    (`WRITE_METAFIELDS`) — `DeleteMetafieldInput { entityType, entityId, key }`.
  - Item create/update inputs also accept inline `metafields: [MetafieldInput!]`
    (`MetafieldInput { key, value, valueType }`) to set metafields at creation time.

```graphql
mutation SetSaleMetafields {
  setMetafields(accountId: "ACCOUNT_ID", metafields: [
    {
      entityType: METAFIELD_ENTITY_TYPE_SALE
      entityId: "sale_abc123"
      key: "catalogue_pdf_url"
      value: "https://cdn.example.com/catalogue.pdf"
      valueType: METAFIELD_VALUE_TYPE_SINGLE_LINE_TEXT
    }
  ]) { id key value }
}
```

```graphql
query ReadSaleMetafields {
  sale(accountId: "ACCOUNT_ID", id: "sale_abc123") {
    metafields(input: { keys: ["catalogue_pdf_url", "sponsor"] }) { key value valueType }
  }
}
```

### Client API (read-only)

`Metafield { id, key, value, valueType }` (no `entityType` on the client). Available on
Sale and Item:
- `metafields(input: GetMetafieldsInput): [MetafieldsConnection!]!` — note the Client API
  wraps results in `MetafieldsConnection` (`edges`, `nodes`, `pageInfo`).
- `metafield(input: GetMetafieldInput!): Metafield`

```graphql
query {
  sale(saleId: "sale_abc123") {
    metafields(input: { keys: ["catalogue_pdf_url"] }) {
      nodes { key value valueType }
    }
  }
}
```
