"""
LLM Client - OpenAI API Integration

This module provides the interface to OpenAI's language models for intent
classification, sentiment analysis, and response generation with usage tracking.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

from ..data.data_types import (
    IntentType,
    PlanStep,
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Track API usage and costs."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    api_calls: int = 0

    def update_from_response(self, response: Dict[str, Any]) -> None:
        """Update stats from API response."""
        usage = response.get("usage", {})
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        self.api_calls += 1

        # Estimate cost (approximate rates for GPT-4)
        cost_per_1k_tokens = 0.03  # $0.03 per 1K tokens (approximate)
        self.total_cost += (total_tokens / 1000) * cost_per_1k_tokens


class LLMClient:
    """Client for interacting with OpenAI's language models."""

    def __init__(self, model_name: str = "gpt-4o", max_tokens: int = 1000) -> None:

        self.model_name = model_name
        self.max_tokens = max_tokens

        # Get API key from environment
        self.api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.client: Optional[OpenAI] = None

        if self.api_key:
            print("✅ [LLM_CLIENT] OpenAI API key found")
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("✅ [LLM_CLIENT] OpenAI client configured")
            except ImportError:
                self.api_key = None
                self.client = None
        else:
            self.client = None

        # Initialize usage tracking
        self.usage_stats: Dict[str, Any] = {
            "total_requests": 0,
            "total_tokens": 0,
            "requests_by_model": {},
            "last_request": None,
        }
        logger.info(f"LLMClient initialized with model {model_name}")

    def classify_intent(self, user_input: str) -> IntentType:
        """Classify the user's intent from their input."""

        try:
            if self.api_key:
                intent = self._classify_intent_with_openai(user_input)
            else:
                intent = self._classify_intent_mock(user_input)

            self._update_usage_stats("intent_classification")
            return intent

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")

            # Fallback to mock classification
            return self._classify_intent_mock(user_input)

    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the given context."""

        if not self.api_key:
            raise ValueError("OpenAI API key is required for response generation")

        try:
            response = self._generate_response_with_openai(context)
            self._update_usage_stats("response_generation")
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e

    def _classify_intent_with_openai(self, user_input: str) -> IntentType:
        """Classify intent using OpenAI API."""

        try:
            if not self.client:
                raise ValueError("OpenAI client not initialized")

            prompt = f"""
            Classify the customer's intent from the following message. Choose from these categories:
            - ORDER_STATUS: Questions about order tracking, shipping, delivery
            - PRODUCT_INQUIRY: Questions about products, recommendations, availability
            - CUSTOMER_SERVICE: General customer service, policies, company info
            - COMPLAINT: Complaints, issues, problems
            - RETURN_REQUEST: Returns, refunds, exchanges
            - SHIPPING_INFO: Shipping options, costs, tracking
            - PROMOTION_INQUIRY: Sales, discounts, promotions
            
            Customer message: "{user_input}"
            
            Respond with only the intent category (e.g., ORDER_STATUS):
            """

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            intent_text = content.strip().upper()

            # Map response to IntentType
            intent_mapping = {
                "ORDER_STATUS": IntentType.ORDER_STATUS,
                "PRODUCT_INQUIRY": IntentType.PRODUCT_INQUIRY,
                "CUSTOMER_SERVICE": IntentType.CUSTOMER_SERVICE,
                "COMPLAINT": IntentType.COMPLAINT,
                "RETURN_REQUEST": IntentType.RETURN_REQUEST,
                "SHIPPING_INFO": IntentType.SHIPPING_INFO,
                "PROMOTION_INQUIRY": IntentType.PROMOTION_INQUIRY,
            }

            if intent_text in intent_mapping:
                return intent_mapping[intent_text]
            return IntentType.CUSTOMER_SERVICE

        except Exception as e:
            print(f"❌ [LLM_CLIENT] OpenAI API error: {e}")
            raise

    def _classify_intent_mock(self, user_input: str) -> IntentType:
        """Mock intent classification for testing."""

        user_input_lower = user_input.lower()

        # Simple keyword-based classification
        if any(
            word in user_input_lower
            for word in ["order", "tracking", "shipping", "delivery"]
        ):
            intent = IntentType.ORDER_STATUS
        elif any(
            word in user_input_lower
            for word in ["product", "hiking", "camping", "boots", "tent", "backpack"]
        ):
            intent = IntentType.PRODUCT_INQUIRY
        elif any(word in user_input_lower for word in ["return", "refund", "exchange"]):
            intent = IntentType.RETURN_REQUEST
        elif any(
            word in user_input_lower
            for word in ["complaint", "problem", "issue", "broken", "wrong"]
        ):
            intent = IntentType.COMPLAINT
        elif any(
            word in user_input_lower for word in ["shipping", "delivery", "tracking"]
        ):
            intent = IntentType.SHIPPING_INFO
        elif any(
            word in user_input_lower
            for word in ["sale", "discount", "promotion", "deal"]
        ):
            intent = IntentType.PROMOTION_INQUIRY
        else:
            intent = IntentType.CUSTOMER_SERVICE

        return intent

    def _generate_response_with_openai(self, context: Dict[str, Any]) -> str:
        """Generate response using OpenAI API."""

        try:
            if not self.client:
                raise ValueError("OpenAI client not initialized")

            # Build prompt from context
            prompt = self._build_response_prompt(context)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            generated_response = content.strip()
            print(
                f"🌐 [LLM_CLIENT] OpenAI generated response: {len(generated_response)} characters"
            )

            return generated_response

        except Exception as e:
            print(f"❌ [LLM_CLIENT] OpenAI API error: {e}")
            raise

    def _generate_response_mock(self, context: Dict[str, Any]) -> str:
        """Mock response generation for testing."""
        print("🎭 [LLM_CLIENT] Performing mock response generation...")

        user_input = context.get("user_input", "")
        intent = context.get("intent", "customer_service")
        sentiment = context.get("sentiment", "neutral")

        print(
            f"🎭 [LLM_CLIENT] Mock context - Intent: {intent}, Sentiment: {sentiment}"
        )

        # Generate appropriate mock response based on intent
        if intent == "order_status":
            response = "I'd be happy to help you with your order. Could you please provide your order number?"
        elif intent == "product_inquiry":
            response = "I'd be happy to help you find the perfect outdoor gear. What are you looking for?"
        elif intent == "return_request":
            response = "I understand you'd like to make a return. Let me help you with that process."
        elif intent == "complaint":
            response = "I'm sorry to hear you're experiencing an issue. Let me help resolve this for you."
        elif intent == "shipping_info":
            response = (
                "I can help you with shipping information. What would you like to know?"
            )
        elif intent == "promotion_inquiry":
            response = "Great question about our promotions! Let me check what's currently available."
        else:
            response = "Thank you for contacting Sierra Outfitters. How can I assist you today?"

        # Adjust response based on sentiment
        if sentiment == "positive":
            response = "I'm glad to help! " + response
        elif sentiment == "negative":
            response = "I understand your concern. " + response

        print(
            f"🎭 [LLM_CLIENT] Mock response generated: '{response[:50]}{'...' if len(response) > 50 else ''}'"
        )
        return response

    def _build_response_prompt(self, context: Dict[str, Any]) -> str:
        """Build a prompt for response generation from context."""
        print("📝 [LLM_CLIENT] Building response prompt from context...")

        user_input = context.get("user_input", "")
        customer_request = context.get("customer_request", user_input)
        intent = context.get("intent", "customer_service")
        sentiment = context.get("sentiment", "neutral")
        tool_results = context.get("tool_results", {})
        plan_results = context.get("plan_results", [])
        conversation_history = context.get("conversation_history", [])

        # Use tool_results which contains the consolidated business data
        business_data = tool_results
        
        print(f"📝 [LLM_CLIENT] Business data available: {bool(business_data)}")
        if business_data:
            print(f"📝 [LLM_CLIENT] Business data keys: {list(business_data.keys()) if isinstance(business_data, dict) else 'Not a dict'}")

        # Check if there was an error in the business data
        has_error = False
        if isinstance(business_data, dict) and "error" in business_data:
            has_error = True
            print("📝 [LLM_CLIENT] Error detected in business data")

        # Format business data for better readability
        if isinstance(business_data, dict):
            formatted_data = "\n".join([f"  {key}: {value}" for key, value in business_data.items()])
        else:
            formatted_data = str(business_data)

        if has_error:
            prompt = f"""You are a helpful customer service agent for Sierra Outfitters, a premium outdoor gear retailer.

