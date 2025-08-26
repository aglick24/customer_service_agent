#!/usr/bin/env python3
"""
Debug script to reproduce the planning issue where get_product_info is not being suggested
when user asks "tell me about the products I ordered".
"""

import os
import sys
sys.path.insert(0, 'src')

from sierra_agent.ai.llm_service import LLMService
from sierra_agent.core.planning_types import ConversationContext
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator
from sierra_agent.data.data_provider import DataProvider

def debug_planning_analysis():
    """Debug the LLM planning analysis for the specific failing case."""
    
    print("🔍 Debugging Planning Analysis")
    print("=" * 50)
    
    # Set up services
    llm_service = LLMService()
    data_provider = DataProvider()
    tool_orchestrator = ToolOrchestrator(data_provider)
    
    # Simulate the exact context from the conversation log
    plan_context = ConversationContext()
    plan_context.customer_email = "george.hill@example.com"
    plan_context.order_number = "#W009"
    
    # Simulate having order data from previous get_order_status call
    order_result = tool_orchestrator.execute_tool("get_order_status", 
                                                  email="george.hill@example.com", 
                                                  order_number="#W009")
    if order_result.success:
        plan_context.current_order = order_result.data
        print(f"✅ Order context set: {order_result.data.order_number} with products {order_result.data.products_ordered}")
    else:
        print(f"❌ Failed to get order: {order_result.error}")
        return
    
    # Test the exact user inputs from the conversation log
    test_cases = [
        "can you tell me about the products i ordered and make recommendations for me using them",
        "tell me about the products i ordered",
        "tell me about the products I ordered",
        "",  # Test empty message that caused "message didn't come through"
        "   ",  # Test whitespace-only message
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: '{user_input}'")
        print("-" * 40)
        
        try:
            # Get available tools
            available_tools = tool_orchestrator.get_available_tools()
            print(f"📋 Available tools: {available_tools}")
            
            # Run the LLM analysis that's failing
            suggested_actions = llm_service.analyze_vague_request_and_suggest(
                user_input=user_input,
                plan_context=plan_context,
                available_tools=available_tools,
                tool_orchestrator=tool_orchestrator
            )
            
            print(f"🤖 LLM suggested actions: {suggested_actions}")
            
            # Check what we expected vs what we got
            expected_actions = ["get_product_info"]  # Should suggest this for product details
            if "get_product_info" in suggested_actions:
                print("✅ CORRECT: get_product_info was suggested")
            else:
                print("❌ INCORRECT: get_product_info was NOT suggested")
                print(f"   Expected: {expected_actions}")
                print(f"   Got: {suggested_actions}")
                
        except Exception as e:
            print(f"💥 Error during analysis: {e}")
            import traceback
            traceback.print_exc()
    
    # Test the prompt that's being sent to the LLM
    print(f"\n📝 Debug Prompt Generation")
    print("-" * 40)
    
    user_input = "tell me about the products i ordered"
    available_tools = tool_orchestrator.get_available_tools()
    tools_description = tool_orchestrator.get_tools_for_llm_planning()
    
    prompt = llm_service.prompt_builder.build_vague_request_analysis_prompt(
        plan_context=plan_context,
        user_input=user_input,
        available_tools=available_tools,
        tools_description=tools_description
    )
    
    print("System prompt being sent to LLM:")
    print("=" * 30)
    print(prompt.system_prompt)
    print("=" * 30)
    print("User message being sent to LLM:")
    print(prompt.user_message)
    print("=" * 30)

if __name__ == "__main__":
    debug_planning_analysis()