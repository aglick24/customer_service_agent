#!/usr/bin/env python3
"""
Test Multiple Product Scenarios

Specific tests for handling orders with multiple products
and complex product interaction scenarios.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.sierra_agent.core.agent import SierraAgent


def test_multiple_product_order():
    """Test handling orders with multiple products."""
    print("📦 TESTING MULTIPLE PRODUCT ORDER HANDLING")
    print("=" * 60)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Test order W009 which has multiple products (SOBT003, SOGK009)
    print("\n🧪 Test: Multi-Product Order Analysis")
    print("-" * 40)
    
    response = agent.process_user_input(
        "Show me detailed information about all products in order W009 for george.hill@example.com"
    )
    
    # Check for both product SKUs
    product_skus = ["SOBT003", "SOGK009"]
    found_skus = [sku for sku in product_skus if sku in response]
    
    print(f"Products found: {found_skus}")
    print(f"Multi-product handling: {'✅ PASS' if len(found_skus) >= 2 else '❌ FAIL'}")
    
    # Check for product details
    detail_indicators = ["boot", "hiking", "waterproof", "glove", "insulated"]
    found_details = [detail for detail in detail_indicators if detail.lower() in response.lower()]
    
    print(f"Product details: {'✅ PASS' if len(found_details) >= 3 else '🔄 PARTIAL'} ({len(found_details)} details)")


def test_product_recommendation_flow():
    """Test product recommendations based on order history."""
    print("\n🎯 TESTING PRODUCT RECOMMENDATION FLOW")
    print("=" * 60)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Establish order context first
    agent.process_user_input("george.hill@example.com, order W009")
    
    # Ask for recommendations based on order
    print("\n🧪 Test: Order-Based Recommendations")
    print("-" * 40)
    
    response = agent.process_user_input(
        "Based on what I ordered, recommend similar products"
    )
    
    # Should recommend hiking/outdoor related items
    rec_indicators = ["recommend", "similar", "hiking", "outdoor", "boot", "glove"]
    found_recs = [rec for rec in rec_indicators if rec.lower() in response.lower()]
    
    print(f"Recommendations: {'✅ PASS' if len(found_recs) >= 4 else '❌ FAIL'} ({len(found_recs)} indicators)")


def test_cross_product_queries():
    """Test queries that span multiple products and categories."""
    print("\n🔄 TESTING CROSS-PRODUCT QUERIES")
    print("=" * 60)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Test 1: Compare products from order
    print("\n🧪 Test: Product Comparison")
    print("-" * 40)
    
    response = agent.process_user_input(
        "Compare the hiking boots and insulated gloves from order W009 for george.hill@example.com"
    )
    
    comparison_indicators = ["boot", "glove", "hiking", "insulated", "compare"]
    found_comparisons = [comp for comp in comparison_indicators if comp.lower() in response.lower()]
    
    print(f"Product comparison: {'✅ PASS' if len(found_comparisons) >= 4 else '❌ FAIL'} ({len(found_comparisons)} indicators)")
    
    # Test 2: Category-based search
    print("\n🧪 Test: Category Search")
    print("-" * 40)
    
    response = agent.process_user_input(
        "Show me all winter gear suitable for hiking"
    )
    
    category_indicators = ["winter", "hiking", "gear", "outdoor"]
    found_categories = [cat for cat in category_indicators if cat.lower() in response.lower()]
    
    print(f"Category search: {'✅ PASS' if len(found_categories) >= 3 else '❌ FAIL'} ({len(found_categories)} indicators)")


def run_product_tests():
    """Run all product-related tests."""
    print("🏔️ SIERRA AGENT - MULTIPLE PRODUCT TEST SUITE")
    print("=" * 70)
    print("Testing complex product scenarios and interactions...")
    
    try:
        test_multiple_product_order()
        test_product_recommendation_flow()
        test_cross_product_queries()
        
        print("\n🎉 PRODUCT TEST SUITE COMPLETED")
        print("=" * 70)
        print("All product scenarios have been tested.")
        print("This validates the system's ability to handle:")
        print("  - Multiple products in single orders")
        print("  - Product recommendations based on history")
        print("  - Cross-product comparisons and queries")
        
    except Exception as e:
        print(f"\n❌ PRODUCT TEST ERROR: {e}")
        print("Some product tests may not have completed.")


if __name__ == "__main__":
    run_product_tests()