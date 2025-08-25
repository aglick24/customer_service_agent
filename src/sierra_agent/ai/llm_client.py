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

# IntentType removed - using simple strings for request types

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)




class LLMClient:
    """Pure OpenAI API client - handles only API communication."""

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

        logger.info(f"LLMClient initialized with model {model_name}")


    def call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Make a direct API call to OpenAI - pure interface."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        if not self.client:
            raise ValueError("OpenAI client not initialized")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            return content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the given context."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required for response generation")

        try:
            response = self._generate_response_with_openai(context)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e

    def _generate_response_with_openai(self, context: Dict[str, Any]) -> str:
        """Generate response using OpenAI API."""
        try:
            if not self.client:
                raise ValueError("OpenAI client not initialized")

            # Build simple prompt from context
            prompt = self._build_simple_prompt(context)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            return content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _build_simple_prompt(self, context: Dict[str, Any]) -> str:
        """Build a simple, effective prompt from context."""
        user_input = context.get("user_input", "")
        customer_request = context.get("customer_request", user_input)
        primary_tool_result = context.get("primary_tool_result")
        
        # Simple data formatting
        if primary_tool_result and primary_tool_result.success:
            # Use the data directly without complex serialization
            data = primary_tool_result.data
            if hasattr(data, '__dict__'):
                formatted_data = str(data.__dict__)
            elif isinstance(data, (list, dict)):
                formatted_data = str(data)
            else:
                formatted_data = str(data)
        else:
            formatted_data = "No data available"

        prompt = f"""You are a helpful customer service agent for Sierra Outfitters, a premium outdoor gear retailer.

Customer's message: "{customer_request}"

Business data:
{formatted_data}

Provide a helpful, professional response using the business data above. Sign as "Sierra Outfitters Customer Service Team"."""

        return prompt
