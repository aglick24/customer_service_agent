"""
Pytest configuration and fixtures for Sierra Agent tests.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sierra_agent.data.data_types import (
    IntentType, SentimentType, QualityLevel,
    Product, Order, Customer, QualityScore,
    ConversationMetrics, ToolResult
)
from sierra_agent.core.conversation import Conversation, Message, MessageType
from sierra_agent.utils.branding import Branding
from sierra_agent.utils.error_messages import ErrorMessages


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('sierra_agent.ai.llm_client.openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 5,
                'total_tokens': 15
            }
        }
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        yield mock_client


@pytest.fixture
def sample_product():
    """Sample product for testing."""
    return Product(
        id="TEST001",
        name="Test Hiking Boots",
        category="Hiking & Backpacking",
        price=99.99,
        description="Test hiking boots for testing",
        availability=True,
        stock_quantity=10,
        tags=["test", "hiking", "boots"]
    )


@pytest.fixture
def sample_order():
    """Sample order for testing."""
    from datetime import datetime, timedelta
    
    return Order(
        order_id="ORD12345",
        customer_email="test@example.com",
        customer_name="Test Customer",
        items=[{"product_id": "TEST001", "quantity": 1, "price": 99.99}],
        total_amount=99.99,
        status="Processing",
        order_date=datetime.now() - timedelta(days=1),
        estimated_delivery=datetime.now() + timedelta(days=3)
    )


@pytest.fixture
def sample_customer():
    """Sample customer for testing."""
    from datetime import datetime
    
    return Customer(
        customer_id="CUST001",
        email="test@example.com",
        name="Test Customer",
        phone="555-0123",
        preferences={"category": "hiking", "size": "10"},
        order_history=["ORD12345"]
    )


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing."""
    conversation = Conversation()
    conversation.add_user_message("Hello, I need help with hiking boots")
    conversation.add_ai_message("I'd be happy to help you find hiking boots!")
    return conversation


@pytest.fixture
def sample_quality_score():
    """Sample quality score for testing."""
    return QualityScore(
        overall_score=0.85,
        relevance_score=0.9,
        helpfulness_score=0.8,
        engagement_score=0.85,
        resolution_score=0.8,
        sentiment_trajectory_score=0.9,
        response_time_score=0.8,
        tool_effectiveness_score=0.8,
        quality_level=QualityLevel.GOOD,
        recommendations=["Great conversation flow", "Maintain helpful tone"]
    )


@pytest.fixture
def sample_conversation_metrics():
    """Sample conversation metrics for testing."""
    return ConversationMetrics(
        session_id="session_123",
        conversation_length=4,
        duration_seconds=120.5,
        quality_score=0.85,
        customer_satisfaction=0.8,
        intent_distribution={"PRODUCT_INQUIRY": 1},
        tool_usage={"search_products": 1},
        sentiment_trend=["NEUTRAL", "POSITIVE"]
    )


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'}):
        yield


@pytest.fixture
def sample_tool_result():
    """Sample tool result for testing."""
    return ToolResult(
        tool_name="search_products",
        success=True,
        data={"products": ["boots", "tent"]},
        execution_time=0.1
    )
