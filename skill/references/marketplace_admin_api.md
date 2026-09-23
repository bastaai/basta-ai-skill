# Marketplace Admin API Reference

The **Admin API** is the dashboard-facing GraphQL API of Basta's Marketplace (ecommerce)
engine. It manages the catalog (products, variants, options, collections, facets),
orders and their fulfillment/payment/refund lifecycle, customers, promotions, shipping
methods, tax, zones/countries, marketplace settings, and image uploads.

This is separate from the auction **Management API** (`management.api.basta.app`). Where
the auction Management API manages sales/items/bids, the Marketplace Admin API manages an
ecommerce storefront.

**Endpoint:** `https://marketplace.api.basta.app/admin/graphql`
**Playground:** `https://marketplace.api.basta.app/admin`
**API version:** `2026-02` (also an `unstable` channel in the playground picker)

## Authentication

Two authentication paths are tried in order. **In addition**, every query and mutation
takes an explicit `accountId: String!` argument that scopes the operation.

| Method | Headers / Cookie | Used by |
|--------|------------------|---------|
| **API key** | `x-account-id` + `x-api-key` (validated against the account service) | Server-to-server / integrations |
| **Kratos session** | `ory_kratos_session` cookie (validated against Ory Kratos; memberships fetched from the account service) | Dashboard UI |

Unauthenticated requests are rejected with `authentication required`.

```bash
curl -X POST https://marketplace.api.basta.app/admin/graphql \
  -H "Content-Type: application/json" \
  -H "x-account-id: <your_account_id>" \
  -H "x-api-key: <your_api_key>" \
  -d '{"query":"query($a:String!){ products(accountId:$a){ totalItems } }","variables":{"a":"<your_account_id>"}}'
```

## Key Concepts

- **`accountId` everywhere** — every operation requires `accountId` as an argument, even
  when an API key already identifies the account. Pass your account id to both.
- **Money** — integer **minor units** (cents). Net (`price`) vs. gross (`priceWithTax`).
- **Tax rates** — in the Admin API all rate fields are **decimals** (e.g. `0.24` for 24%):
  `TaxRate.rate`, `OrderLine.taxRate`, and `OrderTaxSummary.taxRate`. ⚠️ This differs from
  the **Shop API**, where `OrderLine.taxRate` is a **percentage** (e.g. `24.0`). Same field
  name, different convention per API — check the value scale when moving between them.
- **Handlers & `argsJson`** — Promotions (conditions/actions), shipping methods
  (checker/calculator/fulfillment), and collection filters are configured by a handler
  `type` code plus a JSON-encoded `argsJson` argument string.
- **Bulk + positional results** — many delete/create mutations are batch
  (`deleteProducts(ids)`) and return `[DeletionResponse!]!` aligned positionally to inputs.
- **Two-step image upload** — `createMarketplaceUploadUrl` → PUT bytes to the signed URL →
  `upsertMarketplaceImage`.

## Order State Machine

`Order.state` is a string. The lifecycle (from marketplace-core):

```
Draft / AddingItems            (cart being built)
   │
   ▼
ArrangingPayment
   │
   ▼
PaymentAuthorized
   │
   ▼
PaymentSettled                 (stock is deducted on entry; restored if later cancelled)
   │
   ├──► PartiallyShipped ──► Shipped
   │                          │
   │                          ▼
   ├──► PartiallyDelivered ──► Delivered
   │
   ▼
Cancelled                      (reachable from stock-deducted states; restores stock)

Modifying / ArrangingAdditionalPayment   (entered by modifyOrder on a placed order)
```

`active` is `true` while the order is a mutable cart (pre-placement) and `false` once
placed. Stock is deducted on the transition **into** `PaymentSettled` and restored if the
order is cancelled from any stock-deducted state.

## Queries (all take `accountId: String!`)

