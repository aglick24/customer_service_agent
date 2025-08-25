"""
Conversation Management Module

This module handles conversation state, message history, and customer context
for the Sierra Outfitters AI agent system.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sierra_agent.data.data_types import ToolResult

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages in a conversation."""

    USER = "user"
    AI = "ai"
    SYSTEM = "system"

@dataclass
class Message:
    """Represents a single message in the conversation."""

    content: str
    message_type: MessageType
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_results: Optional[List[ToolResult]] = None  # Business data associated with this message
    intent: Optional[str] = None  # Intent detected for this message
    plan_id: Optional[str] = None  # Plan that generated this message (for AI messages)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tool_results": [tr.to_dict() for tr in self.tool_results] if self.tool_results else None,
            "intent": self.intent,
            "plan_id": self.plan_id,
        }

@dataclass
class CustomerContext:
    """Customer context and preferences."""

    customer_id: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_topics: List[str] = field(default_factory=list)
    sentiment_history: List[str] = field(default_factory=list) # Changed from SentimentType to str
    # Removed intent_history - no longer using IntentType
    last_interaction: Optional[datetime] = None

    def update_sentiment(self, sentiment: str) -> None: # Changed from SentimentType to str
        """Update customer sentiment history."""

        self.sentiment_history.append(sentiment)
        self.last_interaction = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert customer context to dictionary format."""
        return {
            "customer_id": self.customer_id,
            "preferences": self.preferences,
            "conversation_topics": self.conversation_topics,
            "sentiment_history": self.sentiment_history, # Changed from SentimentType to str
            # Removed intent_history - no longer tracking intents
            "last_interaction": self.last_interaction.isoformat()
            if self.last_interaction
            else None,
        }

@dataclass
class ConversationState:
    """Current state of the conversation."""

    current_topic: str = "general"
    urgency_level: str = "normal"
    satisfaction_level: Optional[float] = None
    conversation_phase: str = "greeting"
    pending_inputs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation state to dictionary format."""
        return {
            "current_topic": self.current_topic,
            "urgency_level": self.urgency_level,
            "satisfaction_level": self.satisfaction_level,
            "conversation_phase": self.conversation_phase,
            "pending_inputs": self.pending_inputs,
        }

