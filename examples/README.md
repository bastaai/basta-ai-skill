# Basta Integration Examples

This directory contains practical examples for integrating with Basta's APIs.

## Examples

### 1. Create Auction (`create_auction.py`)

Complete workflow demonstrating:
- Creating a sale
- Adding multiple items
- Publishing the sale
- Generating bidder tokens
- Placing test bids

**Usage:**
```bash
export BASTA_ACCOUNT_ID="your_account_id"
export BASTA_API_KEY="your_api_key"
python create_auction.py
```

**Output:**
- Creates a sample estate auction
- Adds 3 items (painting, desk, vase)
- Publishes the sale
- Generates tokens for 3 test bidders

### 2. Webhook Handler (`webhook_handler.py`)

FastAPI-based webhook endpoint that:
- Receives Basta webhook events
- Handles all 3 event types
- Implements idempotency checking
- Provides health check endpoint

**Usage:**
```bash
pip install fastapi uvicorn --break-system-packages
uvicorn webhook_handler:app --reload
```

**Endpoints:**
- `POST /webhooks/basta` - Main webhook receiver
- `GET /health` - Health check
- `GET /` - Service info

**Testing:**
```bash
# Test with curl
curl -X POST http://localhost:8000/webhooks/basta \
  -H "Content-Type: application/json" \
  -d '{
    "idempotencyKey": "test-123",
    "actionType": "BidOnItem",
    "data": {
      "bidId": "bid-1",
      "itemId": "item-1",
      "userId": "user-1",
      "amount": 1000
    }
  }'
```

## Running Examples

### Prerequisites

```bash
# Install dependencies
pip install requests fastapi uvicorn --break-system-packages

# Set environment variables
export BASTA_ACCOUNT_ID="your_account_id"
export BASTA_API_KEY="your_api_key"
```

### Quick Start

1. **Create an auction:**
   ```bash
   python create_auction.py
   ```

2. **Start webhook handler:**
   ```bash
   uvicorn webhook_handler:app --reload
   ```

3. **Configure webhooks in Basta admin:**
   - Go to Basta admin portal
   - Navigate to Settings → Webhooks
   - Add your webhook URL (e.g., `https://your-domain.com/webhooks/basta`)

## Local Development

For local webhook testing, use [ngrok](https://ngrok.com):

```bash
# Start webhook handler
uvicorn webhook_handler:app --reload

# In another terminal, expose with ngrok
ngrok http 8000

# Use the ngrok URL in Basta admin
https://abc123.ngrok.io/webhooks/basta
```

## Code Structure

### create_auction.py
- `create_sample_auction()` - Main workflow
- `place_test_bid()` - Test bidding functionality

### webhook_handler.py
- `handle_basta_webhook()` - Main webhook endpoint
- `handle_bid_event()` - Process bid events
- `handle_sale_status_event()` - Process sale status changes
- `handle_items_status_event()` - Process item status changes

## Common Patterns

### Error Handling
```python
try:
    result = client.create_sale(...)
except Exception as e:
    logger.error(f"Failed to create sale: {e}")
    # Handle error
```

### Idempotency
```python
# Track processed events
processed_events = set()

if idempotency_key in processed_events:
    return {"status": "duplicate"}

# Process event...
processed_events.add(idempotency_key)
```

### Async Processing
```python
@app.post("/webhooks/basta")
async def handle_webhook(request: Request):
    # Acknowledge immediately
    payload = await request.json()
    await queue.enqueue(process_webhook, payload)
    return {"status": "received"}
```

## Next Steps

1. Review the [main skill documentation](../skill/SKILL.md)
2. Check the [API references](../skill/references/)
3. Test in the [GraphQL Playground](https://management.api.basta.app)
4. Join the Basta community for support

## Resources

- [Basta Documentation](https://docs.basta.app)
- [Basta Developer Docs](https://github.com/bastaai/dev-docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [ngrok Documentation](https://ngrok.com/docs)
