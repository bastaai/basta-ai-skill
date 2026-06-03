# Marketplace Shop API Reference

The **Shop API** is the public, storefront-facing GraphQL API of Basta's Marketplace
(ecommerce) engine. It powers product browsing, search, cart building, checkout, and
the logged-in customer's profile / order history.

This is separate from the auction **Client API** (`client.api.basta.app`). The
Marketplace engine is a full ecommerce stack (products, variants, carts, orders,
fulfillment, payments, promotions, tax, shipping) that can stand alone or mirror
auction items into purchasable variants (see `bastaItemId` below).

**Endpoint:** `https://marketplace.api.basta.app/shop/graphql`
**Playground:** `https://marketplace.api.basta.app/shop`
**API version:** `2026-02` (also an `unstable` channel is exposed in the playground picker)

## Authentication

The Shop API supports both guest and authenticated shoppers.

| Header | Required | Purpose |
|--------|----------|---------|
| `MARKETPLACE-ACCOUNT-ID` | **Yes, every request** | Identifies the storefront / channel (the Basta account). Without it the request is rejected with `missing MARKETPLACE-ACCOUNT-ID header`. |
| `Authorization: Bearer <JWT>` | No | A customer JWT (HS256). When present and valid, the request is authenticated and resolvers can read `user_id` / `account_id` claims. When absent, the request passes through anonymously (guest) and resolvers enforce auth where needed. |
| `x-marketplace-session` | No | Guest cart session token. Round-tripped for session continuity (see below). |

**Guest carts & session continuity.** A guest (no `Authorization` header) gets a cart
keyed by a session token. The server echoes the session back as a `marketplace_session`
cookie (`HttpOnly`, `Secure`, `SameSite=None`); browser clients automatically resend it.
Non-browser clients should read the session value and resend it via the
`x-marketplace-session` header on subsequent requests. On the first authenticated request
the guest cart is automatically merged into the customer's cart by marketplace-core.

```bash
curl -X POST https://marketplace.api.basta.app/shop/graphql \
  -H "Content-Type: application/json" \
  -H "MARKETPLACE-ACCOUNT-ID: <your_account_id>" \
  -H "Authorization: Bearer <customer_jwt>"   # optional, for logged-in shoppers
  -d '{"query":"{ activeOrder { id total } }"}'
```

## Key Concepts

- **Product / ProductVariant** — A `Product` is the merchandising parent; pricing, SKU,
  and stock live on its `ProductVariant`s. The storefront mostly transacts at the
  variant level (you add a `productVariantId` to the cart).
- **Order (cart vs. placed order)** — Carts and placed orders share the `Order` type and
  differ only by `state`/`active`. An `active` order in `AddingItems` / `ArrangingPayment`
  / `ArrangingAdditionalPayment` / `Modifying` is a working cart; once placed it moves
  through fulfillment states. Use `activeOrder` to fetch the caller's current cart.
- **Money** — all amounts are integers in the currency's **minor units** (e.g. cents).
  Every priced field comes in a net (`price`) and a gross (`priceWithTax`) variant.
- **Collections & Facets** — `Collection` is a hierarchical category tree used for
  navigation. `Facet`/`FacetValue` are taxonomy dimensions (Color, Material…) used for
  filtering and merchandising.
- **Custom fields** — `customFields` (a `JSON` scalar) appears on `Order`, `Customer`,
  `Address`, and `MarketplaceSettings` for account-specific data.
- **`bastaItemId`** — `ProductVariant.customFields.bastaItemId` links a marketplace variant
  back to a Basta auction item, when the variant mirrors a won/sold lot.

## Queries

### Catalog & browsing

| Query | Args | Returns | Notes |
|-------|------|---------|-------|
| `products` | `options: ProductListOptions` | `ProductList!` | Filter/sort/paginate. |
| `product` | `id: ID` **or** `slug: String` | `Product` | Provide exactly one. |
| `collections` | `options: CollectionListOptions` | `CollectionList!` | `topLevelOnly` restricts to roots. |
| `collection` | `id: ID` **or** `slug: String` | `Collection` | Provide exactly one. |
| `facets` | `options: FacetListOptions` | `FacetList!` | |
| `facet` | `id: ID!` | `Facet` | |
| `search` | `input: SearchInput!` | `SearchResult!` | Full-text + facet/collection/price filters; returns items plus facet/collection aggregations for filter UIs. |

