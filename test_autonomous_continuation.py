#!/usr/bin/env python3
"""
Test script for autonomous tool continuation functionality.
This tests the minimal continuation system we implemented.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.core.agent import SierraAgent

def test_autonomous_continuation():
    """Test the autonomous continuation flow end-to-end."""
    print("🧪 [TEST] Starting autonomous continuation test...\n")
    
    # Initialize agent and start conversation
    agent = SierraAgent()
    session_id = agent.start_conversation()
    print(f"🚀 Started conversation session: {session_id}\n")
    
    # Test Case 1: First interaction - order lookup with email
    print("=" * 60)
    print("TEST CASE 1: Order lookup with complete information")
    print("=" * 60)
    response1 = agent.process_user_input("Can you check the status of order W001 for john.doe@example.com?")
    print(f"Response 1: {response1}")
    print()
    
    # Test Case 2: Second interaction - asking about products without email context
    # This should trigger the continuation logic
    print("=" * 60)
    print("TEST CASE 2: Ask about products without providing email (should trigger continuation)")
    print("=" * 60)
    response2 = agent.process_user_input("tell me about the products i ordered and recommend related products")
    print(f"Response 2: {response2}")
    print()
    
    # Test Case 3: Provide the missing order number to continue
    print("=" * 60)
    print("TEST CASE 3: Provide missing order number to continue tool execution")
    print("=" * 60)
    response3 = agent.process_user_input("W001")
    print(f"Response 3: {response3}")
    print()
    
    print("🧪 [TEST] Autonomous continuation test completed!")

if __name__ == "__main__":
    test_autonomous_continuation()