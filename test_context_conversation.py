#!/usr/bin/env python3

"""
Test multi-turn conversation with context understanding.
"""

import os
import sys

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.core.agent import SierraAgent, AgentConfig

def test_multi_turn_context_conversation():
    """Test that the agent can understand context in multi-turn conversations."""
    print("🧪 [TEST] Testing multi-turn context conversation...")
    
    # Initialize agent
    config = AgentConfig()
    agent = SierraAgent(config)
    
    # Start conversation
    session_id = agent.start_conversation()
    print(f"🧪 [TEST] Started session: {session_id}")
    
    # First interaction - establish context
    print("\n" + "="*60)
    print("🧪 [TEST] TURN 1: Initial order request")
    print("="*60)
    
    response1 = agent.process_user_input("my email is george.hill@example.com, check order #w009 for me please")
    
    print(f"🧪 [TEST] Response 1:")
    print(response1)
    
    # Second interaction - use context reference "my order"
    print("\n" + "="*60)
    print("🧪 [TEST] TURN 2: Context reference to previous order")
    print("="*60)
    
    response2 = agent.process_user_input("tell me about the products in my order and recommend others that i could like")
    
    print(f"🧪 [TEST] Response 2:")
    print(response2)
    
    # Analyze results
    print("\n" + "="*60)
    print("🧪 [TEST] ANALYSIS")
    print("="*60)
    
    # Check if second response addresses products and recommendations
    success_indicators = [
        "product" in response2.lower() and "sobt003" in response2.lower(),  # Should mention specific products
        "sogk009" in response2.lower(),  # Should mention the other product
        "recommend" in response2.lower() or "suggestion" in response2.lower(),  # Should have recommendations
        "george" in response2.lower(),  # Should maintain personal context
    ]
    
    success_count = sum(success_indicators)
    
    if success_count >= 3:
        print("✅ [TEST] SUCCESS: Agent correctly understood context references")
        print(f"✅ [TEST] Met {success_count}/4 success indicators")
        return True
    else:
        print("❌ [TEST] FAILED: Agent did not properly use conversation context")
        print(f"❌ [TEST] Only met {success_count}/4 success indicators")
        print("❌ [TEST] Expected: Product details + recommendations using previous order context")
        return False

if __name__ == "__main__":
    success = test_multi_turn_context_conversation()
    if success:
        print("\n🎉 [TEST] Multi-turn context conversation test PASSED!")
    else:
        print("\n❌ [TEST] Multi-turn context conversation test FAILED!")