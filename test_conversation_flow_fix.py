#!/usr/bin/env python3
"""Test the conversation flow fixes"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.core.adaptive_planning_service import AdaptivePlanningService
from sierra_agent.ai.llm_service import LLMService
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator
from sierra_agent.data.data_types import Order

def test_context_aware_planning():
    """Test that the planning system can handle context-based requests."""
    
    print("🧪 Testing Context-Aware Planning")
    print("=" * 40)
    
    # Set up services
    llm_service = LLMService()
    planning_service = AdaptivePlanningService(llm_service)
    tool_orchestrator = ToolOrchestrator()
    
    # Create a session with order context
    session_id = "test_session_123"
    
    # Simulate order lookup - this adds order to context
    order_input = "My order is george.hill@example.com #W009"
    plan1, response1 = planning_service.process_user_input(session_id, order_input, tool_orchestrator)
    print(f"1️⃣ Order lookup response: {response1[:100]}...")
    
    # Check if order context was captured
    has_order = plan1.context.current_order is not None
    print(f"   Order context captured: {'✅' if has_order else '❌'}")
    
    if has_order:
        print(f"   Order SKUs: {getattr(plan1.context.current_order, 'products_ordered', [])}")
    
    # Now test context-based requests
    product_requests = [
        "tell me about the products i ordered",
        "can you tell me about the products from my order", 
        "what are the products i bought"
    ]
    
    for i, request in enumerate(product_requests, 2):
        print(f"\n{i}️⃣ Testing: '{request}'")
        plan, response = planning_service.process_user_input(session_id, request, tool_orchestrator)
        
        # Check if it understood and took action
        if "not sure how to help" in response.lower():
            print("   ❌ Still confused - fallback didn't work")
        else:
            print(f"   ✅ Understood: {response[:80]}...")
    
    # Test recommendations
    print(f"\n4️⃣ Testing recommendations based on order")
    plan, response = planning_service.process_user_input(session_id, "recommend products based on my order", tool_orchestrator)
    
    if "not sure how to help" in response.lower():
        print("   ❌ Couldn't handle recommendation request")
    else:
        print(f"   ✅ Generated recommendations: {response[:80]}...")

if __name__ == "__main__":
    test_context_aware_planning()
    print("\n🎉 Context-aware planning test complete!")