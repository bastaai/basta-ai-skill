"""
Complete Example: Creating an Auction with Basta

This example demonstrates TWO workflows for creating auctions:
- Workflow A: Create reusable items, then add to sales
- Workflow B: Create items directly in sales

Requirements:
    pip install requests --break-system-packages
    
Environment variables:
    BASTA_ACCOUNT_ID - Your Basta account ID
    BASTA_API_KEY - Your Basta API key
"""

import os
import sys
from datetime import datetime, timedelta

# Add the scripts directory to path
sys.path.append('../skill/scripts')

from basta_client import BastaClient


def create_sample_auction_workflow_a():
    """
    Create auction using Workflow A: Reusable Items
    Items are created independently, then added to sales.
    """
    account_id = os.getenv('BASTA_ACCOUNT_ID')
    api_key = os.getenv('BASTA_API_KEY')
    
    if not account_id or not api_key:
        print("❌ Error: Set BASTA_ACCOUNT_ID and BASTA_API_KEY environment variables")
        return
    
    client = BastaClient(account_id, api_key)
    print("✅ Initialized Basta client")
    print("\n🔄 Using Workflow A: Reusable Items")
    
    # Step 1: Create standalone items (reusable)
    print("\n📝 Creating standalone items...")
    
    items_data = [
        {
            "title": "19th Century Oil Painting",
            "description": "Original oil on canvas by renowned artist",
            "starting_bid": 100000,  # $1,000
            "reserve": 500000        # $5,000
        },
        {
            "title": "Victorian Mahogany Desk",
            "description": "Antique mahogany writing desk with original hardware",
            "starting_bid": 50000,   # $500
            "reserve": 200000        # $2,000
        },
        {
            "title": "Ming Dynasty Vase",
            "description": "Authenticated Ming dynasty porcelain vase",
            "starting_bid": 1000000, # $10,000
            "reserve": 5000000       # $50,000
        }
    ]
    
    created_items = []
    for item_data in items_data:
        item = client.create_item(
            title=item_data["title"],
            description=item_data["description"],
            starting_bid=item_data["starting_bid"],
            reserve=item_data["reserve"]
        )
        created_items.append(item)
        print(f"✅ Created: {item['title']} (ID: {item['id']})")
    
    # Step 2: Create sale
    print("\n📦 Creating sale...")
    sale = client.create_sale(
        title="Estate Auction - Fine Art & Antiques",
        description="Curated collection of fine art and antique furniture",
        bid_increment_rules=[
            {"lowRange": 0, "highRange": 10000, "step": 100},
            {"lowRange": 10000, "highRange": 100000, "step": 500},
            {"lowRange": 100000, "highRange": 1000000, "step": 1000}
        ],
        closing_time_countdown=120000
    )
    
    sale_id = sale['id']
    print(f"✅ Created sale: {sale_id}")
    
    # Step 3: Add items to sale
    print("\n➕ Adding items to sale...")
    now = datetime.utcnow()
    open_date = (now + timedelta(days=1)).isoformat() + "Z"
    closing_date = (now + timedelta(days=7)).isoformat() + "Z"
    
    for item in created_items:
        client.add_item_to_sale(
            sale_id=sale_id,
            item_id=item['id'],
            open_date=open_date,
            closing_date=closing_date
        )
        print(f"✅ Added {item['title']} to sale")
    
    # Step 4: Publish
    print(f"\n🚀 Publishing sale...")
    published = client.publish_sale(sale_id)
    print(f"✅ Sale published - Status: {published['status']}")
    
    return {"sale_id": sale_id, "item_ids": [item['id'] for item in created_items]}


def create_sample_auction_workflow_b():
    """
    Create auction using Workflow B: Direct Creation
    Items are created directly in the sale.
    """
    account_id = os.getenv('BASTA_ACCOUNT_ID')
    api_key = os.getenv('BASTA_API_KEY')
    
    if not account_id or not api_key:
        print("❌ Error: Set BASTA_ACCOUNT_ID and BASTA_API_KEY environment variables")
        return
    
    client = BastaClient(account_id, api_key)
    print("✅ Initialized Basta client")
    print("\n🔄 Using Workflow B: Direct Creation")
    
    # Step 1: Create sale
    print("\n📦 Creating sale...")
    sale = client.create_sale(
        title="Estate Auction - Fine Art & Antiques",
        description="Curated collection of fine art and antique furniture",
        bid_increment_rules=[
            {"lowRange": 0, "highRange": 10000, "step": 100},
            {"lowRange": 10000, "highRange": 100000, "step": 500},
            {"lowRange": 100000, "highRange": 1000000, "step": 1000}
        ],
        closing_time_countdown=120000
    )
    
    sale_id = sale['id']
    print(f"✅ Created sale: {sale_id}")
    
    # Step 2: Create items directly in sale
    print("\n📝 Creating items in sale...")
    now = datetime.utcnow()
    open_date = (now + timedelta(days=1)).isoformat() + "Z"
    closing_date = (now + timedelta(days=7)).isoformat() + "Z"
    
    items_data = [
        {
            "title": "19th Century Oil Painting",
            "description": "Original oil on canvas by renowned artist",
            "starting_bid": 100000,
            "reserve": 500000
        },
        {
            "title": "Victorian Mahogany Desk",
            "description": "Antique mahogany writing desk with original hardware",
            "starting_bid": 50000,
            "reserve": 200000
        },
        {
            "title": "Ming Dynasty Vase",
            "description": "Authenticated Ming dynasty porcelain vase",
            "starting_bid": 1000000,
            "reserve": 5000000
        }
    ]
    
    created_items = []
    for item_data in items_data:
        item = client.create_item_for_sale(
            sale_id=sale_id,
            title=item_data["title"],
            description=item_data["description"],
            starting_bid=item_data["starting_bid"],
            reserve=item_data["reserve"],
            open_date=open_date,
            closing_date=closing_date
        )
        created_items.append(item)
        print(f"✅ Created: {item['title']}")
    
    # Step 3: Publish
    print(f"\n🚀 Publishing sale...")
    published = client.publish_sale(sale_id)
    print(f"✅ Sale published - Status: {published['status']}")
    
    return {"sale_id": sale_id, "item_ids": [item['id'] for item in created_items]}