### Catalog
| Query | Extra args | Returns |
|-------|-----------|---------|
| `products` | `options: ProductListOptions` | `ProductList!` |
| `product` | `id: ID` **or** `slug: String` | `Product` |
| `productVariant` | `id: ID!` | `ProductVariant` |
| `productVariants` | `productId: ID!` | `ProductVariantList!` |
| `productOptionGroups` | — | `[ProductOptionGroup!]!` |
| `productOptionGroup` | `id: ID!` | `ProductOptionGroup` |
| `collections` | `options: CollectionListOptions` | `CollectionList!` |
| `collection` | `id: ID` **or** `slug: String` | `Collection` |
| `facets` | `options: FacetListOptions` | `FacetList!` (includes private facets) |
| `facet` | `id: ID!` | `Facet` |
| `facetValues` | `options: FacetValueListOptions` | `FacetValueList!` |
| `facetValue` | `id: ID!` | `FacetValue` |

### Orders & customers
| Query | Extra args | Returns |
|-------|-----------|---------|
| `orders` | `options: OrderListOptions` | `OrderList!` (active carts + placed orders) |
| `order` | `id: ID!` | `Order` |
| `customers` | `options: CustomerListOptions` | `CustomerList!` |
| `customer` | `id: ID!` | `Customer` |

### Commerce config
| Query | Extra args | Returns |
|-------|-----------|---------|
| `promotions` | `options: PaginationInput` | `PromotionList!` |
| `promotion` | `id: ID!` | `Promotion` |
| `shippingMethods` | — | `ShippingMethodList!` |
| `shippingMethod` | `id: ID!` | `ShippingMethod` |
| `shippingClasses` | — | `ShippingClassList!` (account-scoped, not paginated) |
| `shippingClass` | `id: ID!` | `ShippingClass` |
| `taxCategories` | — | `TaxCategoryList!` |
| `taxRates` | `taxCategoryId: ID` | `TaxRateList!` |
| `countries` | — | `[Country!]!` (incl. disabled) |
| `enabledCountries` | — | `[Country!]!` |
| `zones` | — | `ZoneList!` |
| `zone` | `id: ID!` | `Zone` |
| `marketplaceSettings` | — | `MarketplaceSettings!` |

**List options** (`ProductListOptions`, `OrderListOptions`, …) share a shape:
`skip`, `take`, `sort: <Entity>SortParameter`, `filter: <Entity>FilterParameter`,
`filterOperator: LogicalOperator`. Filters use typed operator inputs
(`StringOperators { eq, notEq, contains, in, regex, isNull }`,
`NumberOperators { eq, lt, lte, gt, gte, between, isNull }`, `DateOperators`,
`BooleanOperators`, `IDOperators`) and can be nested with `_and` / `_or`.

```graphql
query OpenOrders($a: String!) {
  orders(accountId: $a, options: {
    take: 50
    sort: { orderPlacedAt: DESC }
    filter: { active: { eq: false }, state: { in: ["PaymentSettled", "Shipped"] } }
    filterOperator: AND
  }) {
    totalItems
    items { id code state totalWithTax currencyCode customer { emailAddress } }
  }
}
```

## Mutations (all take `accountId: String!`)

### Products & variants
- `createProduct(input: CreateProductInput!): Product!` — created with no variants.
- `updateProduct(input: UpdateProductInput!): Product!`
- `deleteProduct(id: ID!): DeletionResponse!` / `deleteProducts(ids: [ID!]!): [DeletionResponse!]!`
- `createProductVariants(input: [CreateProductVariantInput!]!): [ProductVariant!]!` — bulk;
  variants of one product must use disjoint option-value combinations. Supports
  `stockOnHand`, `trackInventory`, `weightGrams`, `taxCategoryId`, `shippingClassId`, `bastaItemId`.
- `createProductVariantFromItem(input: CreateProductVariantFromItemInput!): ProductVariant!` —
  create a variant from an existing **Basta auction item**: `name`, `price` (the item's
  reserve) and `currency` are taken from the item's content. `input`: `productId: ID!`,
  `bastaItemId: ID!`, `sku: String!`, plus optional `stockOnHand`, `trackInventory`,
  `enabled`, `taxCategoryId`, `optionValueIds: [ID!]`, `weightGrams`, `customFields: JSON`,
  `shippingClassId`.