```graphql
query Search {
  search(input: {
    term: "guitar"
    collectionSlug: "instruments"
    take: 24
    skip: 0
    sort: { price: ASC }
    facetValueIds: ["fv_brand_gibson", "fv_color_sunburst"]
    facetValueOperator: AND
    priceRangeFilter: { min: 50000, max: 500000 }   # 500.00 – 5000.00
  }) {
    totalItems
    items {
      productVariantId
      productVariantName
      sku
      slug
      inStock
      price { value min max }
      priceWithTax { value }
      currencyCode
      featuredImage { url }
    }
    facetValues { facetValue { id name } count }
    collections { collection { id name slug } count }
  }
}
```

### Cart, checkout & customer

| Query | Returns | Notes |
|-------|---------|-------|
| `activeOrder` | `Order` | The caller's current cart (customer cart or guest session cart). Null if none yet. |
| `order(id: ID!)` | `Order` | Restricted to orders owned by the caller. |
| `orderByCode(code: String!)` | `Order` | Look up by human-readable code; caller-owned only. |
| `nextOrderStates` | `[String!]!` | Legal next states for the active cart. |
| `eligibleShippingMethods` | `[ShippingMethod!]!` | Methods valid for the cart's contents + shipping address (prices resolved for this cart). |
| `activeShippingMethods` | `[ShippingMethod!]!` | Alias of `eligibleShippingMethods` in this implementation. |
| `me` | `CurrentUser` | The authenticated principal, or null for guests. |
| `activeCustomer` | `Customer` | Full profile incl. saved `addresses` and `orders`. Null for guests. |
| `availableCountries` | `[Country!]!` | Countries the storefront ships to / accepts addresses for. |
| `marketplaceSettings` | `MarketplaceSettings!` | Store name, locale/currency options, `guestCheckoutEnabled`. Fetch at boot. |

## Mutations

### Cart manipulation

| Mutation | Signature | Notes |
|----------|-----------|-------|
| `addItemToOrder` | `(productVariantId: ID!, quantity: Int!): Order!` | Creates a guest cart on first call if unauthenticated. |
| `addItemsToOrder` | `(inputs: [AddItemToOrderInput!]!): Order!` | Batch add, atomically. |
| `adjustOrderLine` | `(orderLineId: ID!, quantity: Int!): Order!` | Absolute new quantity; `0` removes the line. |
| `removeOrderLine` | `(orderLineId: ID!): Order!` | |
| `removeAllOrderLines` | `: Order!` | Empties the cart. |
| `applyCouponCode` | `(couponCode: String!): Order!` | Re-computes discounts. |
| `removeCouponCode` | `(couponCode: String!): Order` | |
| `setOrderCustomFields` | `(input: JSON!): Order!` | Replaces the cart's custom-fields payload. |

### Addresses, shipping & customer on the cart

| Mutation | Signature | Notes |
|----------|-----------|-------|
| `setOrderShippingAddress` | `(input: SetOrderAddressInput!): Order!` | Inline address (guest / one-off). `countryCode` required for tax & shipping. |
| `setOrderBillingAddress` | `(input: SetOrderAddressInput!): Order!` | |
| `setOrderShippingAddressFromUser` | `(addressId: ID!): Order!` | Reference a saved address (logged-in); stores only the reference, clears inline. |
| `setOrderBillingAddressFromUser` | `(addressId: ID!): Order!` | |
| `unsetOrderShippingAddress` | `: Order!` | Clears inline + saved-reference forms. |
| `unsetOrderBillingAddress` | `: Order!` | |
| `setOrderShippingMethod` | `(shippingMethodId: [ID!]!): Order!` | Treated as a single selection (first id used). |
| `setCustomerForOrder` | `(input: CreateCustomerInput!): Order!` | Attach guest customer details so a guest order can be placed. |
| `transitionOrderToState` | `(state: String!): Order` | Drive the cart through the state machine (e.g. `AddingItems` → `ArrangingPayment`). Errors if illegal; see `nextOrderStates`. |

### Customer profile & address book (authenticated)

| Mutation | Signature | Notes |
|----------|-----------|-------|
| `updateCustomer` | `(input: UpdateCustomerInput!): Customer!` | Null fields left unchanged. |
| `createCustomerAddress` | `(input: CreateAddressInput!): Address!` | Persists in user-service. |
| `updateCustomerAddress` | `(input: UpdateAddressInput!): Address!` | |
| `deleteCustomerAddress` | `(id: ID!): DeletionResponse!` | Existing orders that referenced it are unaffected (snapshot semantics). |

