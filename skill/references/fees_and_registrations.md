# Fees & Registrations (Auction APIs)

Two auction feature sets that span the **Management API** (`management.api.basta.app`,
operator-side) and the **Client API** (`client.api.basta.app`, bidder-side):

1. **Fees** — configurable buyer/seller charges (e.g. buyer's premium, platform fee)
   resolved through an account → sale → item cascade and materialized onto order lines.
2. **Registrations** — bidders are registered to a sale (and optionally to individual
   items), gated by registration policies and bid restrictions.

> All money values are integers in the currency's **minor units** (e.g. cents).

---

## Part 1 — Fees

### The cascade

Fees are resolved through a three-level hierarchy; the most specific level wins:

```
ITEM overrides SALE overrides ACCOUNT
```

- **Account-level** defaults are `AccountFee` records (the account's standard fee schedule).
- **Sale-level** and **item-level** overrides are `FeeRule` records. A sale starts with a
  snapshot of the account defaults; customizing it replaces that snapshot for the sale.
- When you read **effective** fees (`Sale.feeRules`, `SaleItem.feeRules`), each returned
  `FeeRule` carries a `source` (`ACCOUNT` / `SALE` / `ITEM`) telling you which level it
  came from. `Sale.hasDefaultSaleFees` is `true` when the sale still uses the unmodified
  account-default snapshot.

### Calculation

Every fee has a `type` (`PERCENTAGE` / `AMOUNT` / `NOT_SET`), a `value`, a `lowerLimit`
(exclusive) and optional `upperLteLimit` (inclusive upper bound), and a
`calculationType` (`FLAT` / `PROGRESSIVE`):

- **`value`** is interpreted by `type`: `500` = **5%** for `PERCENTAGE`; `1000` = **$10.00**
  (minor units) for `AMOUNT`.
- **`FLAT`** — a single bracket (lower_limit, upper_lte_limit). For `PERCENTAGE` the rate
  applies to the entire amount; for `AMOUNT` the fixed charge applies once when the bracket
  matches.
- **`PROGRESSIVE`** — each bracket is evaluated independently. For `PERCENTAGE` the rate
  applies only to the slice of the amount within the bracket
  (`min(amount, upperLteLimit) - lowerLimit`). For `AMOUNT` the fixed charge applies once
  whenever `amount > lowerLimit`, regardless of `upperLteLimit`.

### Types

| Type | Where | Key fields |
|------|-------|-----------|
| `AccountFee` (Node) | Account defaults | `id`, `name`, `type: AccountFeeType!`, `value`, `lowerLimit`, `upperLteLimit`, `calculationType` |
| `FeeRule` (Node) | Effective sale/item fees | same as above + `type: FeeRuleType!` and `source: FeeRuleSource!` |
| `OrderLineFee` | Materialized on an order line | `id`, `description`, `name` *(deprecated → use `description`)*, `amount`, `isSystemDefined` |

Enums: `FeeCalculationType {FLAT, PROGRESSIVE}` · `AccountFeeType {NOT_SET, PERCENTAGE, AMOUNT}`
· `FeeRuleType {NOT_SET, PERCENTAGE, AMOUNT}` · `FeeRuleSource {ACCOUNT, SALE, ITEM}`.

Where fees surface elsewhere:
- `Sale.feeRules: [FeeRule!]!`, `Sale.hasDefaultSaleFees: Boolean!`
- `SaleItem.feeRules: [FeeRule!]!`
- `PaymentDetails.accountFees: [AccountFee!]!`
- `OrderLine.fees: [OrderLineFee!]!` (buyer fees, e.g. Buyer's Premium) and
  `OrderLine.sellerFees: [OrderLineFee!]!` (seller-paid, e.g. Platform Fee)
- Payment order-line inputs: `CreatePaymentOrderLineFeeInput { description, amount }`,
  `UpdateOrderLineFeeInput { description, amount }`

### Management API mutations (all require the relevant write permission)

**Account fees** (`WRITE_ACCOUNT`):
- `createAccountFee(accountId, input: CreateAccountFeeInput!): AccountFee!`
- `updateAccountFee(accountId, input: UpdateAccountFeeInput!): AccountFee!`
- `deleteAccountFee(accountId, input: DeleteAccountFeeInput!): ID!`

**Sale fees** (`WRITE_SALE`):
- `createSaleFee(accountId, input: CreateSaleFeeInput!): FeeRule!`
- `updateSaleFee(accountId, input: UpdateSaleFeeInput!): FeeRule!`
- `deleteSaleFee(accountId, input: DeleteSaleFeeInput!): ID!`
- `resetSaleFees(accountId, input: ResetSaleFeesInput!): [FeeRule!]!` — discard sale
  customizations and revert to the account defaults.

**Item fees** (`WRITE_SALE`):
- `createSaleItemFee(accountId, input: CreateSaleItemFeeInput!): FeeRule!`
- `updateSaleItemFee(accountId, input: UpdateSaleItemFeeInput!): FeeRule!`
- `deleteSaleItemFee(accountId, input: DeleteSaleItemFeeInput!): ID!`

Create/update inputs share: `name`, `type`, `value`, `lowerLimit`, `upperLteLimit?`,
`calculationType = FLAT`. Sale inputs add `saleId`; item inputs add `saleId` + `itemId`;
update inputs add `id`.

```graphql
mutation AddBuyersPremium {
  createSaleFee(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    name: "Buyer's Premium"
    type: PERCENTAGE
    value: 2000          # 20%
    lowerLimit: 0        # exclusive lower bound
    calculationType: FLAT
  }) {
    id name type value source calculationType
  }
}
```

### Client API (bidder-side, read-only)

- `Sale.feeRules: [FeeRule!]!` and `SaleItem.feeRules: [FeeRule!]!` expose the effective
  fees so a storefront can show buyer's premium etc. There are **no** fee mutations on the
  Client API.

---

## Part 2 — Registrations

Bidders must be registered to a sale to bid when the sale requires it. Registration is
**operator-driven**: it is created and managed through the **Management API**. The Client
API only exposes the authenticated bidder's own registrations (read-only) — there is **no
self-registration mutation** on the Client API.

### Concepts

- **Registration types** (`SaleRegistrationType`): `ONLINE` (web/app), `PHONE`,
  `PADDLE` (in-person), `AGGREGATOR` (third-party platform).
- **Status** (`SaleRegistrationStatus`): `PENDING` → `ACCEPTED` / `REJECTED`.
- **Bid restrictions** (`Sale.bidRestrictions: BidRestrictions!`):
  `acceptedRegistrationRequired` (must have an `ACCEPTED` registration to bid) and
  `phoneRegistrationOpen`.
- **Item registrations** — a `SaleRegistration` can have per-item `SaleItemRegistration`s
  (e.g. paddle/phone bidding scoped to specific lots). Creating an item registration
  creates the parent sale registration for that user+type if one doesn't exist.
- **Registration policies** — reusable rules expressed as **CEL** (Common Expression
  Language). A policy has `code`, `description`, `rule` (the CEL expression), and
  `isDefault` (auto-applied to all of the account's sales). Policies are attached to
  sales; evaluating them yields `SaleRegistrationPolicyResult { code, passed, description }`,
  surfaced on a registration's `policyResults`.
- **Pre-registration bids** — bids may exist without a registration id; in that case the
  bid's `registration` field is null.

### Management API

**Types:** `SaleRegistration` (Node — `userId`, `type`, `identifier`, `status`,
`rejectedReason`, `createdAt`, `userProfile`, `policyResults`, `preferredPhoneNumber`,
`alternativePhoneNumbers`, `itemRegistrations`), `SaleItemRegistration`,
`SaleRegistrationPolicy`, `SaleRegistrationPolicyResult`, and their `*Connection`/`*Edge`
pagination wrappers. Sort: `SaleRegistrationSortByField {CREATED_AT}`.

**Queries:**
- `saleRegistrations(accountId, first=20, after, filter: SaleRegistrationsQueryFilter, direction=BACKWARDS, sortByField=CREATED_AT): SaleRegistrationsConnection!` (`READ_SALE`)
- `saleRegistrationPolicies(accountId, first, after, …): SaleRegistrationPoliciesConnection!`
- On the `Sale` type: `registrations(filter: SaleRegistrationsForSaleFilter, …)`,
  `registrationPolicies(…)`, `bidRestrictions`.

Filters: `SaleRegistrationsQueryFilter { saleIds, userIds, types, statuses }` (account-wide
query), `SaleRegistrationsForSaleFilter { types, statuses, userId }` (per-sale),
`SaleItemRegistrationFilter { types, userId }`.

**Mutations** (all `WRITE_SALE`):
- `createSaleRegistration(accountId, input: CreateSaleRegistrationInput!): SaleRegistration!`
- `acceptSaleRegistration(accountId, input: AcceptSaleRegistrationInput!): SaleRegistration!`
- `rejectSaleRegistration(accountId, input: RejectSaleRegistrationInput!): SaleRegistration!` (carries `reason`)
- `deleteSaleRegistration(accountId, input: DeleteSaleRegistrationInput!): ID!`
- `createSaleItemRegistration(accountId, input: CreateSaleItemRegistrationInput!): SaleItemRegistration!`
- `deleteSaleItemRegistration(accountId, input: DeleteSaleItemRegistrationInput!): ID!`
- `createSaleRegistrationPolicy(accountId, input: CreateSaleRegistrationPolicyInput!): SaleRegistrationPolicy!`
- `updateSaleRegistrationPolicy(accountId, input: UpdateSaleRegistrationPolicyInput!): SaleRegistrationPolicy!`
- `attachSaleRegistrationPolicies(accountId, input: AttachSaleRegistrationPoliciesInput!): [SaleRegistrationPolicy!]!`
- `detachSaleRegistrationPolicies(accountId, input: DetachSaleRegistrationPoliciesInput!): [SaleRegistrationPolicy!]!`

(There is no `deleteSaleRegistrationPolicy` mutation — detach a policy from sales instead.)

`CreateSaleRegistrationInput`: `saleId`, `userId`, `type`, `identifier?`,
`status = PENDING`, and for `PHONE`: `preferredPhoneNumberId?`,
`alternativePhoneNumberIds?`. `CreateSaleItemRegistrationInput` adds `itemId`.

```graphql
# Register a user, then accept them
mutation Register {
  createSaleRegistration(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    userId: "user_123"
    type: ONLINE
  }) { id status }
}

mutation Accept {
  acceptSaleRegistration(accountId: "ACCOUNT_ID", input: {
    registrationId: "reg_456"
  }) { id status policyResults { code passed description } }
}
```

```graphql
# Define a CEL policy and attach it to a sale
mutation CreatePolicy {
  createSaleRegistrationPolicy(accountId: "ACCOUNT_ID", input: {
    code: "min-age"
    description: "Bidder must be 18+"
    rule: "user.age >= 18"          # CEL expression
    isDefault: false
  }) { id code }
}
mutation AttachPolicy {
  attachSaleRegistrationPolicies(accountId: "ACCOUNT_ID", input: {
    saleId: "sale_abc123"
    policyIds: ["pol_789"]
  }) { id code }
}
```

### Client API (bidder-side, read-only)

- `Sale.userSaleRegistrations: [UserSaleRegistration!]!` — the authenticated user's
  registration(s) for the sale.
- `Item.userItemRegistrations: [UserItemRegistration!]!` — their item-level registrations.
- `UserSaleRegistration`: `id`, `saleId`, `userId`, `registrationType`, `status`,
  `policyResults`, `preferredPhoneNumber`, `alternativePhoneNumbers`, `identifier`.
- `Sale.bidRestrictions: BidRestrictions!` — drives whether the UI must require an accepted
  registration before allowing a bid.
- Bid types carry `registration: UserSaleRegistration` (null for pre-registration bids).

There are no registration mutations on the Client API; to register a bidder, call the
Management API's `createSaleRegistration` server-side.
