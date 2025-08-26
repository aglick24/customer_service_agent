#!/usr/bin/env python3
"""
Test script to verify the multiple products fix is working.
"""

import os
import sys
sys.path.insert(0, 'src')

from sierra_agent.tools.tool_orchestrator import ToolOrchestrator
from sierra_agent.data.data_provider import DataProvider

def test_multiple_products():
    """Test that get_product_info can handle comma-separated SKUs."""
    
    print("🧪 Testing Multiple Products Fix")
    print("=" * 50)
    
    # Set up services
    data_provider = DataProvider()
    tool_orchestrator = ToolOrchestrator(data_provider)
    
    # Test 1: Single product (existing functionality)
    print("Test 1: Single product")
    result1 = tool_orchestrator.execute_tool("get_product_info", product_identifier="SOBT003")
    print(f"✅ Single product result: Success={result1.success}")
    if result1.success and result1.data:
        print(f"   Product: {result1.data.get('product', {}).product_name if hasattr(result1.data.get('product', {}), 'product_name') else 'N/A'}")
    
    # Test 2: Multiple products (new functionality)  
    print("\nTest 2: Multiple products")
    result2 = tool_orchestrator.execute_tool("get_product_info", product_identifier="SOBT003,SOGK009")
    print(f"✅ Multiple products result: Success={result2.success}")
    if result2.success and result2.data:
        if 'products' in result2.data:
            print(f"   Found {len(result2.data['products'])} products:")
            for p in result2.data['products']:
                product = p.get('product', {})
                if hasattr(product, 'product_name'):
                    print(f"   - {product.product_name} ({product.sku})")
        else:
            print(f"   Data structure: {list(result2.data.keys())}")
    else:
        print(f"   Error: {result2.error}")

if __name__ == "__main__":
    test_multiple_products()