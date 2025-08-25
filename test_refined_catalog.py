#!/usr/bin/env python3
"""Test the refined catalog tools"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.tools.tool_orchestrator import ToolOrchestrator

def test_catalog_tools():
    """Test the refined catalog tools."""
    orchestrator = ToolOrchestrator()
    
    print("🛍️ Testing Refined Catalog Tools")
    print("=" * 50)
    
    # Test 1: Browse catalog by category
    print("\n1️⃣ Browse Adventure Products:")
    result1 = orchestrator.execute_tool(
        "browse_catalog",
        category_filter="Adventure",
        limit=3
    )
    if result1.success:
        products = result1.data.get("products", [])
        print(f"   Found {len(products)} adventure products")
        for p in products[:2]:
            print(f"   - {p.product_name} ({p.sku})")
    else:
        print(f"   Error: {result1.error}")
    
    # Test 2: Get recommendations based on activity  
    print("\n2️⃣ Activity-Based Recommendations (tech gadgets):")
    result2 = orchestrator.execute_tool(
        "get_recommendations",
        recommendation_type="activity_based",
        activity_or_need="tech gadgets",
        limit=3
    )
    if result2.success:
        recs = result2.data.get("recommendations", [])
        print(f"   {result2.data.get('message', 'Got recommendations')}")
        for p in recs:
            print(f"   - {p.product_name} (Tags: {', '.join(p.tags)})")
    else:
        print(f"   Error: {result2.error}")
    
    # Test 3: Get product details
    print("\n3️⃣ Product Details (Backpack):")
    result3 = orchestrator.execute_tool(
        "get_product_info",
        product_identifier="SOBP001",
        include_recommendations=True
    )
    if result3.success:
        details = result3.data.get("details", {})
        print(f"   Product: {details.get('name')}")
        print(f"   Description: {details.get('description', '')[:80]}...")
        print(f"   Categories: {', '.join(details.get('categories', []))}")
        related = result3.data.get("related_products", [])
        if related:
            print(f"   Related: {len(related)} products")
    else:
        print(f"   Error: {result3.error}")
    
    # Test 4: Complementary recommendations
    print("\n4️⃣ Complementary to Backpack:")
    result4 = orchestrator.execute_tool(
        "get_recommendations", 
        recommendation_type="complement_to",
        reference_skus=["SOBP001"],
        limit=2
    )
    if result4.success:
        recs = result4.data.get("recommendations", [])
        print(f"   Found {len(recs)} complementary products")
        for p in recs:
            print(f"   - {p.product_name}")
    else:
        print(f"   Error: {result4.error}")
    
    print("\n✅ Catalog tools testing complete!")

def test_tool_descriptions():
    """Test that tool descriptions work with the planning system."""
    orchestrator = ToolOrchestrator()
    
    print("\n🤖 Tool Descriptions for LLM Planning:")
    print("=" * 45)
    descriptions = orchestrator.get_tools_for_llm_planning()
    print(descriptions)

if __name__ == "__main__":
    test_catalog_tools()
    test_tool_descriptions()