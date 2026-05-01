#!/usr/bin/env python3
"""
Interactive Demo Auction Creator

This script creates a demo auction with sample items using your Basta credentials.
It will prompt you for your Account ID and API Key.
"""

import sys
from datetime import datetime, timedelta

# Add the scripts directory to path
sys.path.append('skill/scripts')

from basta_client import BastaClient


def create_demo_auction():
    """Create a demo auction with interactive credential input."""

    print("=" * 70)
    print("🎯 Basta Demo Auction Creator")
    print("=" * 70)
    print()

    # Get credentials interactively
    print("Please enter your Basta credentials:")
    print()
    account_id = input("Account ID: ").strip()
    api_key = input("API Key: ").strip()

    if not account_id or not api_key:
        print("\n❌ Error: Both Account ID and API Key are required")
        return

    print("\n" + "-" * 70)
    print("🚀 Creating demo auction...")
    print("-" * 70)

    try:
        # Initialize client
        client = BastaClient(account_id, api_key)
        print("\n✅ Connected to Basta API")

        # Step 1: Create sale
        print("\n📦 Creating sale...")
        sale = client.create_sale(
            title="Demo Auction - Collectibles & Antiques",
            description="A demonstration auction featuring vintage collectibles and antiques",
            bid_increment_rules=[
                {"lowRange": 0, "highRange": 10000, "step": 100},      # $0 - $100: $1 increments
                {"lowRange": 10000, "highRange": 100000, "step": 500}, # $100 - $1000: $5 increments
                {"lowRange": 100000, "highRange": 1000000, "step": 1000} # $1000+: $10 increments
            ],
            closing_time_countdown=120000  # 2 minutes countdown when bid placed near closing
        )

        sale_id = sale['id']
        print(f"✅ Created sale: {sale['title']}")
        print(f"   Sale ID: {sale_id}")

        # Step 2: Create items directly in sale
        print("\n📝 Adding items to sale...")

        # Calculate dates: open tomorrow, close in 7 days
        now = datetime.utcnow()
        open_date = (now + timedelta(days=1)).isoformat() + "Z"
        closing_date = (now + timedelta(days=7)).isoformat() + "Z"

        items_data = [
            {
                "title": "Vintage Rolex Submariner Watch",
                "description": "Classic 1970s Rolex Submariner in excellent condition. Fully serviced with original box and papers.",
                "starting_bid": 500000,  # $5,000
                "reserve": 800000        # $8,000
            },
            {
                "title": "First Edition Harry Potter Book",
                "description": "Rare first edition of Harry Potter and the Philosopher's Stone. Signed by J.K. Rowling.",
                "starting_bid": 100000,  # $1,000
                "reserve": 300000        # $3,000
            },
            {
                "title": "Mid-Century Modern Eames Lounge Chair",
                "description": "Authentic Herman Miller Eames Lounge Chair and Ottoman. Original leather, excellent condition.",
                "starting_bid": 300000,  # $3,000
                "reserve": 500000        # $5,000
            },
            {
                "title": "1952 Mickey Mantle Baseball Card",
                "description": "PSA-graded Mickey Mantle rookie card. Investment grade collectible.",
                "starting_bid": 200000,  # $2,000
                "reserve": 400000        # $4,000
            },
            {
                "title": "Vintage Gibson Les Paul Guitar",
                "description": "1959 Gibson Les Paul Standard in Sunburst. One of the most sought-after guitars.",
                "starting_bid": 1000000, # $10,000
                "reserve": 2000000       # $20,000
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
            print(f"   ✅ {item['title']}")
            print(f"      Starting bid: ${item_data['starting_bid']/100:,.2f}")

        # Step 3: Publish the sale
        print(f"\n🚀 Publishing sale...")
        published = client.publish_sale(sale_id)
        print(f"✅ Sale published successfully!")
        print(f"   Status: {published['status']}")

        # Step 4: Generate demo bidder tokens
        print(f"\n🎟️  Generating demo bidder tokens...")

        bidders = ["alice", "bob", "charlie"]
        tokens = {}

        for bidder_id in bidders:
            token_data = client.create_bidder_token(bidder_id, ttl_minutes=180)
            tokens[bidder_id] = token_data['token']
            print(f"   ✅ Token for '{bidder_id}': {token_data['token'][:30]}...")
            print(f"      Expires: {token_data['expiration']}")

        # Display final summary
        print("\n" + "=" * 70)
        print("🎉 Demo Auction Created Successfully!")
        print("=" * 70)

        print(f"\n📊 Auction Summary:")
        print(f"   Sale ID: {sale_id}")
        print(f"   Title: {sale['title']}")
        print(f"   Items: {len(created_items)}")
        print(f"   Status: {published['status']}")
        print(f"   Opens: {open_date}")
        print(f"   Closes: {closing_date}")

        print(f"\n📋 Items in Auction:")
        for i, item in enumerate(created_items, 1):
            print(f"   {i}. {item['title']}")
            print(f"      Item ID: {item['id']}")
            print(f"      Status: {item['status']}")

        print(f"\n🔗 API Endpoints:")
        print(f"   Management API: https://management.api.basta.app")
        print(f"   Client API: https://client.api.basta.app")
        print(f"   GraphQL Playground: Add '/query' to either endpoint")

        print(f"\n📍 Next Steps:")
        print(f"   1. Auction will open on {open_date}")
        print(f"   2. Use bidder tokens (alice/bob/charlie) to place test bids")
        print(f"   3. Test the auction using the Client API")
        print(f"   4. Monitor via GraphQL subscriptions for real-time updates")

        print(f"\n💡 Tip: Save your Sale ID ({sale_id}) to interact with this auction later!")

        # Save auction info to file
        with open('demo_auction_info.txt', 'w') as f:
            f.write(f"Demo Auction Information\n")
            f.write(f"========================\n\n")
            f.write(f"Sale ID: {sale_id}\n")
            f.write(f"Account ID: {account_id}\n")
            f.write(f"Created: {datetime.utcnow().isoformat()}Z\n\n")
            f.write(f"Bidder Tokens:\n")
            for bidder_id, token in tokens.items():
                f.write(f"  {bidder_id}: {token}\n")
            f.write(f"\nItem IDs:\n")
            for item in created_items:
                f.write(f"  {item['id']}: {item['title']}\n")

        print(f"\n💾 Auction details saved to: demo_auction_info.txt")
        print()

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"   Details: {error_data}")
            except:
                print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import requests  # Import here to check if available
    create_demo_auction()
