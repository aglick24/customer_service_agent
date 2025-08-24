"""
Tests for data types and models.
"""

import pytest
from datetime import datetime
from sierra_agent.data.data_types import (
    IntentType, SentimentType, QualityLevel,
    Product, Order, Customer, QualityScore,
    ConversationMetrics, ToolResult, BusinessRule,
    validate_email, validate_order_id, sanitize_input,
    format_currency, format_datetime
)


class TestIntentType:
    """Test IntentType enum."""
    
    def test_intent_values(self):
        """Test that all intent values are properly defined."""
        assert IntentType.ORDER_STATUS.value == "ORDER_STATUS"
        assert IntentType.PRODUCT_INQUIRY.value == "PRODUCT_INQUIRY"
        assert IntentType.CUSTOMER_SERVICE.value == "CUSTOMER_SERVICE"
        assert IntentType.COMPLAINT.value == "COMPLAINT"
        assert IntentType.COMPLIMENT.value == "COMPLIMENT"
        assert IntentType.RETURN_REQUEST.value == "RETURN_REQUEST"
        assert IntentType.SHIPPING_INFO.value == "SHIPPING_INFO"
        assert IntentType.PROMOTION_INQUIRY.value == "PROMOTION_INQUIRY"
    
    def test_intent_from_value(self):
        """Test creating IntentType from string value."""
        intent = IntentType("ORDER_STATUS")
        assert intent == IntentType.ORDER_STATUS
        
        intent = IntentType("PRODUCT_INQUIRY")
        assert intent == IntentType.PRODUCT_INQUIRY


class TestSentimentType:
    """Test SentimentType enum."""
    
    def test_sentiment_values(self):
        """Test that all sentiment values are properly defined."""
        assert SentimentType.POSITIVE.value == "POSITIVE"
        assert SentimentType.NEUTRAL.value == "NEUTRAL"
        assert SentimentType.NEGATIVE.value == "NEGATIVE"
    
    def test_sentiment_from_value(self):
        """Test creating SentimentType from string value."""
        sentiment = SentimentType("POSITIVE")
        assert sentiment == SentimentType.POSITIVE


class TestQualityLevel:
    """Test QualityLevel enum."""
    
    def test_quality_values(self):
        """Test that all quality level values are properly defined."""
        assert QualityLevel.EXCELLENT.value == "EXCELLENT"
        assert QualityLevel.GOOD.value == "GOOD"
        assert QualityLevel.FAIR.value == "FAIR"
        assert QualityLevel.POOR.value == "POOR"


class TestProduct:
    """Test Product dataclass."""
    
    def test_product_creation(self, sample_product):
        """Test creating a product."""
        assert sample_product.id == "TEST001"
        assert sample_product.name == "Test Hiking Boots"
        assert sample_product.category == "Hiking & Backpacking"
        assert sample_product.price == 99.99
        assert sample_product.availability is True
        assert sample_product.stock_quantity == 10
        assert "test" in sample_product.tags
    
    def test_product_to_dict(self, sample_product):
        """Test product serialization to dictionary."""
        product_dict = sample_product.to_dict()
        assert product_dict["id"] == "TEST001"
        assert product_dict["name"] == "Test Hiking Boots"
        assert product_dict["price"] == 99.99
        assert product_dict["tags"] == ["test", "hiking", "boots"]
    
    def test_product_defaults(self):
        """Test product with default values."""
        product = Product(
            id="MINIMAL",
            name="Minimal Product",
            category="Test",
            price=10.0,
            description="Minimal description",
            availability=False,
            stock_quantity=0
        )
        assert product.tags == []
        assert product.image_url is None


class TestOrder:
    """Test Order dataclass."""
    
    def test_order_creation(self, sample_order):
        """Test creating an order."""
        assert sample_order.order_id == "ORD12345"
        assert sample_order.customer_email == "test@example.com"
        assert sample_order.customer_name == "Test Customer"
        assert len(sample_order.items) == 1
        assert sample_order.total_amount == 99.99
        assert sample_order.status == "Processing"
    
    def test_order_to_dict(self, sample_order):
        """Test order serialization to dictionary."""
        order_dict = sample_order.to_dict()
        assert order_dict["order_id"] == "ORD12345"
        assert order_dict["customer_email"] == "test@example.com"
        assert order_dict["total_amount"] == 99.99
        assert "items" in order_dict
        assert len(order_dict["items"]) == 1


