#!/usr/bin/env python3
"""
Debug script to print out prompts being sent to LLM to see why get_product_info isn't being called for multiple products.
"""

import os
import sys
sys.path.insert(0, 'src')

from sierra_agent.ai.llm_service import LLMService
from sierra_agent.core.planning_types import ConversationContext
from sierra_agent.core.adaptive_planning_service import AdaptivePlanningService
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator
from sierra_agent.data.data_provider import DataProvider

def debug_full_conversation_flow():
    """Debug the full conversation flow that's failing."""
    
    print("🔍 Debugging Full Conversation Flow")
    print("=" * 50)
    
    # Set up services
    data_provider = DataProvider()
    tool_orchestrator = ToolOrchestrator(data_provider)
    llm_service = LLMService()
    planning_service = AdaptivePlanningService(llm_service)
    
    session_id = "test_session"
    
    # Step 1: Simulate "tell me about my order"
    print("👤 User: tell me about my order")
    print("-" * 30)
    
    plan1, response1 = planning_service.process_user_input(
        session_id=session_id,
        user_input="tell me about my order",
        tool_orchestrator=tool_orchestrator
    )
    
    print(f"🤖 Response 1: {response1[:200]}...")
    print(f"📋 Plan status: {plan1.plan_id}, executed: {[s.tool_name for s in plan1.executed_steps]}")
    
    # Step 2: Simulate providing email and order number
    print(f"\n👤 User: #W009 and george.hill@example.com")
    print("-" * 30)
    
    plan2, response2 = planning_service.process_user_input(
        session_id=session_id,
        user_input="#W009 and george.hill@example.com",
        tool_orchestrator=tool_orchestrator
    )
    
    print(f"🤖 Response 2: {response2[:200]}...")
    print(f"📋 Plan status: {plan2.plan_id}, executed: {[s.tool_name for s in plan2.executed_steps]}")
    
    # Step 3: The failing case - "tell me about the products i ordered"
    print(f"\n👤 User: tell me about the products i ordered")
    print("-" * 30)
    
    # Add debug prints to see what's happening in planning
    print("🔍 DEBUGGING PLANNING PROCESS:")
    
    # Get the current plan
    current_plan = planning_service.active_plans.get(session_id)
    if current_plan:
        print(f"📋 Current plan context - Order: {current_plan.context.current_order.order_number if current_plan.context.current_order else 'None'}")
        print(f"📋 Available tools: {tool_orchestrator.get_available_tools()}")
        
        # Test the LLM planning directly
        print("\n🧠 Testing LLM Planning Analysis:")
        available_tools = tool_orchestrator.get_available_tools()
        suggested_actions = llm_service.analyze_vague_request_and_suggest(
            user_input="tell me about the products i ordered",
            plan_context=current_plan.context,
            available_tools=available_tools,
            tool_orchestrator=tool_orchestrator
        )
        print(f"🎯 LLM suggested actions: {suggested_actions}")
    
    plan3, response3 = planning_service.process_user_input(
        session_id=session_id,
        user_input="tell me about the products i ordered",
        tool_orchestrator=tool_orchestrator
    )
    
    print(f"🤖 Response 3: {response3}")
    print(f"📋 Plan status: {plan3.plan_id}, executed: {[s.tool_name for s in plan3.executed_steps]}")
    
    # Check what products are in the order
    if plan3.context.current_order:
        order = plan3.context.current_order
        print(f"🛒 Order products: {order.products_ordered}")
        print(f"❌ ISSUE: Should have called get_product_info for each: {', '.join(order.products_ordered)}")

if __name__ == "__main__":
    debug_full_conversation_flow()