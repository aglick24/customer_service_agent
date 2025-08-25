#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sierra Outfitters Agent Chat Loop

This test suite validates the core requirements from the original assignment:
1. Order Status and Tracking
2. Product Recommendations  
3. Early Risers Promotion
4. Agent Chat Loop with outdoor branding
5. Multi-step workflows and conversation design

Run with: python test_comprehensive_agent.py
"""

import sys
from datetime import datetime
from typing import Dict, List, Tuple
from src.sierra_agent.core.agent import SierraAgent


class AgentTester:
    """Comprehensive test runner for Sierra Outfitters Agent."""
    
    def __init__(self):
        self.agent = SierraAgent()
        self.session_id = None
        self.test_results = []
        
    def reset_session(self):
        """Start a fresh conversation session."""
        self.session_id = self.agent.start_conversation()
        
    def send_message(self, message: str) -> str:
        """Send a message and return the agent's response."""
        return self.agent.process_user_input(message)
    
    def assert_contains(self, response: str, expected: str, test_name: str):
        """Assert that response contains expected text."""
        success = expected.lower() in response.lower()
        self.test_results.append({
            'test': test_name,
            'success': success,
            'expected': expected,
            'response': response[:200] + '...' if len(response) > 200 else response
        })
        return success
    
    def assert_not_contains(self, response: str, unexpected: str, test_name: str):
        """Assert that response does NOT contain unexpected text."""
        success = unexpected.lower() not in response.lower()
        self.test_results.append({
            'test': test_name,
            'success': success,
            'expected': f'Should NOT contain: {unexpected}',
            'response': response[:200] + '...' if len(response) > 200 else response
        })
        return success
        
    def print_results(self):
        """Print test results summary."""
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"\n{'='*60}")
        print(f"TEST RESULTS: {passed}/{total} PASSED")
        print(f"{'='*60}")
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if not result['success']:
                print(f"    Expected: {result['expected']}")
                print(f"    Response: {result['response']}")
                print()


def run_comprehensive_tests():
    """Run all comprehensive test suites."""
    tester = AgentTester()
    
    print("🏔️ SIERRA OUTFITTERS AGENT COMPREHENSIVE TEST SUITE 🏔️")
    print("Testing against original assignment requirements...\n")
    
    # Test Suite 1: Order Status and Tracking
    test_order_status_and_tracking(tester)
    
    # Test Suite 2: Product Recommendations  
    test_product_recommendations(tester)
    
    # Test Suite 3: Early Risers Promotion
    test_early_risers_promotion(tester)
    
    # Test Suite 4: Multi-step Workflows
    test_multistep_workflows(tester)
    
    # Test Suite 5: Conversation Design and Branding
    test_conversation_design(tester)
    
    # Test Suite 6: Error Handling and Edge Cases
    test_error_handling(tester)
    
    # Print final results
    tester.print_results()


def test_order_status_and_tracking(tester: AgentTester):
    """Test Suite 1: Order Status and Tracking"""
    print("🔍 Testing Order Status and Tracking...")
    
    # Test 1.1: Basic order lookup flow
    tester.reset_session()
    response1 = tester.send_message("tell me about my order")
    tester.assert_contains(response1, "email", "1.1a: Asks for email and order number")
    tester.assert_contains(response1, "order number", "1.1b: Asks for email and order number")
    
    # Test 1.2: Provide email
    response2 = tester.send_message("george.hill@example.com")
    tester.assert_contains(response2, "order number", "1.2: Asks for order number after email")
    
    # Test 1.3: Provide order number and get order details
    response3 = tester.send_message("#W009")
    tester.assert_contains(response3, "W009", "1.3a: Shows order number")
    tester.assert_contains(response3, "George Hill", "1.3b: Shows customer name")
    tester.assert_contains(response3, "delivered", "1.3c: Shows order status")
    
    # Test 1.4: Check for tracking information
    tester.assert_contains(response3, "TRK445566778", "1.4a: Shows tracking number")
    tester.assert_contains(response3, "https://tools.usps.com/go/TrackConfirmAction?tLabels=TRK445566778", "1.4b: Shows tracking URL")
    
    # Test 1.5: Provide both email and order number at once
    tester.reset_session()
    response4 = tester.send_message("My email is george.hill@example.com and my order number is #W009")
    tester.assert_contains(response4, "delivered", "1.5: Handles email and order number together")
    
    print("   ✓ Order Status and Tracking tests completed\n")


