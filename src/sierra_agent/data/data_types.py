"""
Simple Data Types for Sierra Agent Chat Loop

Basic data types that match the JSON data structure for the three core features:
1. Order Status and Tracking
2. Product Recommendations  
3. Early Risers Promotion
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class IntentType(Enum):
    """Customer intent types for planning."""
    ORDER_STATUS = "ORDER_STATUS"
    PRODUCT_INQUIRY = "PRODUCT_INQUIRY"
    EARLY_RISERS_PROMOTION = "EARLY_RISERS_PROMOTION"
    GENERAL_INQUIRY = "GENERAL_INQUIRY"
    COMPLAINT = "COMPLAINT"
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"
    RETURN_REQUEST = "RETURN_REQUEST"
    SHIPPING_INFO = "SHIPPING_INFO"
    PROMOTION_INQUIRY = "PROMOTION_INQUIRY"


class PlanStatus(Enum):
    """Status of plan execution."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Product:
    """Product information matching the JSON structure."""
    product_name: str
    sku: str
    inventory: int
    description: str
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ProductName": self.product_name,
            "SKU": self.sku,
            "Inventory": self.inventory,
            "Description": self.description,
            "Tags": self.tags,
        }


@dataclass
class Order:
    """Order information matching the JSON structure."""
    customer_name: str
    email: str
    order_number: str
    products_ordered: List[str]
    status: str
    tracking_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CustomerName": self.customer_name,
            "Email": self.email,
            "OrderNumber": self.order_number,
            "ProductsOrdered": self.products_ordered,
            "Status": self.status,
            "TrackingNumber": self.tracking_number,
        }


@dataclass
class PlanStep:
    """A single step in a multi-turn plan."""
    step_id: str
    name: str
    description: str
    required_input: Optional[str] = None
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    is_completed: bool = False
    result: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "required_input": self.required_input,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "is_completed": self.is_completed,
            "result": self.result,
        }


@dataclass
class MultiTurnPlan:
    """A plan for multi-turn conversation execution."""
    plan_id: str
    intent: IntentType
    customer_request: str
    steps: List[PlanStep]
    current_step_index: int = 0
    status: PlanStatus = PlanStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    conversation_context: Dict[str, Any] = field(default_factory=dict)
    max_turns: int = 5
    current_turn: int = 1

    def get_current_step(self) -> Optional[PlanStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance_step(self) -> bool:
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return True
        return False

    def is_complete(self) -> bool:
        return all(step.is_completed for step in self.steps)

    def print_plan(self) -> None:
        """Print the plan in a readable format."""
        print(f"\n📋 Plan: {self.plan_id}")
        print(f"   Intent: {self.intent.value}")
        print(f"   Status: {self.status.value}")
        print(f"   Customer Request: {self.customer_request}")
        print(f"   Steps ({len(self.steps)}):")
        for i, step in enumerate(self.steps, 1):
            status = "✅" if step.is_completed else "⏳"
            print(f"      {i}. {status} {step.name}")
            print(f"         Tool: {step.tool_name}")
            print(f"         Description: {step.description}")
        print()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "intent": self.intent.value,
            "customer_request": self.customer_request,
            "steps": [step.to_dict() for step in self.steps],
            "current_step_index": self.current_step_index,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "conversation_context": self.conversation_context,
            "max_turns": self.max_turns,
            "current_turn": self.current_turn,
        }


@dataclass
class ConversationState:
    """State of the current conversation."""
    session_id: str
    active_plan: Optional[MultiTurnPlan] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    current_turn: int = 1
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        self.last_activity = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "active_plan": self.active_plan.to_dict() if self.active_plan else None,
            "conversation_history": self.conversation_history,
            "current_turn": self.current_turn,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }
