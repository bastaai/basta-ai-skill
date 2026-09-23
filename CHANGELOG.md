# Changelog

All notable changes to the Basta Claude Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-30

### Added
- Initial release of Basta Claude Skill
- Complete Management API reference documentation
- Complete Client API reference documentation
- Comprehensive webhooks guide with implementation examples
- Detailed glossary of Basta terms and concepts
- Python client library (`basta_client.py`) with helper methods
- WebSocket subscription example (`websocket_example.py`)
- Support for both MaxBid (proxy) and NormalBid (direct) bidding
- Real-time GraphQL subscription workflows
- Webhook integration patterns (BidOnItem, SaleStatusChanged, ItemsStatusChanged)
- Step-by-step auction creation workflow
- Bidder token generation and management
- Error handling and best practices documentation

### Features
- 🎯 Complete API coverage for both Management and Client APIs
- 🔄 Real-time updates via WebSocket subscriptions
- 🪝 Full webhook integration support
- 🤖 Proxy bidding (MaxBid) and direct bidding (NormalBid)
- 📚 Comprehensive reference documentation
- 🐍 Ready-to-use Python scripts

## [1.1.0] - 2026-01-30

### Added
- Documentation for `createItem` mutation - create standalone, reusable items
- Documentation for `addItemToSale` mutation - add existing items to sales
- Two flexible workflow options: Reusable Items (Workflow A) vs Direct Creation (Workflow B)
- New Python client methods: `create_item()` and `add_item_to_sale()`
- Comprehensive workflow comparison in SKILL.md showing when to use each approach
- Example code demonstrating both workflows in `create_auction.py`

### Changed
- Corrected documentation to reflect that items CAN be created independently of sales
- Renamed `add_item()` to `create_item_for_sale()` for clarity (backward compatible)
- Updated all examples to show both workflow options
- Enhanced "Common Pitfalls" section with accurate information about item lifecycle
- Updated Implementation Guidelines with workflow selection guidance

### Deprecated
- `add_item()` method in Python client (use `create_item_for_sale()` for clarity)

## [1.6.0] - 2026-09-23

### Added
- Documentation for **auction make-an-offer / negotiation** — Client API buyer mutations `makeOffer`, `counterOffer`, `acceptCounter`, `withdrawOffer` and `offer` query; Management API seller side `setItemOfferConfig` (auto-accept threshold + TTL), `acceptOffer`, `rejectOffer`, `counterOffer`, reads `offer`/`itemOffers`/`offers`; types `Offer`/`OfferCounter`/`ItemOfferConfig`, enums `OfferStatus`/`OfferParty`/`OfferActor` (distinct from the Marketplace Shop API offers)
- Documentation for **Buy-Now** — `setItemBuyNowConfig` and terminal `buyItem` (Management API)
- Documentation for **Dutch (descending-clock) auctions & `SaleV2`** — Client API `placeDutchBid` (with `PRICE_MISMATCH` retry semantics), `saleV2`/`salesV2`, `saleActivityV2`, and the `DutchSale`/`DutchSaleItem`/`DutchPrice`/`DutchSchedule`/`DutchBidPlaced` cluster + `SaleFormat`/`DutchItemStatus`/`DutchBidErrorCode` enums; Management API `createDutchSale`/`updateDutchSale`/`createDutchItemForSale`/`updateDutchSaleItem`
- Documentation for **consignments** (Management API) — `createConsignment`/`updateConsignment`/`deleteConsignment`, `setItemConsignment`/`clearItemConsignment`, multi-consignor + staff ops (`addConsignors`, `setMainConsignor`, `addConsignmentStaff`, `setConsignmentStaffLead`, …), reads `consignment`/`consignmentByShortId`/`consignments`
- Documentation for **live-sale clerking** (Management API, `LIVE` sales) — `passLiveItem`, `sellLiveItem`, `sellLiveItemToBid` (typed `BID_NOT_HIGHEST` error), `addLiveStreamToSale`/`deleteLiveStreamFromSale`
- Documentation for **notification preferences** (Client API) — `setMyNotificationPreferences`, `NotificationEvent`/`NotificationChannel`
- New glossary section **Auction Formats, Offers & Consignments**; sections added to `client_api.md`, `management_api.md`, and `SKILL.md`

## [1.5.0] - 2026-09-22

### Added
- Documentation for **Marketplace offers / negotiation** (make-an-offer) — buyer Shop API mutations `makeOffer`, `counterOffer`, `acceptCounter`, `declineOffer`; buyer queries `myOffers`, `offer(id)`, and `ProductVariant.offers`; admin read-only `ProductVariant.offers` (seller view with `buyerUserId`/`decidedByUserId`/`decidedByActor`); types `Offer`, `OfferCounter`, `OffersConnection`/`OffersEdge`/`OffersPageInfo`, inputs `MakeOfferInput`/`CounterOfferInput`, enums `OfferStatus`, `OfferParty`, `OfferActor`
- Documentation for **`searchAsync`** — Typesense-index-backed variant search on the Shop API (eventually consistent; `filterBy`/`orderBy`, page-based pagination, facet counts/stats), `SearchAsyncType` enum, and the `search` vs. `searchAsync` trade-off
- Documentation for **shipping classes** on the Admin API — `ShippingClass`/`ShippingClassList`, queries `shippingClasses`/`shippingClass`, mutations `createShippingClass`/`updateShippingClass`/`deleteShippingClass`, variant `shippingClassId`/`shippingClass`/`effectiveShippingClass`, and a shipping method's `allowedShippingClassIds`
- Documentation for **`createProductVariantFromItem`** — mint a Marketplace variant from a Basta auction item (name/price/currency sourced from the item)

