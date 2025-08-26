#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sierra Agent

Tests covering tools, planning, and interactions functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sierra_agent.core.agent import SierraAgent


def test_tool_functionality():
    """Test individual tool operations."""
    print("🔧 TESTING TOOL FUNCTIONALITY")
    print("=" * 50)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Test 1: Order lookup tool
    print("\n🧪 Test 1: Order Lookup Tool")
    print("-" * 30)
    response = agent.process_user_input("george.hill@example.com, #W009 show my order")
    success_indicators = ["#W009", "delivered", "SOBT003", "SOGK009"]
    found = [ind for ind in success_indicators if ind in response]
    print(f"Order lookup: {'✅ PASS' if len(found) >= 3 else '❌ FAIL'} ({len(found)}/4 indicators)")
    
    # Test 2: Product search tool
    print("\n🧪 Test 2: Product Search Tool")
    print("-" * 30)
    response = agent.process_user_input("search for hiking boots")
    boot_indicators = ["hiking", "boot", "trail", "outdoor"]
    found = [ind for ind in boot_indicators if ind.lower() in response.lower()]
    print(f"Product search: {'✅ PASS' if len(found) >= 2 else '❌ FAIL'} ({len(found)}/4 indicators)")
    
    # Test 3: Early Risers promotion tool
    print("\n🧪 Test 3: Promotion Tool")
    print("-" * 30)
    response = agent.process_user_input("any early morning discounts?")
    promo_indicators = ["early", "discount", "promotion", "risers"]
    found = [ind for ind in promo_indicators if ind.lower() in response.lower()]
    print(f"Promotion tool: {'✅ PASS' if len(found) >= 2 else '❌ FAIL'} ({len(found)}/4 indicators)")


def test_planning_system():
    """Test planning system with complex multi-step requests."""
    print("\n🧠 TESTING PLANNING SYSTEM")
    print("=" * 50)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Test 1: Complex multi-step request
    print("\n🧪 Test 1: Complex Multi-Step Planning")
    print("-" * 30)
    complex_request = "I need to check my order W009 for george.hill@example.com and also want recommendations for similar hiking gear"
    response = agent.process_user_input(complex_request)
    planning_indicators = ["order", "W009", "recommendation", "hiking"]
    found = [ind for ind in planning_indicators if ind.lower() in response.lower()]
    print(f"Complex planning: {'✅ PASS' if len(found) >= 3 else '❌ FAIL'} ({len(found)}/4 indicators)")
    
    # Test 2: Sequential context building
    print("\n🧪 Test 2: Sequential Context Planning")
    print("-" * 30)
    agent.process_user_input("I want to explore outdoor gear")
    agent.process_user_input("Specifically for winter camping")
    response = agent.process_user_input("What would you recommend?")
    context_indicators = ["winter", "camping", "outdoor", "gear"]
    found = [ind for ind in context_indicators if ind.lower() in response.lower()]
    print(f"Context planning: {'✅ PASS' if len(found) >= 2 else '❌ FAIL'} ({len(found)}/4 indicators)")
    
    # Test 3: Order + Product details planning
    print("\n🧪 Test 3: Order Analysis Planning")
    print("-" * 30)
    response = agent.process_user_input("Show me details about the products in order W009 for george.hill@example.com")
    detail_indicators = ["SOBT003", "SOGK009", "product", "detail"]
    found = [ind for ind in detail_indicators if ind in response]
    print(f"Order analysis: {'✅ PASS' if len(found) >= 2 else '❌ FAIL'} ({len(found)}/4 indicators)")


def test_interaction_flows():
    """Test conversation interactions and memory."""
    print("\n💬 TESTING INTERACTION FLOWS")
    print("=" * 50)
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Test 1: Multi-turn conversation
    print("\n🧪 Test 1: Multi-Turn Conversation")
    print("-" * 30)
    agent.process_user_input("I need help with my order")
    agent.process_user_input("george.hill@example.com")
    response = agent.process_user_input("order W009")
    memory_indicators = ["W009", "george.hill", "order"]
    found = [ind for ind in memory_indicators if ind in response]
    print(f"Conversation memory: {'✅ PASS' if len(found) >= 2 else '❌ FAIL'} ({len(found)}/3 indicators)")
    
    # Test 2: Follow-up questions
    print("\n🧪 Test 2: Follow-up Context")
    print("-" * 30)
    agent.process_user_input("search for hiking boots")
    response = agent.process_user_input("what about waterproof ones?")
    followup_indicators = ["waterproof", "boot", "hiking"]
    found = [ind for ind in followup_indicators if ind.lower() in response.lower()]
    print(f"Follow-up context: {'✅ PASS' if len(found) >= 2 else '❌ FAIL'} ({len(found)}/3 indicators)")
    
    # Test 3: Error handling and recovery
    print("\n🧪 Test 3: Error Handling")
    print("-" * 30)
    response = agent.process_user_input("check order INVALID123 for fake@email.com")
    error_indicators = ["not found", "unable", "error", "invalid"]
    found = [ind for ind in error_indicators if ind.lower() in response.lower()]
    print(f"Error handling: {'✅ PASS' if len(found) >= 1 else '❌ FAIL'} ({len(found)}/4 indicators)")


def run_comprehensive_tests():
    """Run all test suites."""
    print("🏔️ SIERRA AGENT COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing tools, planning, and interactions...")
    
    try:
        test_tool_functionality()
        test_planning_system()
        test_interaction_flows()
        
        print("\n🎉 TEST SUITE COMPLETED")
        print("=" * 60)
        print("All major functionality areas have been tested.")
        print("Review individual test results above for details.")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE ERROR: {e}")
        print("Some tests may not have completed successfully.")


if __name__ == "__main__":
    run_comprehensive_tests()