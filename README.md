# Basta Skill for Claude

A comprehensive Claude skill for integrating with [Basta's](https://basta.app) auction and ecommerce APIs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This skill enables Claude to work seamlessly with Basta's GraphQL APIs, helping you build auction platforms, manage sales, handle bidding, and implement real-time auction experiences.

## Features

- 🎯 **Complete API Coverage** - Both Management API and Client API
- 🔄 **Real-time Updates** - WebSocket subscriptions for live auction data
- 🪝 **Webhooks** - Comprehensive webhook integration guide
- 🤖 **Proxy Bidding** - Full support for MaxBid and NormalBid types
- 📚 **Detailed Documentation** - API references, glossary, and examples
- 🐍 **Python Scripts** - Ready-to-use client library and WebSocket examples

## Installation

1. Download the skill file: [`basta.skill`](releases/basta.skill)
2. Go to [Claude.ai](https://claude.ai)
3. Open Settings → Skills
4. Click "Upload Skill"
5. Select the downloaded `basta.skill` file

## Usage

Once installed, the skill automatically activates when you ask Claude about:
- Creating or managing auctions
- Working with Basta's APIs
- Handling bidding workflows
- Setting up real-time updates
- Implementing webhooks

### Example Requests

```
"Create a Basta auction for vintage guitars"
"Help me build a bidding interface using Basta's Client API"
"Show me how to subscribe to real-time auction updates"
"Generate a bidder token for user 123"
"Set up webhooks to notify me when bids are placed"
"Explain the difference between MaxBid and NormalBid"
```

## What's Included

### Core Skill (`skill/SKILL.md`)
Step-by-step workflows for:
- Creating auctions and items
- Publishing sales
- Generating bidder tokens
- Placing bids
- Real-time subscriptions
- Webhook integration

### Python Scripts (`skill/scripts/`)

**basta_client.py** - Full-featured API client
```python
from basta_client import BastaClient

client = BastaClient(account_id="...", api_key="...")
sale = client.create_sale(title="My Auction")
item = client.add_item(sale_id=sale["id"], title="Item 1", starting_bid=1000)
client.publish_sale(sale["id"])
```

**websocket_example.py** - Real-time subscription client
```python
from websocket_example import BastaSubscriptionClient

client = BastaSubscriptionClient(bidder_token="...")
await client.subscribe_to_item(sale_id="...", item_id="...", callback=handle_update)
```

### Reference Documentation (`skill/references/`)

- **management_api.md** - Complete Management API reference
- **client_api.md** - Complete Client API reference  
- **webhooks.md** - Comprehensive webhooks guide
- **glossary.md** - All Basta terminology and concepts

## Quick Start with Basta

### 1. Get Credentials

1. Sign up at [basta.app](https://basta.app)
2. Get your Account ID
3. Generate API Key in dashboard settings

### 2. Test in GraphQL Playground

- Management API: https://management.api.basta.app
- Client API: https://client.api.basta.app

### 3. Create Your First Auction

```python
from basta_client import BastaClient

# Initialize
client = BastaClient(account_id="your_id", api_key="your_key")

# Create auction
sale = client.create_sale(
    title="Estate Auction",
    description="Fine art and antiques"
)

# Add item
item = client.add_item(
    sale_id=sale["id"],
    title="Vintage Guitar",
    starting_bid=50000,  # $500
    reserve=200000       # $2000
)

# Publish
client.publish_sale(sale["id"])

# Generate bidder token
token = client.create_bidder_token("user_123", ttl_minutes=60)
```

## API Overview

### Management API
**Endpoint:** `https://management.api.basta.app`
- Server-side, authenticated operations
- Create/manage sales and items
- Generate bidder tokens
- Requires `x-account-id` and `x-api-key` headers

### Client API
**Endpoint:** `https://client.api.basta.app`
- Public-facing, client-side operations
- Browse auctions
- Place bids (with bidder token)
- Optional JWT authentication

### WebSocket Subscriptions
**Endpoint:** `wss://client.api.basta.app/query`
- Real-time auction updates
- Uses graphql-ws protocol
- Authenticated with bidder tokens

## Bid Types

### MaxBid (Proxy Bidding)
- User sets maximum amount willing to pay
- Auction engine automatically bids incrementally
- Winning amount may be lower than max
- Engine reacts to counter-bids up to max amount

### NormalBid (Direct Bidding)
- One-time bid at specified amount
- Must align with bid increment table
- Does not react to counter-bids

## Webhooks

Configure webhooks in Basta admin portal to receive real-time notifications:

- **BidOnItem** - Triggered when bids are placed
- **SaleStatusChanged** - Triggered when sales change status
- **ItemsStatusChanged** - Triggered when items change status

Each webhook includes an idempotency key to prevent duplicate processing.

See [`skill/references/webhooks.md`](skill/references/webhooks.md) for implementation guide with Python and Node.js examples.

## Documentation

- [Basta Official Docs](https://docs.basta.app)
- [Basta Developer Docs (GitHub)](https://github.com/bastaai/dev-docs)
- [API Overview](https://docs.basta.app/api-overview)
- [Glossary](https://docs.basta.app/glossary)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Basta Support:** [hi@basta.app](mailto:hi@basta.app)
- **Basta Documentation:** [docs.basta.app](https://docs.basta.app)
- **Issues:** [GitHub Issues](../../issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for use with [Claude](https://claude.ai) by Anthropic
- Integrates with [Basta](https://basta.app) auction platform
- Inspired by Basta's excellent [developer documentation](https://github.com/bastaai/dev-docs)

## Related

- [Claude Skills Documentation](https://support.claude.ai) (when available)
- [Basta Platform](https://basta.app)
- [Basta Developer Docs](https://github.com/bastaai/dev-docs)

---

Made with ❤️ for the Claude and Basta communities