### Changed
- Corrected the Admin API note that `bastaItemId` lives under `customFields` — it is a top-level `ProductVariant` field on the Admin API (the Shop API keeps it under `customFields.bastaItemId`)
- Offer/searchAsync/shipping-class sections added to `marketplace_shop_api.md`, `marketplace_admin_api.md`, and `SKILL.md`

## [1.4.0] - 2026-06-03

### Added
- Documentation for **watchlist / favourites** — bidder mutations on the Client API (`subscribeToSale`, `subsribeToItem` *(sic)*, `subscribeToAccount`, `unsubscribe*`, `isUserSubscribed`) and operator read-side on the Management API (`Sale.watchlist`/`SaleItem.watchlist`, `SaleWatchlistEntry`/`SaleItemWatchlistEntry`)
- Documentation for **highlighted items** — `ItemHighlight`/`ItemHighlightInput`, `Sale.highlighted`/`SaleItem.highlight`, and `reorderHighlightedItems` (`ReorderHighlightedItemsInput`)
- Documentation for **metafields** — `Metafield`, `MetafieldValueType`, `MetafieldEntityType`, read (`metafields`/`metafield` on Account/Sale/Item/SaleItem) and write (`setMetafields`/`deleteMetafield`, `SetMetafieldInput`/`DeleteMetafieldInput`/`MetafieldInput`); Client API read-side wraps results in `MetafieldsConnection`
- New reference `references/watchlist_highlights_metafields.md` covering all three across the Management and Client APIs
- Sections added to `management_api.md`, `client_api.md`, `SKILL.md`, and the glossary
- Flagged the schema's misspelled Client API field name `subsribeToItem`

## [1.3.0] - 2026-06-03

### Added
- Documentation for **auction fees** — an account → sale → item fee cascade (item overrides sale overrides account) with `FLAT`/`PROGRESSIVE` calculation
  - Management API fee mutations: `createAccountFee`/`updateAccountFee`/`deleteAccountFee`, `createSaleFee`/`updateSaleFee`/`deleteSaleFee`/`resetSaleFees`, `createSaleItemFee`/`updateSaleItemFee`/`deleteSaleItemFee`
  - Types/enums: `AccountFee`, `FeeRule` (+`source`), `OrderLineFee`, `FeeCalculationType`, `AccountFeeType`, `FeeRuleType`, `FeeRuleSource`; `Sale.feeRules`/`hasDefaultSaleFees`, `SaleItem.feeRules`, `OrderLine.fees`/`sellerFees`
- Documentation for **sale & item registrations** — operator-driven registration with types (`ONLINE`/`PHONE`/`PADDLE`/`AGGREGATOR`), statuses (`PENDING`/`ACCEPTED`/`REJECTED`), CEL-based registration policies, and `Sale.bidRestrictions`
  - Management API mutations: `createSaleRegistration`, `acceptSaleRegistration`, `rejectSaleRegistration`, `deleteSaleRegistration`, `createSaleItemRegistration`/`deleteSaleItemRegistration`, and policy create/update/attach/detach
  - Client API read-side: `Sale.userSaleRegistrations`, `Item.userItemRegistrations`, `UserSaleRegistration`, `bidRestrictions`, and `registration` on bids (null for pre-registration bids)
- New reference `references/fees_and_registrations.md` covering both features across the Management and Client APIs
- Fee + registration sections added to `management_api.md`, `client_api.md`, `SKILL.md`, and the glossary

## [1.2.0] - 2026-06-03

### Added
- Documentation for the **Basta Marketplace** (ecommerce) engine — a second product surface alongside Auctions
- `references/marketplace_shop_api.md` — storefront Shop API reference (`marketplace.api.basta.app/shop/graphql`): products, variants, collections, facets, search, cart, checkout, customer/address management
- `references/marketplace_admin_api.md` — dashboard Admin API reference (`marketplace.api.basta.app/admin/graphql`): catalog, orders, fulfillment, payments/refunds, customers, promotions, shipping methods, tax, zones/countries, settings, two-step image upload
- Marketplace authentication: Shop uses `MARKETPLACE-ACCOUNT-ID` header + optional `Authorization: Bearer <JWT>` (guest carts via `x-marketplace-session` ⇄ `marketplace_session` cookie); Admin uses `x-account-id` + `x-api-key` or Kratos session, with every operation scoped by an `accountId` argument
- Order state machine documentation (AddingItems → ArrangingPayment → PaymentAuthorized → PaymentSettled → shipping/delivery states; Cancelled; Modifying/ArrangingAdditionalPayment)
- Marketplace terminology added to the glossary
- Note on the `bastaItemId` custom field linking marketplace variants to auction items

### Changed
- `SKILL.md` reframed around two product surfaces (Auctions + Marketplace) covering all four GraphQL APIs
- `README.md` updated with Marketplace endpoints, playgrounds, and reference docs

## [Unreleased]

### Planned
- Ruby code examples
- TypeScript/JavaScript examples
- More webhook implementation examples
- Testing utilities
- Docker compose setup for local testing
- Additional tutorials and walkthroughs
