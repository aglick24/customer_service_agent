"""
Data Types and Enums

This module defines the core data types, enums, and data classes used
throughout the Sierra Outfitters customer service system.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


class IntentType(Enum):
    """Types of customer intents."""
    ORDER_STATUS = "ORDER_STATUS"
    PRODUCT_INQUIRY = "PRODUCT_INQUIRY"
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"
    COMPLAINT = "COMPLAINT"
    COMPLIMENT = "COMPLIMENT"
    RETURN_REQUEST = "RETURN_REQUEST"
    SHIPPING_INFO = "SHIPPING_INFO"
    PROMOTION_INQUIRY = "PROMOTION_INQUIRY"


class SentimentType(Enum):
    """Types of customer sentiment."""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class QualityLevel(Enum):
    """Quality assessment levels."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"


@dataclass
class Product:
    """Product information."""
    id: str
    name: str
    category: str
    price: float
    description: str
    availability: bool
    stock_quantity: int
    tags: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "description": self.description,
            "availability": self.availability,
            "stock_quantity": self.stock_quantity,
            "tags": self.tags,
            "image_url": self.image_url
        }


@dataclass
class Order:
    """Order information."""
    order_id: str
    customer_email: str
    customer_name: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    order_date: datetime
    estimated_delivery: Optional[datetime] = None
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary format."""
        return {
            "order_id": self.order_id,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "items": self.items,
            "total_amount": self.total_amount,
            "status": self.status,
            "order_date": self.order_date.isoformat(),
            "estimated_delivery": self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            "shipping_address": self.shipping_address,
            "tracking_number": self.tracking_number
        }


@dataclass
class Customer:
    """Customer information."""
    customer_id: str
    email: str
    name: str
    phone: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    order_history: List[str] = field(default_factory=list)  # Order IDs
    created_date: datetime = field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert customer to dictionary format."""
        return {
            "customer_id": self.customer_id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "preferences": self.preferences,
            "order_history": self.order_history,
            "created_date": self.created_date.isoformat(),
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None
        }


@dataclass
class QualityScore:
    """Quality assessment score."""
    overall_score: float
    relevance_score: float
    helpfulness_score: float
    engagement_score: float
    resolution_score: float
    sentiment_trajectory_score: float
    response_time_score: float
    tool_effectiveness_score: float
    quality_level: QualityLevel
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quality score to dictionary format."""
        return {
            "overall_score": self.overall_score,
            "relevance_score": self.relevance_score,
            "helpfulness_score": self.helpfulness_score,
            "engagement_score": self.engagement_score,
            "resolution_score": self.resolution_score,
            "sentiment_trajectory_score": self.sentiment_trajectory_score,
            "response_time_score": self.response_time_score,
            "tool_effectiveness_score": self.tool_effectiveness_score,
            "quality_level": self.quality_level.value,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ConversationMetrics:
    """Conversation performance metrics."""
    session_id: str
    conversation_length: int
    duration_seconds: float
    quality_score: Optional[float]
    customer_satisfaction: float
    intent_distribution: Dict[str, int]
    tool_usage: Dict[str, int]
    sentiment_trend: List[str]  # Will store sentiment values as strings
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "session_id": self.session_id,
            "conversation_length": self.conversation_length,
            "duration_seconds": self.duration_seconds,
            "quality_score": self.quality_score,
            "customer_satisfaction": self.customer_satisfaction,
            "intent_distribution": self.intent_distribution,
            "tool_usage": self.tool_usage,
            "sentiment_trend": self.sentiment_trend,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ToolResult:
    """Result from executing a business tool."""
    tool_name: str
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool result to dictionary format."""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


@dataclass
class BusinessRule:
    """Business rule for decision making."""
    rule_id: str
    rule_name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int = 1
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert business rule to dictionary format."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "description": self.description,
            "conditions": self.conditions,
            "actions": self.actions,
            "priority": self.priority,
            "is_active": self.is_active
        }


# Utility functions for data validation and conversion
def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_order_id(order_id: str) -> bool:
    """Validate order ID format."""
    return len(order_id) >= 8 and len(order_id) <= 12 and order_id.isalnum()


def sanitize_input(text: str) -> str:
    """Sanitize user input text."""
    import html
    return html.escape(text.strip())


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.2f}"


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
