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
        conversation_context=None,
        use_thinking_model: bool = False
    ) -> str:
        """Generate customer service response using unified context system."""
        try:
            context = self.context_builder.build_customer_service_context(
                user_input=user_input,
                tool_results=tool_results or [],
                conversation_context=conversation_context
            )

            prompt = self.prompt_builder.build_customer_service_prompt(context)
            client = self.thinking_client if use_thinking_model else self.low_latency_client
            return client.call_llm(prompt, temperature=0.7)

        except Exception as e:
            logger.exception(f"Error generating customer service response: {e}")
            return self._get_fallback_customer_service_response(user_input)

    def _get_fallback_customer_service_response(self, user_input: str) -> str:
        """Generate fallback response when LLM fails."""
        return """I'm experiencing some technical difficulties right now, but I'm here to help!

Could you please rephrase your question or provide more specific details about what you're looking for?
I can assist with:
- Order status and tracking
- Product recommendations and details
- Promotions and discounts
- General customer service questions

Thank you for your patience!

- Sierra Outfitters Customer Service Team"""

    def _get_fallback_planning_suggestions(self, _user_input: str, _available_data: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate context-aware fallback planning suggestions."""
        return []

    def analyze_vague_request_and_suggest(self, user_input: str, plan_context, available_tools: Optional[List[str]] = None, tool_orchestrator=None) -> List[str]:
        """Use LLM to analyze requests and suggest the right sequence of actions."""
        try:
            # Get available tools
            if tool_orchestrator and hasattr(tool_orchestrator, 'get_available_tools'):
                tools_list = tool_orchestrator.get_available_tools()
            else:
                tools_list = available_tools or [
                    "get_order_status", "get_product_info", "browse_catalog",
                    "get_recommendations", "get_early_risers_promotion",
                    "get_company_info", "get_contact_info", "get_policies"
                ]
            
            # Use the new consolidated prompt template
            prompt = self.prompt_builder.build_vague_request_analysis_prompt(plan_context, user_input, tools_list)
            
            response = self.low_latency_client.call_llm(prompt, temperature=0.1)
            
            import json
            try:
                suggestions = json.loads(response.strip())
                if isinstance(suggestions, list):
                    return suggestions
                else:
                    logger.warning(f"LLM returned non-list response: {response}")
                    return self._get_fallback_planning_suggestions(user_input, None)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse LLM response as JSON: {response}")
                return self._get_fallback_planning_suggestions(user_input, None)
                
        except Exception as e:
            logger.exception(f"Error in vague request analysis: {e}")
            return self._get_fallback_planning_suggestions(user_input, None)

    def validate_tool_addressed_request(self, user_request: str, tool_executed: str, tool_result_summary: str, plan_context) -> Dict[str, Any]:
                tool_descriptions = {
                    "get_order_status": "get_order_status(email, order_number) - Get order details, status, and tracking info",
                    "get_product_info": "get_product_info(product_identifier) - Get detailed product information by SKU or name",
                    "browse_catalog": "browse_catalog(search_query=None, category_filter=None) - Browse product catalog",
                    "get_recommendations": "get_recommendations(recommendation_type='general', reference_skus=None, activity_or_need=None) - Get personalized product recommendations",
                    "get_early_risers_promotion": "get_early_risers_promotion() - Check Early Risers promotion (8-10 AM PT)",
                    "get_company_info": "get_company_info() - Get Sierra Outfitters company information",
                    "get_contact_info": "get_contact_info() - Get contact details and social media",
                    "get_policies": "get_policies() - Get return, shipping, and warranty policies"
                }
                
                tools_description = "\n".join([
                    f"- {tool_descriptions.get(tool, tool)}" for tool in tools_list
                ])
            
            prompt = f"""You are an intelligent customer service workflow planner for Sierra Outfitters outdoor gear company. Your job is to analyze what the customer wants and determine the best response approach.

Customer Request: "{user_input}"
Available Context: {context_summary or "No context available"}{conversation_info}

Available Tools:
{tools_description}

STEP 1 - ANALYZE THE REQUEST TYPE:

A) CONVERSATIONAL REQUESTS (respond conversationally, no tools needed):
   - Greetings: "hello", "hi", "hey" (standalone, not followed by specific requests) → return "conversational_response"
   - Thanks: "thanks", "thank you" → return "conversational_response"  
   - General help: "I need help", "can you help" (without any context or specifics) → return "conversational_response"
   - General questions: "what can you do", "what services" → return "conversational_response"
   - IMPORTANT: If user provides email, order numbers, or specific product info, DO NOT treat as conversational

B) INFORMATION REQUESTS (use tools to get specific data):
   - Order questions: "my order", "order status", "track order" + email/order# → get_order_status
   - Product search: "show me", "what products", "looking for [product]" → search_products
   - Product details: "tell me about [specific product]" → search_products (then get_product_details if found)
   - Order product details: "products I ordered", "what did I order", "items in my order" (with order context) → get_product_details
   - Recommendations: "recommend", "suggest products" → get_product_recommendations
   - Promotions: "discount", "promotion", "deal", "early risers", "tell me about early risers" → get_early_risers_promotion
   - Company info: "about company", "contact" → get_company_info

