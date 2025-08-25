"""
LLM Service - Consolidated LLM Interface

This module provides a unified, strongly-typed interface for all LLM interactions,
replacing the scattered LLM calls throughout the codebase with a clean service layer.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .context_builder import (
    ContextBuilder, 
    LLMPromptBuilder,
    CustomerServiceContext,
    PlanningContext, 
    PlanUpdateContext,
    ContextType
)
from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class LLMService:
    """Consolidated LLM service with unified context handling."""
    
    def __init__(self, thinking_model: str = "gpt-4o", low_latency_model: str = "gpt-4o-mini"):
        """Initialize LLM service with context builder and clients."""
        print("🤖 [LLM_SERVICE] Initializing consolidated LLM service...")
        
        # Initialize context building components
        self.context_builder = ContextBuilder()
        self.prompt_builder = LLMPromptBuilder()
        
        # Initialize LLM clients
        self.thinking_client = LLMClient(model_name=thinking_model, max_tokens=2000)
        self.low_latency_client = LLMClient(model_name=low_latency_model, max_tokens=1000)
        
        print(f"🤖 [LLM_SERVICE] Initialized with thinking model: {thinking_model}, low-latency model: {low_latency_model}")
        logger.info("LLMService initialized with unified context system")
    
    def generate_customer_service_response(
        self,
        user_input: str,
        tool_results: List = None,
        request_type: str = "general",
        conversation_phase: str = "greeting",
        customer_sentiment: str = "neutral",
        conversation_context=None,
        use_thinking_model: bool = False
    ) -> str:
        """Generate customer service response using unified context system."""
        print(f"🎯 [LLM_SERVICE] Generating customer service response: {request_type}")
        
        try:
            # Build strongly-typed context
            context = self.context_builder.build_customer_service_context(
                user_input=user_input,
                tool_results=tool_results or [],
                request_type=request_type,
                conversation_phase=conversation_phase,
                customer_sentiment=customer_sentiment,
                conversation_context=conversation_context
            )
            
            # Build prompt from context
            prompt = self.prompt_builder.build_customer_service_prompt(context)
            
            # Choose appropriate LLM client
            client = self.thinking_client if use_thinking_model else self.low_latency_client
            model_type = "thinking" if use_thinking_model else "low-latency"
            
            print(f"🎯 [LLM_SERVICE] Using {model_type} model for customer service response")
            
            # Generate response
            response = client.call_llm(prompt, temperature=0.7)
            
            print(f"✅ [LLM_SERVICE] Generated customer service response ({len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"Error generating customer service response: {e}")
            print(f"❌ [LLM_SERVICE] Error generating response: {e}")
            return self._get_fallback_customer_service_response(user_input)
    
    def generate_planning_suggestions(
        self,
        user_input: str,
        available_data: Dict[str, Any] = None,
        available_tools: List[str] = None,
        conversation_phase: str = "greeting",
        current_topic: str = "general",
        max_steps: int = 5,
        conversation_context=None
    ) -> List[str]:
        """Generate intelligent planning suggestions using unified context system."""
        print(f"🧠 [LLM_SERVICE] Generating planning suggestions for: '{user_input[:30]}...'")
        
        try:
            # Build strongly-typed planning context
            context = self.context_builder.build_planning_context(
                user_input=user_input,
                available_data=available_data or {},
                available_tools=available_tools or [],
                conversation_phase=conversation_phase,
                current_topic=current_topic,
                max_steps=max_steps,
                conversation_context=conversation_context
            )
            
            # Build planning prompt
            prompt = self.prompt_builder.build_planning_prompt(context)
            
            # Use thinking model for complex planning decisions
            print("🧠 [LLM_SERVICE] Using thinking model for planning")
            response = self.thinking_client.call_llm(prompt, temperature=0.3)
            
            # Parse JSON response
            suggested_tools = self._parse_json_tool_list(response)
            
            # Validate tools are available
            validated_tools = self._validate_suggested_tools(suggested_tools, available_tools or [])
            
            print(f"✅ [LLM_SERVICE] Generated {len(validated_tools)} validated planning suggestions: {validated_tools}")
            return validated_tools
            
        except Exception as e:
            logger.error(f"Error generating planning suggestions: {e}")
            print(f"❌ [LLM_SERVICE] Error in planning: {e}")
            return self._get_fallback_planning_suggestions(user_input, available_data)
    
    def update_plan_suggestions(
        self,
        user_input: str,
        original_plan,
        execution_results: List,
        remaining_steps: List[str] = None,
        available_tools: List[str] = None
    ) -> List[str]:
        """Generate plan update suggestions using unified context system."""
        print(f"🔄 [LLM_SERVICE] Generating plan update suggestions for plan: {original_plan.plan_id}")
        
        try:
            # Build strongly-typed plan update context
            context = self.context_builder.build_plan_update_context(
                user_input=user_input,
                original_plan=original_plan,
                execution_results=execution_results,
                remaining_steps=remaining_steps or [],
                available_tools=available_tools or []
            )
            
            # Build plan update prompt
            prompt = self.prompt_builder.build_plan_update_prompt(context)
            
            # Use low-latency model for quick plan updates
            print("🔄 [LLM_SERVICE] Using low-latency model for plan updates")
            response = self.low_latency_client.call_llm(prompt, temperature=0.3)
            
            # Parse JSON response
            suggested_tools = self._parse_json_tool_list(response)
            
            # Validate tools are available
            validated_tools = self._validate_suggested_tools(suggested_tools, available_tools or [])
            
            print(f"✅ [LLM_SERVICE] Generated {len(validated_tools)} plan update suggestions: {validated_tools}")
            return validated_tools
            
        except Exception as e:
            logger.error(f"Error generating plan update suggestions: {e}")
            print(f"❌ [LLM_SERVICE] Error in plan update: {e}")
            return []  # Conservative fallback - no additional steps
    
    def _parse_json_tool_list(self, response: str) -> List[str]:
        """Parse JSON tool list from LLM response."""
        print("🔍 [LLM_SERVICE] Parsing JSON tool list from LLM response")
        
        try:
            # Look for JSON array pattern
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                json_str = '[' + json_match.group(1) + ']'
                tools = json.loads(json_str)
                
                # Ensure all items are strings
                string_tools = [str(tool).strip('"\'') for tool in tools if tool]
                print(f"🔍 [LLM_SERVICE] Successfully parsed {len(string_tools)} tools from JSON")
                return string_tools
            else:
                print("⚠️ [LLM_SERVICE] No JSON array found in response")
                return []
                
        except json.JSONDecodeError as e:
            print(f"⚠️ [LLM_SERVICE] JSON parsing error: {e}")
            # Try to extract tool names from text
            return self._extract_tools_from_text(response)
        except Exception as e:
            print(f"❌ [LLM_SERVICE] Unexpected error parsing tools: {e}")
            return []
    
    def _extract_tools_from_text(self, response: str) -> List[str]:
        """Extract tool names from text response as fallback."""
        print("🔍 [LLM_SERVICE] Attempting to extract tools from text response")
        
        known_tools = [
            "get_order_status", "search_products", "get_product_details",
            "get_product_recommendations", "get_early_risers_promotion",
            "get_company_info", "get_contact_info", "get_policies"
        ]
        
        found_tools = []
        response_lower = response.lower()
        
        for tool in known_tools:
            if tool in response_lower:
                found_tools.append(tool)
        
        print(f"🔍 [LLM_SERVICE] Extracted {len(found_tools)} tools from text: {found_tools}")
        return found_tools
    
    def _validate_suggested_tools(self, suggested_tools: List[str], available_tools: List[str]) -> List[str]:
        """Validate that suggested tools are actually available."""
        if not available_tools:
            # If no available tools list provided, trust the suggestions
            return suggested_tools
        
        validated = [tool for tool in suggested_tools if tool in available_tools]
        
        if len(validated) != len(suggested_tools):
            invalid_tools = [tool for tool in suggested_tools if tool not in available_tools]
            print(f"⚠️ [LLM_SERVICE] Filtered out invalid tools: {invalid_tools}")
        
        return validated
    
    def _get_fallback_customer_service_response(self, user_input: str) -> str:
        """Generate fallback response when LLM fails."""
        print("🔄 [LLM_SERVICE] Generating fallback customer service response")
        
        return """I'm experiencing some technical difficulties right now, but I'm here to help! 
        
