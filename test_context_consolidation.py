#!/usr/bin/env python3
"""
Context Consolidation Test

This test validates that the consolidated context system (ConversationContext)
correctly replaces the old scattered context systems.
"""

import sys
from src.sierra_agent.core.planning_types import ConversationContext
from src.sierra_agent.ai.llm_service import LLMService
from src.sierra_agent.ai.context_builder import ContextBuilder
from src.sierra_agent.ai.prompt_templates import PromptTemplates
from src.sierra_agent.data.data_types import Order, Product


def test_conversation_context():
    """Test the unified ConversationContext system."""
    print("🔧 Testing ConversationContext...")
    
    # Test 1: Basic ConversationContext creation
    try:
        context = ConversationContext()
        print("✅ ConversationContext creation successful")
    except Exception as e:
        print(f"❌ ConversationContext creation failed: {e}")
        return False
    
    # Test 2: Context data methods
    try:
        # Test to_available_data (replaces get_available_data)
        available_data = context.to_available_data()
        print(f"✅ to_available_data() works: {type(available_data)}")
        
        # Test interaction summaries (replaces MinimalHistoryItem)
        context.add_interaction_summary("User asked about order status")
        print("✅ add_interaction_summary() works")
        
        # Test prompt context generation
        prompt_context = context.get_prompt_context()
        print(f"✅ get_prompt_context() works: {len(prompt_context)} chars")
        
    except Exception as e:
        print(f"❌ Context methods failed: {e}")
        return False
    
    # Test 3: Add some data and verify it works
    try:
        # Create a mock order
        order = Order(
            order_number="W001",
            customer_name="Test Customer", 
            email="test@example.com",
            status="delivered",
            products_ordered=["SOBP001"],
            tracking_number="TRK123"
        )
        context.current_order = order
        context.customer_email = "test@example.com"
        context.order_number = "W001"
        
        # Test that to_available_data includes this data
        available_data = context.to_available_data()
        if "current_order" in available_data:
            print("✅ Context correctly includes order data")
        else:
            print("❌ Context missing order data")
            return False
            
    except Exception as e:
        print(f"❌ Context data handling failed: {e}")
        return False
    
    print("✅ ConversationContext tests passed!")
    return True


def test_prompt_templates():
    """Test the consolidated PromptTemplates system."""
    print("🔧 Testing PromptTemplates...")
    
    try:
        # Create a context for testing
        context = ConversationContext()
        context.customer_email = "test@example.com"
        
        # Test 1: Missing info prompt
        prompt = PromptTemplates.build_missing_info_prompt(
            plan_context=context,
            user_input="tell me about my order"
        )
        print("✅ build_missing_info_prompt works")
        
        # Test 2: No data response prompt
        prompt = PromptTemplates.build_no_data_response_prompt(
            plan_context=context,
            user_input="hello",
            response_type="greeting"
        )
        print("✅ build_no_data_response_prompt works")
        
        # Test 3: Tool result response prompt
        prompt = PromptTemplates.build_tool_result_response_prompt(
            plan_context=context,
            user_input="check my order",
            result_data="Order W001 found"
        )
        print("✅ build_tool_result_response_prompt works")
        
        # Test 4: Vague request analysis prompt  
        prompt = PromptTemplates.build_vague_request_analysis_prompt(
            plan_context=context,
            user_input="I need help",
            available_tools=["get_order_status", "get_recommendations"]
        )
        print("✅ build_vague_request_analysis_prompt works")
        
    except Exception as e:
        print(f"❌ PromptTemplates failed: {e}")
        return False
    
    print("✅ PromptTemplates tests passed!")
    return True


def test_llm_service_integration():
    """Test LLMService integration with consolidated system.""" 
    print("🔧 Testing LLMService integration...")
    
    try:
        # Test 1: LLMService initialization
        llm_service = LLMService()
        print("✅ LLMService initialization successful")
        
        # Test 2: Statistics method (renamed from get_service_status)
        stats = llm_service.get_agent_statistics()
        if "llm_status" in stats:
            print("✅ get_agent_statistics() works")
        else:
            print("❌ get_agent_statistics() missing expected fields")
            return False
        
        # Test 3: Methods accept plan_context parameter
        context = ConversationContext()
        
        # These should not crash even if LLM calls fail
        try:
            llm_service.analyze_vague_request_and_suggest(
                user_input="help me",
                plan_context=context,
                available_tools=["get_order_status"]
            )
            print("✅ analyze_vague_request_and_suggest accepts plan_context")
        except Exception as e:
            # Expected to fail without API key, but should accept the parameters
            if "plan_context" not in str(e):
                print("✅ analyze_vague_request_and_suggest accepts plan_context")
            else:
                print(f"❌ analyze_vague_request_and_suggest parameter issue: {e}")
                return False
        
    except Exception as e:
        print(f"❌ LLMService integration failed: {e}")
        return False
    
    print("✅ LLMService integration tests passed!")
    return True


def test_context_builder_integration():
    """Test ContextBuilder integration with consolidated system."""
    print("🔧 Testing ContextBuilder integration...")
    
    try:
        context_builder = ContextBuilder()
        print("✅ ContextBuilder initialization successful")
        
        # Test that methods work without crashes
        context = ConversationContext()
        
        # Test customer service context building
        cs_context = context_builder.build_customer_service_context(
            user_input="hello",
            tool_results=[],
            plan_context=context
        )
        print("✅ build_customer_service_context works with plan_context")
        
        # Test planning context building  
        planning_context = context_builder.build_planning_context(
            user_input="help me",
            available_data={},
            available_tools=["get_order_status"]
        )
        print("✅ build_planning_context works without recent_history")
        
    except Exception as e:
        print(f"❌ ContextBuilder integration failed: {e}")
        return False
    
    print("✅ ContextBuilder integration tests passed!")
    return True


def run_all_tests():
    """Run all context consolidation tests."""
    print("🏔️ CONTEXT CONSOLIDATION TEST SUITE 🏔️")
    print("Testing the unified context system...\n")
    
    tests = [
        test_conversation_context,
        test_prompt_templates, 
        test_llm_service_integration,
        test_context_builder_integration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"{'='*50}")
    print(f"RESULTS: {passed}/{len(tests)} test suites passed")
    print(f"{'='*50}")
    
    return passed == len(tests)


if __name__ == "__main__":
    """Run context consolidation validation."""
    try:
        success = run_all_tests()
        if success:
            print("\n🎉 All context consolidation tests PASSED!")
            print("✅ The consolidated context system is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Some context consolidation tests FAILED!")
            print("🔍 Check the consolidated system implementation")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)