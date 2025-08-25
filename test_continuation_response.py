#!/usr/bin/env python3
"""
Test script for continuation response generation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.core.agent import SierraAgent

def test_continuation_response():
    """Test that continuation completion generates proper responses."""
    print("🧪 [TEST] Testing continuation response generation...\n")
    
    # Initialize agent and start conversation
    agent = SierraAgent()
    session_id = agent.start_conversation()
    print(f"🚀 Started conversation session: {session_id}\n")
    
    # Test: Order lookup requiring continuation
    print("=" * 60)
    print("TEST: Order lookup requiring continuation and proper response")
    print("=" * 60)
    
    # Step 1: Ask for order without email (should trigger continuation)
    print("Step 1: Ask for order without email")
    response1 = agent.process_user_input("tell me about order #W009")
    print(f"Response 1: {response1}")
    print()
    
    # Step 2: Provide email (should complete continuation with proper response)
    print("Step 2: Provide email to complete continuation")
    response2 = agent.process_user_input("george.hill@example.com")
    print(f"Response 2: {response2}")
    print()
    
    print("🧪 [TEST] Continuation response test completed!")

if __name__ == "__main__":
    test_continuation_response()