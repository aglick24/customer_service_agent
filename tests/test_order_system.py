#!/usr/bin/env python3
"""Test the order lookup system after architecture cleanup"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sierra_agent.core.agent import SierraAgent

def test_order_system():
    """Test order system with the cleaned up architecture"""
    print("🏔️ TESTING CLEANED ORDER SYSTEM")
    print("=" * 50)
    
    # Test 1: Direct order request
    print("\n🧪 Test 1: Direct Order Request")
    print("-" * 30)
    
    agent1 = SierraAgent()
    session_id1 = agent1.start_conversation()
    
    response = agent1.process_user_input("george.hill@example.com, #W009 show me my order")
    print(f"Response: {response}")
    
    # Check for success indicators
    success_indicators = ["#W009", "delivered", "SOBT003", "SOGK009"]
    found_indicators = [ind for ind in success_indicators if ind in response]
    
    if len(found_indicators) >= 3:  # Should find most indicators
        print("✅ SUCCESS: Order details present")
    else:
        print(f"❌ FAILED: Missing order details. Found: {found_indicators}")
        
    if "didn't come through" in response.lower() or "might not have come through" in response.lower():
        print("❌ FAILED: Still showing fallback message")
    else:
        print("✅ SUCCESS: No fallback message")
    
    # Test 2: Multi-step request
    print("\n🧪 Test 2: Multi-step Order Request")
    print("-" * 30)
    
    agent2 = SierraAgent()
    session_id2 = agent2.start_conversation()
    
    agent2.process_user_input("tell me about my order")
    agent2.process_user_input("george.hill@example.com")
    final_response = agent2.process_user_input("#W009")
    
    print(f"Final Response: {final_response}")
    
    if all(indicator in final_response for indicator in ["#W009", "delivered"]):
        print("✅ SUCCESS: Multi-step order lookup works")
    else:
        print("❌ FAILED: Multi-step order lookup failed")

if __name__ == "__main__":
    test_order_system()