C) MULTI-STEP REQUESTS (use multiple tools in sequence):
   - "check my order and give recommendations" → get_order_status,get_product_recommendations
   - "tell me about the products I ordered and give recommendations" → get_product_details,get_product_recommendations
   - "show me products and tell me about deals" → search_products,get_early_risers_promotion

STEP 2 - CHECK FOR MISSING INFORMATION:
   - For get_order_status(email, order_number): need email AND order number
   - For get_product_details(skus): need specific product SKUs (from order context or user)
   - For search_products(query): need search terms (product name, category, etc.)
   - For get_product_recommendations: can use order context or customer preferences
   - If missing required parameters: return "wait_for_missing_info"

STEP 3 - DETERMINE RESPONSE:
   - Conversational requests: return "conversational_response"
   - Single tool needed: return the tool name
   - Multiple tools needed: return comma-separated tool names
   - Missing info: return "wait_for_missing_info"

EXAMPLES:
- "hello" → "conversational_response"
- "thanks for your help" → "conversational_response"
- "I need help" (no context) → "conversational_response"
- "george.hill@example.com" (just email provided) → "wait_for_missing_info"
- "do you have promotions?" → "get_early_risers_promotion"
- "tell me about early risers" → "get_early_risers_promotion"
- "early risers discount" → "get_early_risers_promotion"
- "tell me about the backpack" → "search_products"
- "my order george.hill@example.com #W009" → "get_order_status"
- "tell me about my order" (no email/order#) → "wait_for_missing_info"
- "#W009" (with email in context) → "get_order_status"
- "give me recommendations based on my order" (with order in context) → "get_product_recommendations"
- "tell me about the products I ordered and give recommendations" → "get_product_details,get_product_recommendations"
- "I want" (incomplete) → "conversational_response"

Return only the response type or tool name(s), nothing else."""

            response = self.low_latency_client.call_llm(prompt, temperature=0.1)
            
            # Extract and parse actions from the response (handle comma-separated multiple actions)
            response = response.strip().strip('"').strip("'").lower()
            
            # Parse multiple actions if comma-separated
            if ',' in response:
                suggested_actions = [action.strip() for action in response.split(',')]
            else:
                suggested_actions = [response]
            
            # Handle special actions that aren't real tools
            if 'wait_for_missing_info' in suggested_actions:
                return ['wait_for_missing_info']
            
            if 'conversational_response' in suggested_actions:
                return ['conversational_response']
            
            # Validate all actions are real
            valid_actions = tools_list
            validated_actions = []
            
            for action in suggested_actions:
                if action in valid_actions:
                    validated_actions.append(action)
                else:
                    # Try to find action within longer text
                    found_action = None
                    for valid_action in valid_actions:
                        if valid_action in action:
                            found_action = valid_action
                            break
                    if found_action:
                        validated_actions.append(found_action)
            
            if validated_actions:
                return validated_actions
            else:
                # Fall back to context-aware suggestion
                return self._get_fallback_planning_suggestions(user_input, available_data)
                
        except Exception as e:
            logger.exception(f"Error in vague request analysis: {e}")
            return self._get_fallback_planning_suggestions(user_input, available_data)

    def validate_tool_addressed_request(self, user_request: str, tool_executed: str, tool_result_summary: str, conversation_context: Optional[str] = None) -> Dict[str, Any]:
        """Use LLM to check if the executed tool actually addressed what the user asked for."""
        try:
            context_info = f"\nConversation Context: {conversation_context}" if conversation_context else ""
            
            prompt = f"""Analyze if the executed tool properly addressed the user's request.

User Request: "{user_request}"
Tool Executed: {tool_executed}  
Tool Result: {tool_result_summary}{context_info}

Instructions:
1. Did the executed tool directly address what the user asked for?
2. If user asked about "order" but tool got "contact info", that's WRONG
3. If user provided order number but tool got "company info", that's WRONG  
4. If user asked for recommendations but tool got random products, that's WRONG

Respond with JSON:
{{"addressed": true/false, "reason": "explanation", "missing_request": "specific question to ask user or null"}}

Examples:
- User: "tell me about my order", Tool: "get_contact_info" → {{"addressed": false, "reason": "user wanted order info but got contact info", "missing_request": "I need your order number to look up your order."}}
- User: "george@email.com", Tool: "get_company_info" → {{"addressed": false, "reason": "user provided email for order lookup but got company info", "missing_request": "Great! I have your email. Now I need your order number."}}
- User: "#W006", Tool: "get_order_status" → {{"addressed": true, "reason": "order number provided and order lookup performed", "missing_request": null}}"""

            response = self.low_latency_client.call_llm(prompt, temperature=0.1)
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response.strip())
                return result
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                addressed = "true" in response.lower() and "false" not in response.lower()
                return {"addressed": addressed, "reason": "parsing failed", "missing": None}
                
        except Exception as e:
            logger.exception(f"Error validating tool request: {e}")
            return {"addressed": True, "reason": "validation failed", "missing": None}

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
