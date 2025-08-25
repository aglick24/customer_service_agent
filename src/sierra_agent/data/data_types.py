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

    def get_products(self, data_provider) -> List["Product"]:
        """Get full product objects for this order."""
        products = []
        for sku in self.products_ordered:
            product = data_provider.get_product_by_sku(sku)
            if product:
                products.append(product)
        return products
    
    def get_products_summary(self, data_provider) -> str:
        """Get a formatted summary of products in this order."""
        products = self.get_products(data_provider)
        if not products:
            return "Product details not available"
        
        summaries = []
        for product in products:
            summaries.append(f"    - {product.product_name} ({product.sku})")
        
        return "\n".join(summaries)

    def get_tracking_url(self) -> Optional[str]:
        """Generate tracking URL if tracking number exists."""
        if self.tracking_number:
            return f"https://tools.usps.com/go/TrackConfirmAction?tLabels={self.tracking_number}"
        return None

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
    customer_request: str
    steps: List[PlanStep]
    conversation_context: Dict[str, Any] = field(default_factory=dict)  # Structured planning + execution context
    current_step_index: int = 0
    status: PlanStatus = PlanStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
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
        # Show conversation context summary instead of intent
        planning_context = self.conversation_context.get("planning", {})
        if planning_context:
            print(f"   Context: {planning_context.get('conversation_phase', 'unknown')} | {planning_context.get('current_topic', 'general')}")
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


@dataclass
class Promotion:
    """Promotion information."""
    name: str
    discount_percentage: int
    valid_hours: str
    discount_code: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "discount_percentage": self.discount_percentage,
            "valid_hours": self.valid_hours,
            "discount_code": self.discount_code,
            "description": self.description,
        }


@dataclass
class ToolResult:
    """Simple, standardized container for tool results."""
    data: Any = None
    success: bool = True
    error: Optional[str] = None
    
    # Clean result container - no continuation cruft

    def to_dict(self) -> Dict[str, Any]:
        """Standardized serialization for all tool results."""
        if not self.success:
            return {
                "success": False,
                "error": self.error,
                "data": None
            }

        # Handle different data types consistently
        if hasattr(self.data, "to_dict"):
            serialized_data = self.data.to_dict()
        elif isinstance(self.data, list):
            serialized_data = [
                item.to_dict() if hasattr(item, "to_dict") else item
                for item in self.data
            ]
        elif isinstance(self.data, dict):
            serialized_data = self.data
        else:
            serialized_data = self.data

        return {
            "success": True,
            "error": None,
            "data": serialized_data
        }

    def serialize_for_context(self) -> str:
        """Serialize ToolResult data for LLM context with intelligent formatting and error handling."""
        try:
            if not self.success:
                return f"Error: {self.error or 'Unknown error'}"

            if not self.data:
                return "No data available"

            # Handle specific business object types with rich formatting
            if isinstance(self.data, Order):
                return self._format_order_for_context(self.data)
            if isinstance(self.data, list):
                # Handle empty lists appropriately
                if len(self.data) == 0:
                    return "No results found"
                # Handle non-empty lists
                # Check if it's a list of Products
                if all(isinstance(item, Product) for item in self.data):
                    return self._format_products_for_context(self.data)
                # Handle mixed or unknown list types
                return self._format_mixed_list_for_context(self.data)
            if isinstance(self.data, Product):
                return self._format_product_for_context(self.data)
            if isinstance(self.data, Promotion):
                return self._format_promotion_for_context(self.data)
            if isinstance(self.data, dict):
                return self._format_dict_for_context(self.data)
            # Fallback for any other data types
            return self._safe_str_conversion(self.data)

        except Exception as e:
            # Robust error handling to prevent serialization crashes
            return f"Serialization error: {str(e)[:100]}... (Data type: {type(self.data).__name__})"

    def _format_order_for_context(self, order: "Order") -> str:
        """Format Order object for LLM context with enriched product details."""
        # Build detailed product information for ordered items
        product_details = []
        for sku in order.products_ordered:
            # For now, format with SKU - this could be enhanced with full product lookup
            product_details.append(f"    - {sku}")
        
        products_formatted = "\n".join(product_details) if product_details else "    - No products listed"
        
        return f"""Order Details:
  Order Number: {order.order_number}
  Customer: {order.customer_name}
  Status: {order.status}
  Products Ordered:
{products_formatted}
  Tracking: {order.tracking_number or 'Not available'}
  Tracking URL: {order.get_tracking_url() or 'Not available'}"""

    def _format_products_for_context(self, products: List["Product"]) -> str:
        """Format Product list for LLM context with better user feedback."""
        if not products:
            return "No products found"

        # Show more products but with smart truncation
        display_limit = 5
        formatted_products = []
        
        for product in products[:display_limit]:
            formatted_products.append(f"- {product.product_name} ({product.sku}): {product.description}")

        result = "Products Found:\n" + "\n".join(formatted_products)
        
        if len(products) > display_limit:
            remaining = len(products) - display_limit
            result += f"\n\n(Showing {display_limit} of {len(products)} products. {remaining} additional products available - ask me to show more or refine your search for better results.)"
        
        return result

    def _format_product_for_context(self, product: "Product") -> str:
        """Format single Product for LLM context."""
        return f"""Product Details:
  Name: {product.product_name}
  SKU: {product.sku}
  Description: {product.description}
  Inventory: {product.inventory}
  Categories: {', '.join(product.tags)}"""

    def _format_promotion_for_context(self, promotion: "Promotion") -> str:
        """Format Promotion for LLM context."""
        return f"""Promotion Details:
  Name: {promotion.name}
  Discount: {promotion.discount_percentage}%
  Code: {promotion.discount_code}
  Valid: {promotion.valid_hours}
  Description: {promotion.description}"""

    def _format_dict_for_context(self, data: Dict[str, Any]) -> str:
        """Format dictionary data for LLM context."""
        formatted_items = []
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 3:
                formatted_items.append(f"  {key}: {value[:3]} (and {len(value)-3} more)")
            else:
                formatted_items.append(f"  {key}: {value}")

        return "\n".join(formatted_items)

    def _format_mixed_list_for_context(self, data_list: List[Any]) -> str:
        """Format mixed-type list for LLM context."""
        try:
            if not data_list:
                return "Empty list"

            formatted_items = []
            for i, item in enumerate(data_list[:5]):  # Limit to 5 items
                if hasattr(item, "to_dict"):
                    formatted_items.append(f"Item {i+1}: {item.to_dict()}")
                elif isinstance(item, dict):
                    formatted_items.append(f"Item {i+1}: {item}")
                else:
                    formatted_items.append(f"Item {i+1}: {str(item)[:50]}")

            suffix = f" (and {len(data_list) - 5} more items)" if len(data_list) > 5 else ""
            return "List Items:\n" + "\n".join(formatted_items) + suffix

        except Exception:
            return f"Mixed list with {len(data_list)} items (formatting error)"

    def _safe_str_conversion(self, data: Any) -> str:
        """Safely convert any data to string for context."""
        try:
            str_data = str(data)
            # Truncate very long strings
            if len(str_data) > 500:
                return str_data[:500] + "... (truncated)"
            return str_data
        except Exception:
            return f"Data of type {type(data).__name__} (conversion error)"
