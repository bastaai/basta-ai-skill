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

### createItemForSale

Add an item to an existing sale.

**Input:**
- `saleId` (ID!) - Parent sale ID
- `title` (String!) - Item title
- `description` (String) - Item description
- `startingBid` (Int!) - Starting bid in cents
- `reserve` (Int) - Reserve price in cents
- `allowedBidTypes` ([BidType!]) - Allowed bid types (e.g., MAX, LIVE)
- `openDate` (DateTime!) - When bidding opens
- `closingDate` (DateTime!) - When closing period begins

**Returns:** SaleItem object

**Example:**
```graphql
mutation AddItem {
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
