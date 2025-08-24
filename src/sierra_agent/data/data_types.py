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
    AVERAGE = "AVERAGE"
    BELOW_AVERAGE = "BELOW_AVERAGE"
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
    metrics: Dict[str, float] = field(default_factory=dict)
    
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
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics
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
    # Additional fields for analytics
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    message_count: Optional[int] = None
    user_message_count: Optional[int] = None
    ai_message_count: Optional[int] = None
    conversation_phase: Optional[str] = None
    urgency_level: Optional[str] = None
    current_topic: Optional[str] = None
    resolution_status: Optional[str] = None
    
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
            "timestamp": self.timestamp.isoformat(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "message_count": self.message_count,
            "user_message_count": self.user_message_count,
            "ai_message_count": self.ai_message_count,
            "conversation_phase": self.conversation_phase,
            "urgency_level": self.urgency_level,
            "current_topic": self.current_topic,
            "resolution_status": self.resolution_status
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


class PlanStatus(Enum):
    """Status of a plan execution."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PlanStepType(Enum):
    """Types of plan steps."""
    TOOL_EXECUTION = "TOOL_EXECUTION"
    CONDITIONAL_BRANCH = "CONDITIONAL_BRANCH"
    LOOP = "LOOP"
    USER_INTERACTION = "USER_INTERACTION"
    DATA_TRANSFORMATION = "DATA_TRANSFORMATION"
    VALIDATION = "VALIDATION"


class PlanPriority(Enum):
    """Priority levels for plan execution."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    step_id: str
    step_type: PlanStepType
    name: str
    description: str
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # List of step_ids this depends on
    conditions: Optional[Dict[str, Any]] = None  # Conditions for conditional execution
    max_retries: int = 3
    timeout_seconds: int = 30
    priority: PlanPriority = PlanPriority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan step to dictionary format."""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type.value,
            "name": self.name,
            "description": self.description,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "conditions": self.conditions,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "priority": self.priority.value,
            "metadata": self.metadata
        }


@dataclass
class Plan:
    """A complete execution plan for handling a customer request."""
    plan_id: str
    name: str
    description: str
    customer_request: str
    steps: List[PlanStep]
    estimated_duration: int = 0  # in seconds
    priority: PlanPriority = PlanPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    status: PlanStatus = PlanStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary format."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "customer_request": self.customer_request,
            "steps": [step.to_dict() for step in self.steps],
            "estimated_duration": self.estimated_duration,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata
        }


@dataclass
class ExecutionContext:
    """Context for plan execution."""
    plan_id: str
    session_id: str
    user_input: str
    conversation_history: List[Dict[str, Any]]
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    global_variables: Dict[str, Any] = field(default_factory=dict)
    execution_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution context to dictionary format."""
        return {
            "plan_id": self.plan_id,
            "session_id": self.session_id,
            "user_input": self.user_input,
            "conversation_history": self.conversation_history,
            "current_step": self.current_step,
            "step_results": self.step_results,
            "global_variables": self.global_variables,
            "execution_start": self.execution_start.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }


@dataclass
class PlanExecutionResult:
    """Result of plan execution."""
    plan_id: str
    success: bool
    completed_steps: List[str]
    failed_steps: List[str]
    total_duration: float
    final_output: Any
    error_message: Optional[str] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan execution result to dictionary format."""
        return {
            "plan_id": self.plan_id,
            "success": self.success,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "total_duration": self.total_duration,
            "final_output": self.final_output,
            "error_message": self.error_message,
            "execution_log": self.execution_log,
            "metadata": self.metadata
        }


@dataclass
class PlanningRequest:
    """Request for creating a plan."""
    customer_input: str
    conversation_context: Dict[str, Any]
    available_tools: List[str]
    business_rules: List[BusinessRule]
    customer_profile: Optional[Customer] = None
    urgency_level: str = "NORMAL"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert planning request to dictionary format."""
        return {
            "customer_input": self.customer_input,
            "conversation_context": self.conversation_context,
            "available_tools": self.available_tools,
            "business_rules": [rule.to_dict() for rule in self.business_rules],
            "customer_profile": self.customer_profile.to_dict() if self.customer_profile else None,
            "urgency_level": self.urgency_level
        }
