"""
LLM Client - OpenAI API Integration

This module provides the interface to OpenAI's language models for intent
classification, sentiment analysis, and response generation with usage tracking.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

from ..data.data_types import (
    IntentType,
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)




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


    def _build_response_prompt(self, context: Dict[str, Any]) -> str:
        """Build a prompt for response generation from ToolResult context."""
        print("📝 [LLM_CLIENT] Building response prompt from ToolResult context...")

        user_input = context.get("user_input", "")
        customer_request = context.get("customer_request", user_input)
        intent = context.get("intent", "customer_service")
        primary_tool_result = context.get("primary_tool_result")  # Main ToolResult
        conversational_context = context.get("conversational_context", "")  # Rich conversation context

        print(f"📝 [LLM_CLIENT] Primary tool result available: {primary_tool_result is not None}")

        # Check for errors and format the business data
        has_error = False
        formatted_data = ""

        if primary_tool_result:
            if not primary_tool_result.success:
                has_error = True
                formatted_data = primary_tool_result.error
                print("📝 [LLM_CLIENT] Error detected in primary tool result")
            else:
                # Use the intelligent serialization method
                try:
                    formatted_data = primary_tool_result.serialize_for_context()
                    print(f"📝 [LLM_CLIENT] Formatted business data: {len(formatted_data)} characters")
                except Exception as e:
                    print(f"❌ [LLM_CLIENT] Error formatting tool result: {e}")
                    formatted_data = f"Data formatting error: {e!s}"
                    has_error = True
        else:
            has_error = True
            formatted_data = "No business data available"
            print("📝 [LLM_CLIENT] No primary tool result available")

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
            # NEW: Use conversational context if available, otherwise use formatted data
            context_data = conversational_context if conversational_context else formatted_data

            prompt = f"""You are a helpful customer service agent for Sierra Outfitters, a premium outdoor gear retailer.

Customer's message: "{customer_request}"

CONVERSATION CONTEXT:
{context_data}

INSTRUCTIONS:
- You have access to current and previous conversation data above
- Use this information to provide a specific, helpful response that references relevant context
- If you see previous interactions, acknowledge them naturally ("As I mentioned earlier..." or "Following up on your order...")
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
