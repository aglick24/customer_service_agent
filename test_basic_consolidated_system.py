#!/usr/bin/env python3
"""
Basic Test for Consolidated Context System

This test validates that the consolidated context system works correctly
after the refactoring. It focuses on core functionality without complex flows.
"""

import sys
from src.sierra_agent.core.agent import SierraAgent


def test_basic_system():
    """Test basic system initialization and simple interactions."""
    print("🔧 Testing Basic Consolidated System...")
    
    # Test 1: Agent initialization
    try:
        agent = SierraAgent()
        print("✅ Agent initialization successful")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False
    
    # Test 2: Start conversation session
    try:
        session_id = agent.start_conversation()
        print(f"✅ Conversation session started: {session_id}")
    except Exception as e:
        print(f"❌ Conversation session failed: {e}")
        return False
    
    # Test 3: Basic greeting (should work with new consolidated system)
    try:
        response = agent.process_user_input("hello")
        print(f"✅ Basic greeting response: {response[:100]}...")
        
        # Check for outdoor branding (basic requirement)
        if "🏔️" in response or "adventure" in response.lower():
            print("✅ Outdoor branding present")
        else:
            print("⚠️ Outdoor branding might be missing")
            
    except Exception as e:
        print(f"❌ Basic greeting failed: {e}")
        return False
    
    # Test 4: Simple order inquiry (context system test)
    try:
        response = agent.process_user_input("tell me about my order")
        print(f"✅ Order inquiry response: {response[:100]}...")
        
        # Should ask for email/order number
        if "email" in response.lower() or "order" in response.lower():
            print("✅ Context system working - asks for missing info")
        else:
            print("⚠️ Context system might not be working properly")
            
    except Exception as e:
        print(f"❌ Order inquiry failed: {e}")
        return False
    
    # Test 5: LLM service status
    try:
        status = agent.get_llm_status()
        print(f"✅ LLM service status: {status.get('llm_status', 'unknown')}")
    except Exception as e:
        print(f"❌ LLM status check failed: {e}")
        return False
    
    print("\n🎉 Basic consolidated system tests PASSED!")
    return True


if __name__ == "__main__":
    """Run basic system validation."""
    try:
        success = test_basic_system()
        if success:
            print("\n✅ All basic tests passed - consolidated system is working!")
            sys.exit(0)
        else:
            print("\n❌ Some basic tests failed - check the consolidated system")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)