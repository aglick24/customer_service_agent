#!/usr/bin/env python3
"""
Simple test runner for Sierra Agent system.
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent import SierraAgent, Branding
from sierra_agent.data.data_types import Product, Order, Customer, IntentType, SentimentType
from sierra_agent.core.conversation import Conversation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """Test basic system functionality."""
    print("🧪 Testing basic system functionality...")
    
    try:
        # Test data types
        product = Product(
            id="TEST001",
            name="Test Product",
            category="Test",
            price=99.99,
            description="A test product",
            availability=True,
            stock_quantity=10
        )
        assert product.name == "Test Product"
        assert product.price == 99.99
        print("✅ Data types working")
        
        # Test conversation
        conversation = Conversation()
        conversation.add_user_message("Hello")
        conversation.add_ai_message("Hi there!")
        assert len(conversation.messages) == 2
        print("✅ Conversation management working")
        
        # Test branding
        assert Branding.COMPANY_NAME == "Sierra Outfitters"
        print("✅ Branding working")
        
        print("✅ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization."""
    print("\n🤖 Testing agent initialization...")
    
    try:
        # Note: This will fail without OPENAI_API_KEY, but we can test the structure
        agent = SierraAgent()
        assert agent is not None
        assert hasattr(agent, 'conversation')
        assert hasattr(agent, 'tool_orchestrator')
        assert hasattr(agent, 'quality_scorer')
        assert hasattr(agent, 'analytics')
        print("✅ Agent structure verified")
        
        # Test conversation start (without API calls)
        session_id = agent.start_conversation()
        assert session_id is not None
        assert "session_" in session_id
        print("✅ Conversation session created")
        
        print("✅ Agent initialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization test failed: {e}")
        return False

def test_business_tools():
    """Test business tools functionality."""
    print("\n🛠️ Testing business tools...")
    
    try:
        from sierra_agent.tools.business_tools import BusinessTools
        
        tools = BusinessTools()
        assert len(tools.mock_products) > 0
        assert len(tools.mock_orders) > 0
        assert len(tools.mock_customers) > 0
        print("✅ Business tools initialized")
        
        # Test a simple tool
        result = tools.get_company_info("Tell me about your company")
        assert "company_name" in result
        assert "description" in result
        print("✅ Business tools working")
        
        print("✅ Business tools tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Business tools test failed: {e}")
        return False

def main():
    """Run all tests."""
    print(f"🚀 {Branding.COMPANY_INTRO}")
    print("=" * 60)
    print("Running Sierra Agent system tests...")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_agent_initialization,
        test_business_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
