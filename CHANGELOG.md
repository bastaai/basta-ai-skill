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

## [Unreleased]

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

### Planned
- Ruby code examples
- TypeScript/JavaScript examples
- More webhook implementation examples
- Testing utilities
- Docker compose setup for local testing
- Additional tutorials and walkthroughs
