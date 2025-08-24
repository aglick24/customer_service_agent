"""
Integration tests for the main agent system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sierra_agent.core.agent import SierraAgent, AgentConfig
from sierra_agent.data.data_types import IntentType, SentimentType


class TestAgentIntegration:
    """Test the main agent integration."""
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_agent_initialization(self, mock_openai):
        """Test that the agent initializes properly."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test agent initialization
        agent = SierraAgent()
        
        assert agent.session_id is None
        assert agent.interaction_count == 0
        assert agent.conversation is not None
        assert agent.tool_orchestrator is not None
        assert agent.quality_scorer is not None
        assert agent.analytics is not None
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_conversation_start(self, mock_openai):
        """Test starting a conversation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        session_id = agent.start_conversation()
        
        assert session_id is not None
        assert agent.session_id == session_id
        assert "session_" in session_id
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_process_user_input_basic(self, mock_openai):
        """Test basic user input processing."""
        # Mock OpenAI client for intent classification
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "PRODUCT_INQUIRY"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Process user input
        response = agent.process_user_input("I need help finding hiking boots")
        
        assert response is not None
        assert len(response) > 0
        assert agent.interaction_count == 1
        assert len(agent.conversation.messages) == 2  # User + AI message
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_agent_config_customization(self, mock_openai):
        """Test agent configuration customization."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create custom config
        config = AgentConfig(
            quality_check_interval=5,
            analytics_update_interval=10
        )
        
        agent = SierraAgent(config=config)
        
        assert agent.config.quality_check_interval == 5
        assert agent.config.analytics_update_interval == 10
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_conversation_summary(self, mock_openai):
        """Test conversation summary functionality."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Add some conversation
        agent.process_user_input("Hello")
        
        # Get summary
        summary = agent.get_conversation_summary()
        
        assert "session_id" in summary
        assert "interaction_count" in summary
        assert "conversation_length" in summary
        assert "conversation_duration" in summary
        assert summary["interaction_count"] == 1
        assert summary["conversation_length"] == 2
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_conversation_reset(self, mock_openai):
        """Test conversation reset functionality."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Add some conversation
        agent.process_user_input("Hello")
        initial_count = agent.interaction_count
        
        # Reset conversation
        agent.reset_conversation()
        
        assert agent.interaction_count == 0
        assert agent.session_id is None
        assert len(agent.conversation.messages) == 0
        assert agent.conversation.quality_score is None
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_agent_end_conversation(self, mock_openai):
        """Test ending a conversation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Add some conversation
        agent.process_user_input("Hello")
        
        # End conversation
        agent.end_conversation()
        
        # Verify analytics were updated
        assert len(agent.analytics.conversations) > 0


class TestAgentErrorHandling:
    """Test agent error handling."""
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_agent_initialization_without_api_key(self, mock_openai):
        """Test agent initialization without API key."""
        # Mock OpenAI client to raise error
        mock_openai.side_effect = ValueError("OpenAI API key is required")
        
        # The agent should still initialize since we're mocking the OpenAI client
        # The actual error would occur during LLM operations, not initialization
        agent = SierraAgent()
        assert agent is not None
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_process_user_input_with_llm_error(self, mock_openai):
        """Test handling of LLM errors during user input processing."""
        # Mock OpenAI client to raise error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Process user input should handle the error gracefully
        response = agent.process_user_input("Hello")
        
        assert response is not None
        # The response should be a normal greeting since the error is handled internally
        assert len(response) > 0


class TestAgentQualityMonitoring:
    """Test agent quality monitoring."""
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_quality_check_interval(self, mock_openai):
        """Test that quality checks happen at the specified interval."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create agent with custom quality check interval
        config = AgentConfig(quality_check_interval=2)
        agent = SierraAgent(config=config)
        agent.start_conversation()
        
        # First interaction - no quality check
        agent.process_user_input("First message")
        assert agent.conversation.quality_score is None
        
        # Second interaction - should trigger quality check
        agent.process_user_input("Second message")
        # Quality score should be set after quality check
        assert agent.conversation.quality_score is not None
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_analytics_update_interval(self, mock_openai):
        """Test that analytics updates happen at the specified interval."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "MOCK_RESPONSE"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create agent with custom analytics update interval
        config = AgentConfig(analytics_update_interval=3)
        agent = SierraAgent(config=config)
        agent.start_conversation()
        
        # First few interactions - no analytics update
        for i in range(2):
            agent.process_user_input(f"Message {i}")
        
        # Third interaction - should trigger analytics update
        agent.process_user_input("Third message")
        
        # Analytics should have been updated
        assert len(agent.analytics.conversations) > 0


class TestAgentToolIntegration:
    """Test agent integration with business tools."""
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_tool_execution_for_intent(self, mock_openai):
        """Test that tools are executed based on intent."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "ORDER_STATUS"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Process user input that should trigger order-related tools
        response = agent.process_user_input("Check my order ORD12345")
        
        assert response is not None
        # The response should include information from order tools
        assert agent.interaction_count == 1
    
    @patch('sierra_agent.ai.llm_client.openai.OpenAI')
    def test_tool_orchestrator_integration(self, mock_openai):
        """Test integration with tool orchestrator."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "PRODUCT_INQUIRY"
        mock_response.model_dump.return_value = {
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SierraAgent()
        agent.start_conversation()
        
        # Verify tool orchestrator is properly integrated
        assert agent.tool_orchestrator is not None
        assert hasattr(agent.tool_orchestrator, 'execute_tools_for_intent')
        
        # Check available tools
        available_tools = agent.tool_orchestrator.get_available_tools()
        assert len(available_tools) > 0
        assert "search_products" in available_tools
        assert "get_order_status" in available_tools
