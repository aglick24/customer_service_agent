"""
LLM Service - Consolidated LLM Interface

This module provides a unified, strongly-typed interface for all LLM interactions,
replacing the scattered LLM calls throughout the codebase with a clean service layer.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .context_builder import (
    ContextBuilder,
    LLMPromptBuilder,
)
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

class LLMService:
    """Consolidated LLM service with unified context handling."""

    def __init__(self, thinking_model: str = "gpt-4o", low_latency_model: str = "gpt-4o-mini"):
        """Initialize LLM service with context builder and clients."""
        self.context_builder = ContextBuilder()
        self.prompt_builder = LLMPromptBuilder()
        self.thinking_client = LLMClient(model_name=thinking_model, max_tokens=2000)
        self.low_latency_client = LLMClient(model_name=low_latency_model, max_tokens=1000)

        logger.info("LLMService initialized with unified context system")

    def generate_customer_service_response(
        self,
        user_input: str,
        tool_results: Optional[List] = None,
        plan_context=None,
        use_thinking_model: bool = False
    ) -> str:
        """Generate customer service response using unified context system."""
        try:
            context = self.context_builder.build_customer_service_context(
                user_input=user_input,
                tool_results=tool_results or [],
                plan_context=plan_context
            )

            prompt_str = self.prompt_builder.build_customer_service_prompt(context)
            from sierra_agent.ai.prompt_types import Prompt
            # Put the customer request in the user message, not system prompt
            user_message = f"Customer says: \"{user_input}\""
            prompt = Prompt(system_prompt=prompt_str, user_message=user_message, temperature=0.7)
            client = self.thinking_client if use_thinking_model else self.low_latency_client
            
            return client.call_llm(prompt)

        except Exception as e:
            logger.exception(f"Error generating customer service response: {e}")
            return self._get_fallback_customer_service_response(user_input)

    def _get_fallback_customer_service_response(self, user_input: str) -> str:
        """Generate fallback response when LLM fails."""
        return """I'm experiencing some technical difficulties right now, but I'm here to help!

🏔️ At Sierra Outfitters, we're committed to making sure you get the support you need for your outdoor adventures.

For immediate assistance, please try again in a moment, or feel free to reach out to our customer service team directly.

Thank you for your patience!

- Sierra Outfitters Customer Service Team"""

    def _get_fallback_planning_suggestions(self, _user_input: str, _available_data=None) -> List[str]:
        """Generate context-aware fallback planning suggestions."""
        return []

    def analyze_vague_request_and_suggest(self, user_input: str, plan_context, available_tools: Optional[List[str]] = None, tool_orchestrator=None) -> List[str]:
        """Use LLM to analyze requests and suggest the right sequence of actions."""
        try:
            # Get available tools dynamically from tool orchestrator
            if tool_orchestrator and hasattr(tool_orchestrator, 'get_available_tools'):
                tools_list = tool_orchestrator.get_available_tools()
                # Get tool descriptions for better LLM understanding
                tools_description = tool_orchestrator.get_tools_for_llm_planning() if hasattr(tool_orchestrator, 'get_tools_for_llm_planning') else None
            else:
                tools_list = available_tools or [
                    "get_order_status", "get_product_info", "browse_catalog",
                    "get_recommendations", "get_early_risers_promotion",
                    "get_company_info"  # Removed get_contact_info and get_policies - not needed for assignment
                ]
                tools_description = None
            
            # Use the new consolidated prompt template with dynamic tool descriptions
            prompt = self.prompt_builder.build_vague_request_analysis_prompt(
                plan_context=plan_context, 
                user_input=user_input, 
                available_tools=tools_list, 
                tools_description=tools_description
            )
            
            response = self.low_latency_client.call_llm(prompt)
            
            try:
                # With structured output, response should already be parsed JSON
                if isinstance(response, dict):
                    suggestions = response
                else:
                    # Fallback to JSON parsing if needed
                    suggestions = json.loads(response.strip())
                
                # Extract action from structured response
                if isinstance(suggestions, dict) and "action" in suggestions:
                    action_value = suggestions["action"]
                    if "," in action_value:
                        # Multiple comma-separated tools
                        return [tool.strip() for tool in action_value.split(",")]
                    else:
                        # Single action
                        return [action_value]
                
                logger.warning(f"LLM returned unexpected response format: {response}")
                return self._get_fallback_planning_suggestions(user_input, None)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse LLM response as JSON: {response}")
                return self._get_fallback_planning_suggestions(user_input, None)
                
        except Exception as e:
            logger.exception(f"Error in vague request analysis: {e}")
            return self._get_fallback_planning_suggestions(user_input, None)

    def validate_tool_addressed_request(self, user_request: str, tool_executed: str, tool_result_summary: str, plan_context) -> Dict[str, Any]:
        """Use LLM to check if the executed tool actually addressed what the user asked for."""
        try:
            # Use the new consolidated prompt template
            prompt = self.prompt_builder.build_tool_validation_prompt(user_request, tool_executed, tool_result_summary, plan_context)
            
            response = self.low_latency_client.call_llm(prompt)
            
            # Parse JSON response
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError:
                logger.warning(f"Could not parse validation response: {response}")
                return {"addressed": True, "reason": "Unable to validate", "missing_request": None}
                
        except Exception as e:
            logger.exception(f"Error in tool validation: {e}")
            return {"addressed": True, "reason": "Validation error", "missing_request": None}

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get LLM service statistics."""
        return {
            "llm_status": "operational" if self.thinking_client.client else "no_api_key",
            "thinking_model": self.thinking_client.model_name,
            "low_latency_model": self.low_latency_client.model_name,
            "context_builder_initialized": self.context_builder is not None,
            "prompt_builder_initialized": self.prompt_builder is not None,
        }