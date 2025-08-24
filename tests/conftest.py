"""
Pytest configuration and fixtures for Sierra Agent tests.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sierra_agent.core.conversation import Conversation
from sierra_agent.data.data_types import Order, Product


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("sierra_agent.ai.llm_client.openai.OpenAI") as mock_client:
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        yield mock_client


@pytest.fixture
def sample_product():
    """Sample product for testing."""
    return Product(
        product_name="Test Hiking Boots",
        sku="TEST001",
        inventory=10,
        description="Test hiking boots for testing",
        tags=["test", "hiking", "boots"],
    )


@pytest.fixture
def sample_order():
    """Sample order for testing."""
    return Order(
        customer_name="Test Customer",
        email="test@example.com",
        order_number="#W001",
        products_ordered=["TEST001"],
        status="Processing",
        tracking_number="TRK123456789",
    )


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing."""
    conversation = Conversation()
    conversation.add_user_message("Hello, I need help with hiking boots")
    conversation.add_ai_message("I'd be happy to help you find hiking boots!")
    return conversation


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        yield