- `updateProductVariants(input: [UpdateProductVariantInput!]!): [ProductVariant!]!`
- `deleteProductVariant(id: ID!)` / `deleteProductVariants(ids: [ID!]!)`

### Option groups & options
- `createProductOptionGroup(input: CreateProductOptionGroupInput!): ProductOptionGroup!`
- `updateProductOptionGroup(input: UpdateProductOptionGroupInput!): ProductOptionGroup!`
- `addOptionGroupToProduct(productId: ID!, optionGroupId: ID!): Product!`
- `removeOptionGroupFromProduct(productId: ID!, optionGroupId: ID!): Product!`
- `createProductOption(input: CreateProductOptionInput!): ProductOption!`
- `updateProductOption(input: UpdateProductOptionInput!): ProductOption!`
- `deleteProductOption(id: ID!): DeletionResponse!`

### Collections
- `createCollection`, `updateCollection`, `deleteCollection`, `deleteCollections`
- `moveCollection(input: MoveCollectionInput!): Collection!` — reparent / reposition.
- `setCollectionProducts(collectionId: ID!, productIds: [ID!]!): Collection!` — replaces
  manual membership. Automatic membership uses `filters: [CollectionFilterInput]`
  (handler `type` + `argsJson`).

### Facets & facet values
- `createFacet`, `updateFacet`, `deleteFacet`, `deleteFacets`
- `createFacetValues(input: [CreateFacetValueInput!]!): [FacetValue!]!`
- `updateFacetValues(input: [UpdateFacetValueInput!]!): [FacetValue!]!`
- `deleteFacetValues(ids: [ID!]!): DeletionResponse!`

### Customers & addresses
- `createCustomer`, `updateCustomer`, `deleteCustomer`
- `createCustomerAddress(customerId: ID!, input: CreateAddressInput!): Address!`
- `updateCustomerAddress(customerId: ID!, input: UpdateAddressInput!): Address!`
- `deleteCustomerAddress(customerId: ID!, id: ID!): DeletionResponse!`

### Orders, payments, refunds, fulfillment
- `transitionOrderToState(id: ID!, state: String!): Order` — validated; applies side
  effects (stock deduction into `PaymentSettled`, restoration on `Cancelled`).
- `cancelOrder(input: CancelOrderInput!): Order!`
- `addPaymentToOrder(input: AddPaymentToOrderInput!): Order!` — provider-driven payment.
- `addManualPaymentToOrder(input: ManualPaymentInput!): Order!` — cash / bank transfer;
  omit `amount` to record a full payment of `totalWithTax`.
- `modifyOrder(input: ModifyOrderInput!): Order!` — change lines of a placed order
  (transitions through `Modifying` / `ArrangingAdditionalPayment`).
- `assignCartToCustomer(sessionId: String!, customerId: ID!): Order!` — migrate a guest
  cart to a customer.
- `setOrderShippingAddress` / `setOrderBillingAddress` (inline, by `orderId`)
- `setOrderShippingAddressFromUser` / `setOrderBillingAddressFromUser` (by `addressId`)
- `addNoteToOrder` / `updateOrderNote` / `deleteOrderNote` — admin or customer-visible notes.
- `settlePayment(id: ID!): Payment!` / `cancelPayment(id: ID!): Payment!`
- `refundOrder(input: RefundOrderInput!): Refund!` / `settleRefund(input: SettleRefundInput!): Refund!`
- `addFulfillmentToOrder(input: AddFulfillmentInput!): Fulfillment!` — group lines into a shipment.
- `transitionFulfillmentState(input: TransitionFulfillmentStateInput!): Fulfillment!` —
  e.g. `Pending` → `Shipped` → `Delivered`.

### Promotions, shipping, tax, zones, settings
- `createPromotion` / `updatePromotion` / `deletePromotion` — conditions/actions are
  handler `type` + `argsJson`; `couponCode` null = automatic.
