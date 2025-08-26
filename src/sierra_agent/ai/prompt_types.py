"""
Prompt Types for System/User Message Structure

This module defines the Prompt class that separates system prompts from user messages,
following LLM best practices and enabling proper JSON response formatting.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Prompt:
    """
    A structured prompt with separate system and user messages.
    
    This follows LLM best practices by clearly separating:
    - System prompt: Instructions, context, output format
    - User message: The actual user input or specific request
    """
    system_prompt: str
    user_message: str
    expected_json_schema: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    use_structured_output: bool = False
    
    def to_messages(self) -> list:
        """Convert to messages format for LLM API."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_message}
        ]
    
    def get_schema_description(self) -> str:
        """Get a human-readable description of expected JSON schema."""
        if not self.expected_json_schema:
            return ""
        
        schema_parts = []
        for key, value in self.expected_json_schema.items():
            if isinstance(value, dict) and "type" in value:
                schema_parts.append(f'"{key}": {value["type"]}')
            else:
                schema_parts.append(f'"{key}": "{value}"')
        
        return "{\n  " + ",\n  ".join(schema_parts) + "\n}"