def test_product_recommendations(tester: AgentTester):
    """Test Suite 2: Product Recommendations"""
    print("🛍️ Testing Product Recommendations...")
    
    # Test 2.1: General product recommendations
    tester.reset_session()
    response1 = tester.send_message("what products do you recommend?")
    tester.assert_contains(response1, "backpack", "2.1a: Returns product recommendations")
    tester.assert_not_contains(response1, "I don't have", "2.1b: Actually provides recommendations")
    
    # Test 2.2: Product search
    response2 = tester.send_message("show me outdoor gear")
    tester.assert_contains(response2, "outdoor", "2.2: Handles product search requests")
    
    # Test 2.3: Specific product inquiry
    response3 = tester.send_message("tell me about the backpack")
    tester.assert_contains(response3, "backpack", "2.3a: Provides product details")
    tester.assert_contains(response3, "SOBP001", "2.3b: Shows product SKU")
    
    # Test 2.4: Order-based recommendations
    tester.reset_session() 
    tester.send_message("tell me about my order")
    tester.send_message("george.hill@example.com, #W009")
    response4 = tester.send_message("give me recommendations based on my order")
    tester.assert_contains(response4, "recommend", "2.4: Provides order-based recommendations")
    
    print("   ✓ Product Recommendations tests completed\n")


def test_early_risers_promotion(tester: AgentTester):
    """Test Suite 3: Early Risers Promotion"""
    print("🌅 Testing Early Risers Promotion...")
    
    # Test 3.1: Request promotion (time-independent test)
    tester.reset_session()
    response1 = tester.send_message("do you have any promotions or discounts?")
    tester.assert_contains(response1, "early risers", "3.1a: Mentions Early Risers promotion")
    tester.assert_contains(response1, "8:00", "3.1b: Shows valid hours")
    tester.assert_contains(response1, "10:00", "3.1c: Shows valid hours")
    
    # Test 3.2: Specific Early Risers request
    response2 = tester.send_message("I want the Early Risers promotion")
    # Note: This will depend on current time, but should handle gracefully
    success = ("discount" in response2.lower() or "8:00" in response2 or "not available" in response2.lower())
    tester.test_results.append({
        'test': "3.2: Handles Early Risers promotion request",
        'success': success,
        'expected': 'Either provides discount or explains time restriction',
        'response': response2[:200] + '...'
    })
    
    print("   ✓ Early Risers Promotion tests completed\n")


def test_multistep_workflows(tester: AgentTester):
    """Test Suite 4: Multi-step Workflows"""
    print("⚡ Testing Multi-step Workflows...")
    
    # Test 4.1: Compound request - order details and recommendations
    tester.reset_session()
    response1 = tester.send_message("tell me about my order")
    tester.send_message("george.hill@example.com, #W009")
    response2 = tester.send_message("tell me about the products I ordered and give me recommendations")
    
    tester.assert_contains(response2, "infinity pro hairbrush", "4.1a: Shows ordered product details")
    tester.assert_contains(response2, "recommend", "4.1b: Provides recommendations")
    tester.assert_contains(response2, "backpack", "4.1c: Shows recommended products")
    
    # Test 4.2: Complex multi-step request in single message
    tester.reset_session()
    response3 = tester.send_message("I want to check my order status for george.hill@example.com #W009 and get product recommendations")
    tester.assert_contains(response3, "delivered", "4.2a: Handles order lookup")
    tester.assert_contains(response3, "recommend", "4.2b: Provides recommendations")
    
    # Test 4.3: Context persistence across conversation
    tester.reset_session()
    tester.send_message("tell me about my order")
    tester.send_message("george.hill@example.com")
    tester.send_message("#W009")
    response4 = tester.send_message("what products were in that order?")
    tester.assert_contains(response4, "SOBT003", "4.3: Uses context from previous order lookup")
    
    print("   ✓ Multi-step Workflows tests completed\n")


