#!/usr/bin/env python3
"""Test the conversation fixes"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.tools.tool_orchestrator import ToolOrchestrator
from sierra_agent.ai.llm_service import LLMService
from sierra_agent.core.adaptive_planning_service import AdaptivePlanningService

def test_tool_discovery():
    """Test that the LLM service can discover tools from orchestrator."""
    orchestrator = ToolOrchestrator()
    llm_service = LLMService()
    
    print("🔍 Testing Tool Discovery")
    print("=" * 30)
    
    # Test 1: Tool names match
    available_tools = orchestrator.get_available_tools()
    print(f"Available tools: {available_tools}")
    
    # Check that the correct tool names are present
    expected_tools = ["get_recommendations", "browse_catalog", "get_product_info"]
    for tool in expected_tools:
        if tool in available_tools:
            print(f"✅ {tool} found")
        else:
            print(f"❌ {tool} missing")
    
    # Test 2: Tool descriptions
    descriptions = orchestrator.get_tools_for_llm_planning()
    print(f"\n📝 Tool Descriptions:\n{descriptions}")
    
    # Test 3: Test recommendation tool with context
    print(f"\n🧪 Testing Recommendation Tool:")
    result = orchestrator.execute_tool(
        "get_recommendations",
        recommendation_type="complement_to",
        reference_skus=["SOBT003"],  # Hair brush from the order
        limit=2
    )
    
    if result.success:
        recs = result.data.get("recommendations", [])
        print(f"✅ Got {len(recs)} recommendations:")
        for rec in recs:
            print(f"   - {rec.product_name} ({rec.sku})")
    else:
        print(f"❌ Error: {result.error}")

def test_planning_integration():
    """Test that planning service works with new tools."""
    print(f"\n🎯 Testing Planning Integration")
    print("=" * 35)
    
    orchestrator = ToolOrchestrator()
    llm_service = LLMService()
    
    # Test the analyze_vague_request_and_suggest method
    suggestions = llm_service.analyze_vague_request_and_suggest(
        user_input="recommend me products based on my order",
        available_data={"current_order": {"products_ordered": ["SOBT003", "SOGK009"]}},
        tool_orchestrator=orchestrator
    )
    
    print(f"📋 Suggestions for product recommendations: {suggestions}")
    
    # Check that it suggests the right tool name
    if "get_recommendations" in suggestions:
        print("✅ Planning suggests correct tool name")
    else:
        print("❌ Planning doesn't suggest get_recommendations")
        print(f"   Got: {suggestions}")

if __name__ == "__main__":
    test_tool_discovery()
    test_planning_integration()
    print("\n🎉 Testing complete!")