Could you please rephrase your question or provide more specific details about what you're looking for? 
I can assist with:
- Order status and tracking
- Product recommendations and details  
- Promotions and discounts
- General customer service questions

Thank you for your patience!

- Sierra Outfitters Customer Service Team"""
    
    def _get_fallback_planning_suggestions(self, user_input: str, available_data: Dict[str, Any] = None) -> List[str]:
        """Generate rule-based planning suggestions as fallback."""
        print("🔄 [LLM_SERVICE] Generating fallback planning suggestions")
        
        user_lower = user_input.lower()
        suggestions = []
        
        # Simple rule-based fallback logic
        if any(word in user_lower for word in ["order", "track", "delivery", "shipping"]):
            if not (available_data and "current_order" in available_data):
                suggestions.append("get_order_status")
        
        elif any(word in user_lower for word in ["product", "recommend", "looking for", "search"]):
            suggestions.append("search_products")
        
        elif any(word in user_lower for word in ["promotion", "discount", "code", "sale"]):
            suggestions.append("get_early_risers_promotion")
        
        else:
            suggestions.append("get_company_info")
        
        print(f"🔄 [LLM_SERVICE] Generated {len(suggestions)} fallback suggestions: {suggestions}")
        return suggestions
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of the LLM service."""
        return {
            "service_name": "LLMService",
            "thinking_model": self.thinking_client.model_name,
            "low_latency_model": self.low_latency_client.model_name,
            "context_builder_initialized": self.context_builder is not None,
            "prompt_builder_initialized": self.prompt_builder is not None,
            "clients_available": {
                "thinking": self.thinking_client.client is not None,
                "low_latency": self.low_latency_client.client is not None
            }
        }