class TestCustomer:
    """Test Customer dataclass."""
    
    def test_customer_creation(self, sample_customer):
        """Test creating a customer."""
        assert sample_customer.customer_id == "CUST001"
        assert sample_customer.email == "test@example.com"
        assert sample_customer.name == "Test Customer"
        assert sample_customer.phone == "555-0123"
        assert sample_customer.preferences["category"] == "hiking"
        assert "ORD12345" in sample_customer.order_history
    
    def test_customer_to_dict(self, sample_customer):
        """Test customer serialization to dictionary."""
        customer_dict = sample_customer.to_dict()
        assert customer_dict["customer_id"] == "CUST001"
        assert customer_dict["email"] == "test@example.com"
        assert customer_dict["preferences"]["category"] == "hiking"


class TestQualityScore:
    """Test QualityScore dataclass."""
    
    def test_quality_score_creation(self, sample_quality_score):
        """Test creating a quality score."""
        assert sample_quality_score.overall_score == 0.85
        assert sample_quality_score.relevance_score == 0.9
        assert sample_quality_score.helpfulness_score == 0.8
        assert sample_quality_score.quality_level == QualityLevel.GOOD
        assert len(sample_quality_score.recommendations) == 2
    
    def test_quality_score_to_dict(self, sample_quality_score):
        """Test quality score serialization to dictionary."""
        score_dict = sample_quality_score.to_dict()
        assert score_dict["overall_score"] == 0.85
        assert score_dict["quality_level"] == "GOOD"
        assert "recommendations" in score_dict


class TestConversationMetrics:
    """Test ConversationMetrics dataclass."""
    
    def test_metrics_creation(self, sample_conversation_metrics):
        """Test creating conversation metrics."""
        assert sample_conversation_metrics.session_id == "session_123"
        assert sample_conversation_metrics.conversation_length == 4
        assert sample_conversation_metrics.duration_seconds == 120.5
        assert sample_conversation_metrics.quality_score == 0.85
        assert sample_conversation_metrics.customer_satisfaction == 0.8
    
    def test_metrics_to_dict(self, sample_conversation_metrics):
        """Test metrics serialization to dictionary."""
        metrics_dict = sample_conversation_metrics.to_dict()
        assert metrics_dict["session_id"] == "session_123"
        assert metrics_dict["conversation_length"] == 4
        assert "intent_distribution" in metrics_dict


class TestToolResult:
    """Test ToolResult dataclass."""
    
    def test_tool_result_creation(self, sample_tool_result):
        """Test creating a tool result."""
        assert sample_tool_result.tool_name == "search_products"
        assert sample_tool_result.success is True
        assert "products" in sample_tool_result.data
        assert sample_tool_result.execution_time == 0.1
        assert sample_tool_result.error_message is None
    
    def test_tool_result_to_dict(self, sample_tool_result):
        """Test tool result serialization to dictionary."""
        result_dict = sample_tool_result.to_dict()
        assert result_dict["tool_name"] == "search_products"
        assert result_dict["success"] is True
        assert result_dict["execution_time"] == 0.1


class TestBusinessRule:
    """Test BusinessRule dataclass."""
    
    def test_business_rule_creation(self):
        """Test creating a business rule."""
        rule = BusinessRule(
            rule_id="RULE001",
            rule_name="Test Rule",
            description="A test business rule",
            conditions={"condition": "test"},
            actions=["action1", "action2"],
            priority=5
        )
        assert rule.rule_id == "RULE001"
        assert rule.rule_name == "Test Rule"
        assert rule.priority == 5
        assert rule.is_active is True
    
    def test_business_rule_to_dict(self):
        """Test business rule serialization to dictionary."""
        rule = BusinessRule(
            rule_id="RULE001",
            rule_name="Test Rule",
            description="A test business rule",
            conditions={"condition": "test"},
            actions=["action1"]
        )
        rule_dict = rule.to_dict()
        assert rule_dict["rule_id"] == "RULE001"
        assert rule_dict["is_active"] is True


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_validate_email(self):
        """Test email validation."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.co.uk") is True
        assert validate_email("invalid-email") is False
        assert validate_email("") is False
    
    def test_validate_order_id(self):
        """Test order ID validation."""
        assert validate_order_id("ORD12345") is True
        assert validate_order_id("12345678") is True
        assert validate_order_id("123") is False  # Too short
        assert validate_order_id("1234567890123") is False  # Too long
        assert validate_order_id("ORD-123") is False  # Invalid characters
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test that HTML is properly escaped
        sanitized = sanitize_input("<script>alert('xss')</script>")
        assert "&lt;" in sanitized  # < should be escaped
        assert "&gt;" in sanitized  # > should be escaped
        assert "&lt;script&gt;" in sanitized
        assert "&lt;/script&gt;" in sanitized
        
        # Test normal text
        assert sanitize_input("  normal text  ") == "normal text"
        assert sanitize_input("") == ""
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(99.99) == "$99.99"
        assert format_currency(0.0) == "$0.00"
        assert format_currency(1234.56) == "$1234.56"
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime(dt)
        assert "2024-01-15 14:30:00" in formatted