def test_conversation_design(tester: AgentTester):
    """Test Suite 5: Conversation Design and Branding"""
    print("🏔️ Testing Conversation Design and Branding...")
    
    # Test 5.1: Outdoor branding and tone
    tester.reset_session()
    response1 = tester.send_message("hello")
    outdoor_phrases = ["🏔️", "adventure", "outdoor", "mountain", "trail", "onward", "unknown"]
    has_outdoor_branding = any(phrase in response1.lower() for phrase in outdoor_phrases)
    tester.test_results.append({
        'test': "5.1: Uses outdoor branding and enthusiasm", 
        'success': has_outdoor_branding,
        'expected': 'Contains outdoor/adventure themes',
        'response': response1[:200] + '...'
    })
    
    # Test 5.2: Specific Sierra branding phrases
    tester.reset_session()
    response2 = tester.send_message("thanks for your help")
    contains_signature = ("onward into the unknown" in response2.lower() or 
                         "adventure" in response2.lower() or
                         "🏔️" in response2)
    tester.test_results.append({
        'test': "5.2: Uses Sierra signature phrases",
        'success': contains_signature, 
        'expected': 'Contains signature outdoor phrases',
        'response': response2[:200] + '...'
    })
    
    # Test 5.3: Helpful and enthusiastic tone
    response3 = tester.send_message("I need help")
    tester.assert_contains(response3, "help", "5.3a: Acknowledges help request")
    enthusiastic_words = ["excited", "happy", "great", "fantastic", "wonderful", "!"]
    has_enthusiasm = any(word in response3.lower() for word in enthusiastic_words)
    tester.test_results.append({
        'test': "5.3b: Shows enthusiasm and helpfulness",
        'success': has_enthusiasm,
        'expected': 'Shows enthusiastic and helpful tone',
        'response': response3[:200] + '...'
    })
    
    print("   ✓ Conversation Design and Branding tests completed\n")


def test_error_handling(tester: AgentTester):
    """Test Suite 6: Error Handling and Edge Cases"""
    print("🔧 Testing Error Handling and Edge Cases...")
    
    # Test 6.1: Invalid order number
    tester.reset_session()
    tester.send_message("tell me about my order")
    tester.send_message("george.hill@example.com")
    response1 = tester.send_message("#INVALID")
    tester.assert_contains(response1, "error", "6.1: Handles invalid order number")
    
    # Test 6.2: Vague/incomplete requests
    tester.reset_session()
    response2 = tester.send_message("I want")
    tester.assert_contains(response2, "help", "6.2a: Handles incomplete requests")
    
    # Test 6.3: Nonsensical input
    response3 = tester.send_message("blah blah xyz")
    helpful_responses = ["help", "assist", "specific", "more information"]
    is_helpful = any(phrase in response3.lower() for phrase in helpful_responses)
    tester.test_results.append({
        'test': "6.3: Handles nonsensical input gracefully",
        'success': is_helpful,
        'expected': 'Provides helpful guidance',
        'response': response3[:200] + '...'
    })
    
    # Test 6.4: Missing information handling
    tester.reset_session()
    response4 = tester.send_message("tell me about my order")
    response5 = tester.send_message("I don't know my order number")
    tester.assert_contains(response5, "order number", "6.4: Explains what information is needed")
    
    print("   ✓ Error Handling and Edge Cases tests completed\n")


if __name__ == "__main__":
    """Run the comprehensive test suite."""
    try:
        run_comprehensive_tests()
        print("\n🎉 Test suite execution completed!")
        print("Review the results above to see which features need attention.")
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)