## Typical storefront flow

```graphql
# 1. Add a variant to the cart (guest cart auto-created)
mutation { addItemToOrder(productVariantId: "var_123", quantity: 2) { id totalQuantity } }

# 2. Set a shipping address (drives tax + eligible shipping methods)
mutation {
  setOrderShippingAddress(input: {
    streetLine1: "123 Main St", city: "Reykjavik", postalCode: "101", countryCode: "IS"
  }) { id }
}

# 3. Pick a shipping method
query { eligibleShippingMethods { id name priceWithTax } }
mutation { setOrderShippingMethod(shippingMethodId: ["sm_standard"]) { id shippingWithTax } }

# 4. Attach customer (guest) and move toward payment
mutation {
  setCustomerForOrder(input: {
    firstName: "Ada", lastName: "Lovelace", emailAddress: "ada@example.com"
  }) { id }
}
mutation { transitionOrderToState(state: "ArrangingPayment") { id state } }
# Payment capture is handled by the configured payment provider integration.
```

## Selected types

### Order (cart / placed order)
Money fields are minor units. Net vs. gross pairs: `total`/`totalWithTax`,
`subTotal`/`subTotalWithTax`, `shipping`/`shippingWithTax`.
Key fields: `id`, `code`, `state`, `active`, `currencyCode`, `total`, `totalWithTax`,
`subTotal`, `shipping`, `totalQuantity`, `couponCodes`, `lines: [OrderLine!]!`,
`shippingAddress`/`billingAddress: OrderAddress`, `shippingLines`, `payments`,
`fulfillments`, `discounts`, `taxSummary`, `customer: OrderCustomer`, `customFields`.

### OrderLine
`quantity`, `unitPrice`/`unitPriceWithTax`, `discountedUnitPrice…`, `proratedUnitPrice…`
(per-unit after distributing order-level discounts), `linePrice…`,
`taxRate` (a **percentage** in the Shop API, e.g. `24.0` for 24% — note the Admin API uses
a decimal `0.24` for the same field), `discounts: [Discount!]!`,
`productVariant: OrderLineProductVariant!`, `featuredImage`, `images`.

### Product / ProductVariant
- `Product`: `id`, `name`, `slug`, `description`, `variants`, `optionGroups`,
  `facetValues`, `collections`, `featuredImage`, `images`.
- `ProductVariant`: `id`, `productId`, `name`, `sku`, `price`/`priceWithTax`,
  `currencyCode`, `stockLevel` (`IN_STOCK`/`OUT_OF_STOCK`/`LOW_STOCK`), `options`,
  `facetValues`, `customFields { bastaItemId }`, `featuredImage`, `images`.

### Collection
`id`, `name`, `slug`, `description`, `position`, `parent`/`parentId`, `breadcrumbs`,
`children: [CollectionChild!]!`, `productVariants(options): ProductVariantList!`,
`featuredImage`, `images`.

### Customer / Address
- `Customer`: `id`, `firstName`, `lastName`, `emailAddress`, `phoneNumber`,
  `addresses: [Address!]`, `orders: OrderList`, `customFields`.
- `Address`: `id`, address lines, `country: Country`, `defaultShippingAddress`,
  `defaultBillingAddress`, `customFields`.

### MarketplaceSettings
`storeName`, `defaultCurrencyCode`, `availableCurrencyCodes`, `defaultLanguageCode`,
`availableLanguageCodes`, `guestCheckoutEnabled`, `customFields`.

## Enums

- **StockLevel:** `IN_STOCK`, `OUT_OF_STOCK`, `LOW_STOCK`
- **SortOrder:** `ASC`, `DESC`
- **LogicalOperator:** `AND`, `OR` (combining facet filters)
- **AdjustmentType:** `PROMOTION`, `DISTRIBUTED_ORDER_PROMOTION`, `OTHER`
- **OrderType:** `Regular`, `Seller`, `Aggregate` (storefront orders are currently `Regular`)
- **CurrencyCode:** full ISO 4217 set (USD, EUR, GBP, ISK, …); the subset available per
  storefront is configured per account.
- **LanguageCode:** IETF/CLDR language tags (en, en_US, is, de, …).

> Order state strings are plain `String` in the schema (e.g. `AddingItems`,
> `ArrangingPayment`, `PaymentSettled`, `Shipped`, `Delivered`, `Cancelled`). See the
> Marketplace Admin API reference for the full order state machine.
