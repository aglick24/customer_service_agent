"""
Sierra Agent - Simplified Core Agent Implementation

Clean, strongly typed agent using the evolving planning system.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from sierra_agent.ai.llm_service import LLMService
from sierra_agent.core.adaptive_planning_service import AdaptivePlanningService
from sierra_agent.core.conversation import Conversation
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the Sierra Agent."""
    quality_check_interval: int = 3
    analytics_update_interval: int = 5
    max_conversation_length: int = 50
    enable_quality_monitoring: bool = True
    enable_analytics: bool = True
    # LLM Configuration
    thinking_model: str = "gpt-4o"
    low_latency_model: str = "gpt-4o-mini"
    enable_dual_llm: bool = True


class SierraAgent:
    """Simplified AI Agent using evolving plan system."""

    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        self.config = config or AgentConfig()
        
        # Initialize LLM service first
        self.llm_service = LLMService(
            thinking_model=self.config.thinking_model,
            low_latency_model=self.config.low_latency_model
        )
        
        # Core components with LLM service dependency
        self.conversation = Conversation()
        self.tool_orchestrator = ToolOrchestrator()
        self.planning_service = AdaptivePlanningService(llm_service=self.llm_service)
        
        # Session management
        self.session_id: Optional[str] = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0

        logger.info("SierraAgent initialized with evolving planning system")

    def start_conversation(self) -> str:
        """Start a new conversation session."""
        self.session_id = f"session_{int(time.time())}"
        self.interaction_count = 0
        self.conversation.clear_conversation()
        self.conversation.add_system_message(f"Session {self.session_id} started")
        
        logger.info(f"Started conversation session {self.session_id}")
        return self.session_id

    def process_user_input(self, user_input: str) -> str:
        """Process user input using the evolving plan system."""
        try:
            # Add user message to conversation
            self.conversation.add_user_message(user_input)
            self.interaction_count += 1
            
            # Process input through adaptive planning service
            plan, response = self.planning_service.process_user_input(
                self.session_id or "default", 
                user_input, 
                self.tool_orchestrator
            )
            
            # Display plan status
            plan.print_plan()
            
            # Ensure we have a valid response
            final_response = response or "I apologize, but I wasn't able to process your request properly."
            
            # Add AI response to conversation
            self.conversation.add_ai_message(final_response)
            
            # Periodic maintenance
            self._perform_periodic_checks()
            
            return final_response

        except Exception as e:
            logger.exception(f"Error processing user input: {e}")
            fallback_response = "I'm experiencing some technical difficulties right now. Please try again in a moment."
            self.conversation.add_ai_message(fallback_response)
            return fallback_response

    def _perform_periodic_checks(self) -> None:
        """Perform periodic quality checks and analytics updates."""
        if (self.config.enable_quality_monitoring and 
            self.interaction_count % self.config.quality_check_interval == 0):
            self._check_conversation_quality()

        if (self.config.enable_analytics and 
            self.interaction_count % self.config.analytics_update_interval == 0):
            self._update_analytics()

    def _check_conversation_quality(self) -> None:
        """Simple conversation quality check."""
        try:
            quality_score = 0.8  # Simplified mock score
            self.conversation.update_quality_score(quality_score)
            self.last_quality_check = self.interaction_count
        except Exception as e:
            logger.exception(f"Error during quality check: {e}")

    def _update_analytics(self) -> None:
        """Simple analytics update."""
        try:
            if self.session_id:
                self.last_analytics_update = self.interaction_count
        except Exception as e:
            logger.exception(f"Error updating analytics: {e}")

    def get_llm_status(self) -> Dict[str, Any]:
        """Get the status of unified LLM service."""
        return self.llm_service.get_agent_statistics()

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        try:
            return {
                "session_id": self.session_id,
                "interaction_count": self.interaction_count,
                "conversation_length": self.conversation.get_conversation_length(),
                "conversation_duration": self.conversation.get_conversation_duration(),
                "quality_score": self.conversation.quality_score,
                "conversation_phase": self.conversation.conversation_state.conversation_phase,
                "urgency_level": self.conversation.conversation_state.urgency_level,
                "last_quality_check": self.last_quality_check,
                "last_analytics_update": self.last_analytics_update,
            }
        except Exception as e:
            logger.exception(f"Error generating summary: {e}")
            return {"error": str(e)}

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the agent."""
        try:
            return {
                "llm_status": self.get_llm_status(),
                "planning_stats": {"active_plans": len(self.planning_service.active_plans)},
                "tool_stats": self.tool_orchestrator.get_tool_execution_stats(),
                "conversation_summary": self.get_conversation_summary(),
                "configuration": {
                    "quality_check_interval": self.config.quality_check_interval,
                    "analytics_update_interval": self.config.analytics_update_interval,
                    "max_conversation_length": self.config.max_conversation_length,
                    "enable_quality_monitoring": self.config.enable_quality_monitoring,
                    "enable_analytics": self.config.enable_analytics,
                    "thinking_model": self.config.thinking_model,
                    "low_latency_model": self.config.low_latency_model,
                    "enable_dual_llm": self.config.enable_dual_llm,
                },
            }
        except Exception as e:
            logger.exception(f"Error generating statistics: {e}")
            return {"error": str(e)}

    def reset_conversation(self) -> None:
        """Reset the conversation and start fresh."""
        self.conversation.clear_conversation()
        self.session_id = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0
        
        # Clean up completed plans
        self.planning_service.cleanup_completed_plans()
        
        logger.info("Conversation reset")

    def end_conversation(self) -> None:
        """End the current conversation and finalize analytics."""
        try:
            if self.config.enable_quality_monitoring:
                self._check_conversation_quality()

            if self.config.enable_analytics:
                self._update_analytics()

            # Clean up plans
            self.planning_service.cleanup_completed_plans()

        except Exception as e:
            logger.exception(f"Error ending conversation: {e}")