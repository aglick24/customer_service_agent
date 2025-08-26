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
    sentiment_history: List[str] = field(default_factory=list)
    last_interaction: Optional[datetime] = None

    def update_sentiment(self, sentiment: str) -> None:
        """Update customer sentiment history."""
        self.sentiment_history.append(sentiment)
        self.last_interaction = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert customer context to dictionary format."""
        return {
            "customer_id": self.customer_id,
            "preferences": self.preferences,
            "conversation_topics": self.conversation_topics,
            "sentiment_history": self.sentiment_history,
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

        logger.info("New conversation initialized")

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        message = Message(
            content=content, message_type=MessageType.USER, timestamp=datetime.now()
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
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

    def add_system_message(self, content: str) -> None:
        """Add a system message to the conversation."""

        message = Message(
            content=content, message_type=MessageType.SYSTEM, timestamp=datetime.now()
        )
        self.messages.append(message)
        self.last_activity = datetime.now()

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


    def get_conversation_length(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)


    def get_conversation_duration(self) -> float:
        """Get conversation duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


    def clear_conversation(self) -> None:
        """Clear the conversation and reset state."""

        self.messages.clear()
        self.quality_score = None
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.customer_context = CustomerContext()
        self.conversation_state = ConversationState()

        logger.info("Conversation cleared and reset")

