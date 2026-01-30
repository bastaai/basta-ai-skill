"""
Example Basta Webhook Handler using FastAPI

This example shows how to implement a webhook endpoint that receives
and processes Basta webhook events.

Requirements:
    pip install fastapi uvicorn --break-system-packages

Run:
    uvicorn webhook_handler:app --reload
"""

from fastapi import FastAPI, Request, HTTPException
from typing import Set, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Basta Webhook Handler")

# Track processed events to handle duplicates
processed_events: Set[str] = set()


@app.post("/webhooks/basta")
async def handle_basta_webhook(request: Request):
    """
    Main webhook endpoint for Basta events.
    
    Basta sends POST requests with this structure:
    {
        "idempotencyKey": "unique-uuid",
        "actionType": "BidOnItem|SaleStatusChanged|ItemsStatusChanged",
        "data": { ... }
    }
    """
    try:
        payload = await request.json()
        
        # Extract event details
        idempotency_key = payload.get('idempotencyKey')
        action_type = payload.get('actionType')
        data = payload.get('data', {})
        
        # Validate payload
        if not idempotency_key or not action_type:
            logger.error("Invalid payload: missing idempotencyKey or actionType")
            raise HTTPException(status_code=400, detail="Invalid payload")
        
        # Check for duplicate events
        if idempotency_key in processed_events:
            logger.info(f"Duplicate event ignored: {idempotency_key}")
            return {"status": "duplicate", "message": "Event already processed"}
        
        # Route event to appropriate handler
        logger.info(f"Processing {action_type} event: {idempotency_key}")
        
        if action_type == "BidOnItem":
            await handle_bid_event(data)
        elif action_type == "SaleStatusChanged":
            await handle_sale_status_event(data)
        elif action_type == "ItemsStatusChanged":
            await handle_items_status_event(data)
        else:
            logger.warning(f"Unknown event type: {action_type}")
        
        # Mark as processed
        processed_events.add(idempotency_key)
        
        return {"status": "ok", "eventId": idempotency_key}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_bid_event(data: Dict[str, Any]):
    """
    Handle BidOnItem webhook events.
    
    Data includes:
    - bidId, saleId, itemId, userId
    - amount, maxAmount, bidType
    - saleState (newLeader, prevLeader, currentBid, currentMaxBid)
    - reactiveBids (array of reactive bids)
    """
    bid_id = data.get('bidId')
    item_id = data.get('itemId')
    user_id = data.get('userId')
    amount = data.get('amount')
    sale_state = data.get('saleState', {})
    
    logger.info(f"Bid placed: {amount} cents on item {item_id} by user {user_id}")
    
    # Example actions:
    # - Send email notification to bidder
    # - Send "you've been outbid" notification to previous leader
    # - Update real-time dashboard
    # - Log to analytics
    
    new_leader = sale_state.get('newLeader')
    prev_leader = sale_state.get('prevLeader')
    
    if prev_leader and prev_leader != new_leader:
        logger.info(f"User {prev_leader} was outbid by {new_leader}")
        # await send_outbid_notification(prev_leader, item_id)
    
    # Handle reactive bids
    reactive_bids = data.get('reactiveBids', [])
    if reactive_bids:
        logger.info(f"Reactive bids placed: {len(reactive_bids)}")


async def handle_sale_status_event(data: Dict[str, Any]):
    """
    Handle SaleStatusChanged webhook events.
    
    Data includes:
    - saleId
    - saleStatus (UNPUBLISHED, PUBLISHED, OPEN, CLOSED)
    """
    sale_id = data.get('saleId')
    status = data.get('saleStatus')
    
    logger.info(f"Sale {sale_id} changed to status: {status}")
    
    # Example actions based on status:
    if status == "OPEN":
        logger.info(f"Sale {sale_id} is now accepting bids")
        # await send_auction_started_notifications(sale_id)
        # await update_marketing_campaigns(sale_id, active=True)
    
    elif status == "CLOSED":
        logger.info(f"Sale {sale_id} has closed")
        # await process_winning_bids(sale_id)
        # await generate_invoices(sale_id)
        # await send_closing_notifications(sale_id)


async def handle_items_status_event(data: Dict[str, Any]):
    """
    Handle ItemsStatusChanged webhook events.
    
    Data includes:
    - saleId
    - itemStatusChanges (array)
        - itemId
        - itemStatus (UNPUBLISHED, PUBLISHED, OPEN, CLOSING, CLOSED)
        - saleState (newLeader, prevLeader, currentBid, currentMaxBid)
    """
    sale_id = data.get('saleId')
    changes = data.get('itemStatusChanges', [])
    
    logger.info(f"Status changed for {len(changes)} items in sale {sale_id}")
    
    for change in changes:
        item_id = change.get('itemId')
        status = change.get('itemStatus')
        sale_state = change.get('saleState', {})
        
        logger.info(f"Item {item_id} -> {status}")
        
        # Example actions based on status:
        if status == "CLOSING":
            logger.info(f"Item {item_id} entering closing period")
            # await send_last_chance_notifications(item_id)
        
        elif status == "CLOSED":
            winner = sale_state.get('newLeader')
            winning_bid = sale_state.get('currentBid')
            logger.info(f"Item {item_id} closed. Winner: {winner}, Bid: {winning_bid}")
            # await process_item_sale(item_id, winner, winning_bid)
            # await send_winner_notification(item_id, winner)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "events_processed": len(processed_events)
    }


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "service": "Basta Webhook Handler",
        "endpoints": {
            "webhooks": "/webhooks/basta",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
