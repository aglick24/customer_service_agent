#!/usr/bin/env python3
"""
Simple debug case to see the customer service prompt for the failing case.
"""

import os
import sys
sys.path.insert(0, 'src')

from sierra_agent.ai.llm_service import LLMService
from sierra_agent.core.planning_types import ConversationContext
from sierra_agent.core.adaptive_planning_service import AdaptivePlanningService
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator
from sierra_agent.data.data_provider import DataProvider

def debug_customer_service_response():
    """Debug just the customer service response with product data."""
    
    print("🔍 Debugging Customer Service Response")
    print("=" * 50)
    
    # Set up services
    data_provider = DataProvider()
    tool_orchestrator = ToolOrchestrator(data_provider)
    llm_service = LLMService()
    planning_service = AdaptivePlanningService(llm_service)
    
    session_id = "test_session"
    
    # Set up context with order info
    plan = planning_service.get_or_create_plan(session_id, "tell me about my order")
    plan.context.customer_email = "george.hill@example.com"
    plan.context.order_number = "#W009"
    
    # Get order info
    order_result = tool_orchestrator.execute_tool("get_order_status", 
                                                  email="george.hill@example.com", 
                                                  order_number="#W009")
    if order_result.success:
        plan.context.current_order = order_result.data
        print(f"✅ Order context set: {order_result.data.order_number}")
    
    # Now test the product info call that's failing
    print(f"\n🧪 Testing: tell me about the products i ordered")
    print("-" * 30)
    
    plan3, response3 = planning_service.process_user_input(
        session_id=session_id,
        user_input="tell me about the products i ordered",
        tool_orchestrator=tool_orchestrator
    )
    
    print(f"🤖 Final Response: {response3}")

if __name__ == "__main__":
    debug_customer_service_response()