- `createShippingMethod` / `updateShippingMethod` / `deleteShippingMethod` — `checkerType`,
  `calculatorType`, `fulfillmentHandler` (+ `*ArgsJson`), optional `zoneId`, and
  `allowedShippingClassIds` (the shipping classes this method carries; empty = accepts every
  class). `code` is immutable once set.
- `createShippingClass(input: CreateShippingClassInput!): ShippingClass!` /
  `updateShippingClass(input: UpdateShippingClassInput!): ShippingClass!` /
  `deleteShippingClass(id: ID!): DeletionResponse!` — a shipping class is a tenant-scoped
  category (`code` unique per account, `name`) assigned to products/variants; the shipping
  eligibility check filters out methods whose `allowedShippingClassIds` don't cover every
  line in the cart. Delete fails (`success: false`, with reference counts in `message`) while
  any product, variant, or shipping method still references it.
- `createTaxCategory` / `updateTaxCategory`; `createTaxRate` / `updateTaxRate`
  (`rate` as decimal, scoped to a `taxCategoryId` + `zoneId`).
- `enableCountries(countryCodes)` / `disableCountries(countryCodes)`
- `createZone` / `updateZone` / `deleteZone`; `addCountriesToZone` / `removeCountriesFromZone`
- `updateMarketplaceSettings(input: UpdateMarketplaceSettingsInput!): MarketplaceSettings!`
  — array fields replace the full set; includes `defaultTaxZoneId`, `defaultShippingZoneId`,
  `guestCheckoutEnabled`, `requireEmailVerification`.

### Image uploads (two-step)
```graphql
# Step 1 — get a signed S3 PUT URL
mutation Step1($a: String!) {
  createMarketplaceUploadUrl(
    accountId: $a, entityType: PRODUCT, entityId: "prod_1", contentType: "image/jpeg"
  ) { imageId signedUrl imageUrl headers { key value } expiresAt }
}
# Step 2 — PUT the bytes to signedUrl (with the returned headers), then attach:
mutation Step2($a: String!) {
  upsertMarketplaceImage(
    accountId: $a, entityType: PRODUCT, entityId: "prod_1", imageId: "img_1", imageOrder: 0
  ) { id url imageOrder }            # imageOrder 0 = featured (lowest displays first)
}
# Detach: deleteMarketplaceImage(accountId, entityType, entityId, imageId): Boolean!
```
`MarketplaceImageType` is `PRODUCT`, `PRODUCT_VARIANT`, or `COLLECTION`.

## Example: create a product with one variant

```graphql
mutation CreateCatalog($a: String!) {
  createProduct(accountId: $a, input: {
    name: "Field Notebook", slug: "field-notebook", description: "A5 dotted", enabled: true
  }) { id }
}

mutation AddVariant($a: String!) {
  createProductVariants(accountId: $a, input: [{
    productId: "prod_1"
    name: "Field Notebook — Black"
    sku: "FN-BLK"
    price: 1499                # 14.99
    currencyCode: "USD"
    stockOnHand: 200
    trackInventory: true
    enabled: true
  }]) { id sku price stockLevel }
}
```

## Offers (seller view — read-only)

Buyers negotiate a price on items connected to a Basta auction lot via the **Shop API**
(`makeOffer`, `counterOffer`, `acceptCounter`, `declineOffer` — see the Shop reference). The
Admin API exposes those offers **read-only**, scoped to a product variant's connected item:

```graphql
query VariantOffers($a: String!) {
  productVariant(accountId: $a, id: "var_123") {
    id
    offers(first: 20, status: OFFER_STATUS_PENDING) {
      edges { node {
        id itemId buyerUserId amount currency status awaitingParty
        decidedByUserId decidedByActor expiresAt
        counters { party amount currency message createdByUserId created }
      } }
      pageInfo { hasNextPage endCursor }
    }
  }
}
```