class Conversation:
    """Manages conversation state and message history."""

    def __init__(self) -> None:

        self.messages: List[Message] = []
        self.customer_context = CustomerContext()
        self.conversation_state = ConversationState()
        self.quality_score: Optional[float] = None
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.context_storage: Dict[str, Any] = {}  # Add explicit context storage

        logger.info("New conversation initialized")

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""

        message = Message(
            content=content, message_type=MessageType.USER, timestamp=datetime.now()
        )
        self.messages.append(message)
        self.last_activity = datetime.now()

        # Update conversation state based on content
        self._update_conversation_state(content)

    def add_ai_message(self, content: str) -> None:
        """Add an AI message to the conversation."""

        message = Message(
            content=content, message_type=MessageType.AI, timestamp=datetime.now()
        )
        self.messages.append(message)
        self.last_activity = datetime.now()

        # Update conversation phase
        self._update_conversation_phase()

    def add_ai_message_with_results(self, content: str, tool_results: List[ToolResult], intent: Optional[str] = None, plan_id: Optional[str] = None) -> None:
        """Add an AI message with associated tool results and metadata."""

        message = Message(
            content=content,
            message_type=MessageType.AI,
            timestamp=datetime.now(),
            tool_results=tool_results,
            intent=intent,
            plan_id=plan_id
        )
        self.messages.append(message)
        self.last_activity = datetime.now()

        # Update conversation phase
        self._update_conversation_phase()

    def get_previous_tool_results(self, result_type: type, limit: int = 3) -> List[ToolResult]:
        """Get previous tool results of specific type (Order, Product, etc.)."""

        found_results = []
        # Look through messages in reverse order (most recent first)
        for message in reversed(self.messages):
            if message.tool_results:
                for tool_result in message.tool_results:
                    if tool_result.success and isinstance(tool_result.data, result_type):
                        found_results.append(tool_result)
                        if len(found_results) >= limit:
                            break
            if len(found_results) >= limit:
                break

        return found_results

    def get_recent_messages_with_tool_results(self, limit: int = 2) -> List[Message]:
        """Get recent messages that have tool results (for context building)."""

        messages_with_results = []
        # Look through messages in reverse order
        for message in reversed(self.messages):
            if message.tool_results and message.message_type == MessageType.AI:
                messages_with_results.append(message)
                if len(messages_with_results) >= limit:
                    break

        # Return in chronological order
        messages_with_results.reverse()

        return messages_with_results

    def build_conversational_context(self, current_tool_results: List[ToolResult], intent: str) -> str:
        """Build conversational context including current and recent tool results."""

        context_parts = []

        # Get recent messages with tool results (limit to 3 previous messages for better context)
        recent_messages = self.get_recent_messages_with_tool_results(limit=3)

        if recent_messages:
            context_parts.append("PREVIOUS INTERACTIONS:")
            for i, message in enumerate(recent_messages, 1):
                # Format the tool results from the previous message
                if message.tool_results:
                    context_parts.append(f"Interaction {i}:")
                    for tool_result in message.tool_results:
                        formatted_result = tool_result.serialize_for_context()
                        context_parts.append(f"  {formatted_result}")
                    context_parts.append("")  # Add separator between interactions

        # Add current tool results
        if current_tool_results:
            context_parts.append("CURRENT REQUEST DATA:")
            for tool_result in current_tool_results:
                formatted_result = tool_result.serialize_for_context()
                context_parts.append(formatted_result)

        return "\n".join(context_parts)


    def add_system_message(self, content: str) -> None:
        """Add a system message to the conversation."""

        message = Message(
            content=content, message_type=MessageType.SYSTEM, timestamp=datetime.now()
        )
        self.messages.append(message)
        self.last_activity = datetime.now()

    def update_customer_sentiment(self, sentiment: str) -> None: # Changed from SentimentType to str
        """Update customer sentiment."""

        self.customer_context.update_sentiment(sentiment)

        # Update conversation state based on sentiment
        if sentiment == "negative": # Changed from SentimentType to str
            self.conversation_state.urgency_level = "high"

        elif sentiment == "positive": # Changed from SentimentType to str
            self.conversation_state.urgency_level = "normal"
            self.conversation_state.satisfaction_level = 0.8

    def update_quality_score(self, score: float) -> None:
        """Update conversation quality score."""

        self.quality_score = score

    def _update_conversation_state(self, content: str) -> None:
        """Update conversation state based on message content."""

        content_lower = content.lower()

        # Topic detection
        if any(word in content_lower for word in ["order", "tracking", "shipping"]):
            self.conversation_state.current_topic = "order_management"

        elif any(
            word in content_lower
            for word in ["product", "gear", "boots", "tent", "hiking"]
        ):
            self.conversation_state.current_topic = "product_inquiry"

        elif any(
            word in content_lower for word in ["return", "refund", "complaint", "issue"]
        ):
            self.conversation_state.current_topic = "customer_service"

        # Urgency detection
        if any(
            word in content_lower
            for word in ["urgent", "asap", "emergency", "problem", "broken"]
        ):
            self.conversation_state.urgency_level = "high"

    def _update_conversation_phase(self) -> None:
        """Update conversation phase based on message count."""

        message_count = len(self.messages)

        if message_count <= 2:
            self.conversation_state.conversation_phase = "greeting"

        elif message_count <= 6:
            self.conversation_state.conversation_phase = "exploration"

        elif message_count <= 10:
            self.conversation_state.conversation_phase = "resolution"

        else:
            self.conversation_state.conversation_phase = "closing"

    def get_message_history(self, limit: Optional[int] = None) -> List[Message]:
        """Get message history, optionally limited."""

        return self.messages if limit is None else self.messages[-limit:]


    def get_user_messages(self) -> List[Message]:
        """Get all user messages."""

        return [
            msg for msg in self.messages if msg.message_type == MessageType.USER
        ]


    def get_ai_messages(self) -> List[Message]:
        """Get all AI messages."""

        return [
            msg for msg in self.messages if msg.message_type == MessageType.AI
        ]


    def get_system_messages(self) -> List[Message]:
        """Get all system messages."""

        return [
            msg for msg in self.messages if msg.message_type == MessageType.SYSTEM
        ]


    def get_conversation_length(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)


    def get_conversation_duration(self) -> float:
        """Get conversation duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


    def get_customer_sentiment_trend(self) -> List[str]: # Changed from SentimentType to str
        """Get customer sentiment trend."""
        return self.customer_context.sentiment_history


    def get_conversation_patterns(self) -> Dict[str, Any]:
        """Get conversation patterns and statistics."""

        return {
            "message_count": len(self.messages),
            "user_message_count": len(self.get_user_messages()),
            "ai_message_count": len(self.get_ai_messages()),
            "system_message_count": len(self.get_system_messages()),
            "conversation_duration": self.get_conversation_duration(),
            "conversation_phase": self.conversation_state.conversation_phase,
            "urgency_level": self.conversation_state.urgency_level,
            "current_topic": self.conversation_state.current_topic,
            "quality_score": self.quality_score,
        }


    def clear_conversation(self) -> None:
        """Clear the conversation and reset state."""

        self.messages.clear()
        self.quality_score = None
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.customer_context = CustomerContext()
        self.conversation_state = ConversationState()

        logger.info("Conversation cleared and reset")

    def get_available_data(self) -> Dict[str, Any]:
        """Get all data available from previous tool results and context storage."""

        available = {}

        # First check context storage if it exists
        if hasattr(self, "context_storage") and self.context_storage:
            available.update(self.context_storage)

        # Get recent tool results from messages (for backwards compatibility)
        for message in reversed(self.messages):
            if message.tool_results:
                for tool_result in message.tool_results:
                    if tool_result.success and tool_result.data:
                        data_type = type(tool_result.data).__name__
                        if data_type == "Order" and "current_order" not in available:
                            available["current_order"] = tool_result.data

                        elif data_type == "list" and tool_result.data and "recent_products" not in available:
                            # Check if it's products
                            if isinstance(tool_result.data, list) and tool_result.data and hasattr(tool_result.data[0], "product_name"):
                                available["recent_products"] = tool_result.data

        return available

    def export_conversation(self) -> Dict[str, Any]:
        """Export conversation data for analysis."""

        return {
            "conversation_id": f"conv_{int(self.start_time.timestamp())}",
            "start_time": self.start_time.isoformat(),
            "end_time": self.last_activity.isoformat(),
            "duration": self.get_conversation_duration(),
            "message_count": len(self.messages),
            "quality_score": self.quality_score,
            "customer_context": self.customer_context.to_dict(),
            "conversation_state": self.conversation_state.to_dict(),
            "messages": [msg.to_dict() for msg in self.messages],
        }