def create_sample_auction():
    """Main function - chooses workflow based on USE_WORKFLOW_A env var."""
    use_workflow_a = os.getenv('USE_WORKFLOW_A', 'false').lower() == 'true'
    
    if use_workflow_a:
        result = create_sample_auction_workflow_a()
    else:
        result = create_sample_auction_workflow_b()
    
    if not result:
        return None
    
    # Continue with common steps
    account_id = os.getenv('BASTA_ACCOUNT_ID')
    api_key = os.getenv('BASTA_API_KEY')
    client = BastaClient(account_id, api_key)
    
    sale_id = result['sale_id']
    
    # Generate bidder tokens
    print(f"\n🎟️  Generating bidder tokens...")
    
    bidders = ["alice", "bob", "charlie"]
    tokens = {}
    
    for bidder_id in bidders:
        token_data = client.create_bidder_token(bidder_id, ttl_minutes=180)
        tokens[bidder_id] = token_data['token']
        print(f"✅ Token for {bidder_id}: {token_data['token'][:20]}...")
        print(f"   Expires: {token_data['expiration']}")
    
    # Retrieve and display sale summary
    print(f"\n📊 Sale Summary:")
    sale_details = client.get_sale(sale_id, include_items=True)
    
    print(f"   Sale ID: {sale_details['id']}")
    print(f"   Title: {sale_details['title']}")
    print(f"   Status: {sale_details['status']}")
    print(f"   Items: {len(sale_details['items']['edges'])}")
    
    print(f"\n📋 Items:")
    for edge in sale_details['items']['edges']:
        item = edge['node']
        print(f"   • {item['title']}")
        print(f"     ID: {item['id']}")
        print(f"     Status: {item['status']}")
    
    # Return info for testing
    return {
        'sale_id': sale_id,
        'item_ids': result['item_ids'],
        'tokens': tokens
    }


def place_test_bid(sale_id, item_id, bidder_token, amount=150000):
    """Place a test bid on an item."""
    
    account_id = os.getenv('BASTA_ACCOUNT_ID')
    api_key = os.getenv('BASTA_API_KEY')
    
    client = BastaClient(account_id, api_key)
    
    print(f"\n💰 Placing bid of ${amount/100:.2f}...")
    result = client.place_bid(
        sale_id=sale_id,
        item_id=item_id,
        amount=amount,
        bidder_token=bidder_token,
        bid_type="MAX"
    )
    
    if result['__typename'] == 'BidPlacedSuccess':
        print(f"✅ Bid successful!")
        print(f"   Amount: ${result['amount']/100:.2f}")
        print(f"   Status: {result['bidStatus']}")
        print(f"   Type: {result['bidType']}")
    else:
        print(f"❌ Bid failed: {result['error']}")
        print(f"   Code: {result['errorCode']}")
    
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Basta Auction Creation Example")
    print("=" * 60)
    print("\n📘 This example demonstrates TWO workflows:")
    print("   Workflow A (Reusable Items): create_item → add_item_to_sale")
    print("   Workflow B (Direct): create_item_for_sale")
    print("\n💡 Set USE_WORKFLOW_A=true to use Workflow A")
    print("   Otherwise Workflow B will be used (default)\n")
    
    # Create the auction
    auction_info = create_sample_auction()
    
    if auction_info:
        print("\n" + "=" * 60)
        print("✅ Auction created successfully!")
        print("=" * 60)
        
        print(f"\n📍 Next steps:")
        print(f"   1. Wait for the open_date to place bids")
        print(f"   2. Use the bidder tokens to authenticate bid requests")
        print(f"   3. Monitor webhooks for real-time updates")
        print(f"   4. Or subscribe via WebSocket for live data")
        
        print(f"\n🔗 GraphQL Playground:")
        print(f"   Management API: https://management.api.basta.app")
        print(f"   Client API: https://client.api.basta.app")
        
        # Uncomment to test bidding (requires auction to be OPEN)
        # if auction_info['item_ids']:
        #     place_test_bid(
        #         sale_id=auction_info['sale_id'],
        #         item_id=auction_info['item_ids'][0],
        #         bidder_token=auction_info['tokens']['alice'],
        #         amount=150000  # $1,500
        #     )
