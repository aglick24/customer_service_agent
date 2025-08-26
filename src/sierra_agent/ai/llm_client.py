"""
LLM Client - OpenAI API Integration

This module provides the interface to OpenAI's language models for intent
classification, sentiment analysis, and response generation with usage tracking.
"""

import logging
import os
from typing import Optional, Dict, List, Union

from dotenv import load_dotenv
from openai import OpenAI
from .prompt_types import Prompt

load_dotenv()
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
            try:
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                self.api_key = None
                self.client = None
        else:
            self.client = None

        logger.info(f"LLMClient initialized with model {model_name}")

    def call_llm(self, prompt: Prompt) -> str:
        """Make a direct API call to OpenAI - pure interface."""
        if not self.api_key:
            msg = "OpenAI API key is required"
            raise ValueError(msg)

        if not self.client:
            msg = "OpenAI client not initialized"
            raise ValueError(msg)

        messages = prompt.to_messages()
        temp = prompt.temperature

        try:
            # Build request parameters
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": temp,
            }
            
            # Call OpenAI API with specific parameter passing to satisfy mypy
            if prompt.use_structured_output and prompt.expected_json_schema:
                # With structured output
                response_format_dict = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "response",
                        "schema": prompt.expected_json_schema
                    }
                }
                # Pass each argument explicitly to satisfy mypy type checking  
                response = self.client.chat.completions.create(  # type: ignore[call-overload]
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.max_tokens, 
                    temperature=temp,
                    response_format=response_format_dict
                )
            else:
                # Without structured output
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=temp
                )

            content = response.choices[0].message.content
            if not content:
                msg = "Empty response from OpenAI"
                raise ValueError(msg)

            return content.strip()

        except Exception as e:
            logger.exception(f"OpenAI API error: {e}")
            raise
