#!/usr/bin/env python3
"""Debug why planner avoids multi-step product info calls"""

from src.sierra_agent.core.agent import SierraAgent

def debug_planner():
    print("🔍 DEBUGGING PLANNER MULTI-STEP ISSUE")
    print("=" * 50)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Set up order context with multiple products
    print("\n1. Setting up order context...")
    order_response = agent.process_user_input("george.hill@example.com, #W009 show my order")
    print("Order context established ✓")
    
    # Ask for product details - should trigger multiple get_product_info calls
    print("\n2. Asking about products (should do: get_product_info for SOBT003, get_product_info for SOGK009, then get_recommendations)...")
    product_response = agent.process_user_input("tell me about the products I ordered and recommend similar items")
    
    print(f"\nResponse preview: {product_response[:300]}...")
    
    # Check if it actually got product details
    if "SOBT003" in product_response or "SOGK009" in product_response:
        print("\n✅ SUCCESS: Product details included")
    else:
        print("\n❌ FAILED: No product details")
    
    if "recommend" in product_response.lower():
        print("✅ SUCCESS: Recommendations included")
    else:
        print("❌ FAILED: No recommendations")

if __name__ == "__main__":
    debug_planner()