`ProductVariant.offers(first, after, status)` returns an `OffersConnection!`. Unlike the
buyer-scoped Shop view, the admin owns the account and sees **every** offer on the item. The
admin `Offer` type adds seller-side fields over the shop one: `accountId`, `buyerUserId`,
`decidedByUserId`, and `decidedByActor: OfferActor` (`OFFER_ACTOR_ADMIN` or
`OFFER_ACTOR_CONSIGNOR` — who accepted/rejected). Seller accept/reject/counter **actions are
not exposed in this GraphQL schema** — they are recorded here (via `decidedBy*`) but driven
from another surface. Amounts are minor-unit `Int` with a plain `currency: String!`; `Offer`
is the only cursor/Relay-paginated connection in the Admin API.

- **Offer:** `id`, `accountId`, `itemId`, `buyerUserId`, `amount`, `currency`,
  `status: OfferStatus!`, `message`, `awaitingParty: OfferParty`, `decidedByUserId`,
  `decidedByActor: OfferActor`, `counters: [OfferCounter!]!`, `created`, `modified`, `expiresAt`.
- **OfferCounter:** `id`, `party: OfferParty!`, `amount`, `currency`, `message`, `createdByUserId`, `created`.

## Selected types

- **Product / ProductVariant** — admin variants additionally expose `stockOnHand`,
  `trackInventory`, `enabled`, `taxCategoryId`, `weightGrams`, and a top-level `bastaItemId`
  (the auction-item link — a first-class field here, **not** under `customFields`), plus
  shipping-class fields: `shippingClassId`, `shippingClass`, and `effectiveShippingClass`
  (the variant's own class if set, otherwise the parent product's).
- **ShippingClass** — `id`, `code` (unique per account), `name`, `createdAt`, `updatedAt`.
  Assigned to products/variants and carried by shipping methods (`allowedShippingClassIds`).
- **Order** — same shape as the shop `Order` plus `userId`, `notes: [OrderNote!]!`, and
  `customer.externalUserId` (JWT external user id for dashboard routing). Filterable via
  `OrderListOptions`.
- **Promotion** — `enabled`, `startsAt`/`endsAt`, `couponCode`, `perCustomerUsageLimit`,
  `usageLimit`, `usageCount`, `priority`, `conditions`/`actions`.
- **ShippingMethod** — `code`, `checkerType`, `calculatorType`, `fulfillmentHandler`,
  `zoneId`/`zone`.
- **TaxCategory / TaxRate / Zone / Country** — tax & geography config.
- **Payment / Refund / Fulfillment / OrderNote** — order operations.
- **MarketplaceSettings** — store defaults, locales/currencies, default tax/shipping zones,
  `guestCheckoutEnabled`, `requireEmailVerification`, `customFields`.

## Enums

- **SortOrder:** `ASC`, `DESC` · **LogicalOperator:** `AND`, `OR`
- **StockLevel:** `IN_STOCK`, `OUT_OF_STOCK`, `LOW_STOCK`
- **AdjustmentType:** `PROMOTION`, `DISTRIBUTED_ORDER_PROMOTION`, `OTHER`
- **OrderType:** `Regular`, `Seller`, `Aggregate`
- **MarketplaceImageType:** `PRODUCT`, `PRODUCT_VARIANT`, `COLLECTION`
- **OfferStatus:** `OFFER_STATUS_PENDING`, `OFFER_STATUS_ACCEPTED`, `OFFER_STATUS_REJECTED`,
  `OFFER_STATUS_CANCELED`, `OFFER_STATUS_COUNTERED`, `OFFER_STATUS_EXPIRED`
- **OfferParty:** `BUYER`, `SELLER` · **OfferActor:** `OFFER_ACTOR_ADMIN`, `OFFER_ACTOR_CONSIGNOR`
- **CurrencyCode:** full ISO 4217 set · **Scalars:** `JSON`, `DateTime` (RFC 3339)

## Architecture note

The Shop and Admin GraphQL APIs are a BFF (backend-for-frontend) gateway that forwards to
the `marketplace-core` gRPC domain service, which owns PostgreSQL and publishes events to
Kafka via a transactional outbox (event types like `OrderPlaced`). Source lives in the
monorepo at `src/go/marketplace` (BFF) and `src/go/marketplace-core` (domain service).