Customer's message: "{customer_request}"

SYSTEM RESPONSE:
{formatted_data}

INSTRUCTIONS:
- The system encountered an issue processing the customer's request (see above)
- If there's an error message, use it to provide a helpful response to the customer
- Be professional, friendly, and apologetic about any issues
- Offer alternative assistance or ask for clarification if needed
- Sign as "Sierra Outfitters Customer Service Team"

Please write a helpful response addressing the issue:"""
        else:
            prompt = f"""You are a helpful customer service agent for Sierra Outfitters, a premium outdoor gear retailer.

Customer's message: "{customer_request}"

BUSINESS DATA RETRIEVED:
{formatted_data}

INSTRUCTIONS:
- You have successfully retrieved the customer's information above
- Use this data to provide a specific, helpful response
- If order data is available (order_number, status, products, tracking), provide complete order details
- If promotion data is available (available, discount_code, message), explain the promotion status clearly
- Be professional, friendly, and specific
- Sign as "Sierra Outfitters Customer Service Team"
- Do NOT claim you don't have access to information when data is provided above

Please write a helpful response using the retrieved business data:"""

        print(f"📝 [LLM_CLIENT] Prompt built with {len(prompt)} characters")
        return prompt

    def _update_usage_stats(self, request_type: str) -> None:
        """Update usage statistics for a specific request type."""
        if request_type not in self.usage_stats["requests_by_model"]:
            self.usage_stats["requests_by_model"][request_type] = 0
        self.usage_stats["requests_by_model"][request_type] += 1
        self.usage_stats["last_request"] = datetime.now().isoformat()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        print("📊 [LLM_CLIENT] Retrieving usage statistics...")

        stats = self.usage_stats.copy()
        stats["model_name"] = self.model_name
        stats["max_tokens"] = self.max_tokens
        stats["has_api_key"] = bool(self.api_key)

        print(
            f"📊 [LLM_CLIENT] Usage stats retrieved: {stats['total_requests']} total requests"
        )
        return stats

    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        print("🔄 [LLM_CLIENT] Resetting usage statistics...")

        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "requests_by_model": {},
            "last_request": None,
        }

        print("✅ [LLM_CLIENT] Usage statistics reset")
