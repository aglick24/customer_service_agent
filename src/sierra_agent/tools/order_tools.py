"""
Order Management Tools

Extensible order-related tools that implement the BaseTool interface.
"""

import logging
from typing import List

from sierra_agent.data.data_provider import DataProvider
from sierra_agent.data.data_types import ToolResult
from sierra_agent.utils.branding import Branding

from .base_tool import BaseTool, ToolParameter

logger = logging.getLogger(__name__)


class OrderStatusTool(BaseTool):
    """Tool for looking up order status and tracking information."""
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
    
    @property
    def tool_name(self) -> str:
        return "get_order_status"
    
    @property
    def description(self) -> str:
        return "Look up order status, tracking information, and order details"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="email",
                param_type=str,
                required=True,
                description="Customer email address",
                validation_rules={"pattern": r".+@.+\..+", "min_length": 5}
            ),
            ToolParameter(
                name="order_number", 
                param_type=str,
                required=True,
                description="Order number (e.g., #W001)",
                validation_rules={"pattern": r"#?W\d+", "min_length": 2}
            ),
            ToolParameter(
                name="name",
                param_type=str,
                required=False,
                description="Customer name (optional, for verification)",
                validation_rules={"min_length": 2}
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute order status lookup."""
        email = kwargs["email"]
        order_number = kwargs["order_number"]
        name = kwargs.get("name")  # Optional parameter
        
        # Normalize order number format
        if not order_number.startswith("#"):
            order_number = f"#{order_number}"
        
        # Get order from data provider
        order = self.data_provider.get_order_status(email, order_number)
        
        if not order:
            return ToolResult(
                success=False,
                error=Branding.get_adventure_error_message("order_not_found"),
                data=None
            )
        
        return ToolResult(success=True, data=order, error=None)


# COMMENTED OUT - Not needed for assignment requirements
# class OrderHistoryTool(BaseTool):
#     """Tool for getting customer order history (extensible example)."""
#     
#     def __init__(self, data_provider: DataProvider):
#         self.data_provider = data_provider
#     
#     @property
#     def tool_name(self) -> str:
#         return "get_order_history"
#     
#     @property
#     def description(self) -> str:
#         return "Get customer's order history and purchase patterns"
#     
#     @property
#     def parameters(self) -> List[ToolParameter]:
#         return [
#             ToolParameter(
#                 name="email",
#                 param_type=str,
#                 required=True,
#                 description="Customer email address",
#                 validation_rules={"pattern": r".+@.+\..+"}
#             ),
#             ToolParameter(
#                 name="limit",
#                 param_type=int,
#                 required=False,
#                 description="Maximum number of orders to return",
#                 default=10,
#                 validation_rules={"min_value": 1, "max_value": 100}
#             )
#         ]
#     
#     def execute(self, **kwargs) -> ToolResult:
#         """Execute order history lookup."""
#         email = kwargs["email"]
#         _limit = kwargs.get("limit", 10)  # TODO: Implement actual limit functionality
#         
#         # This is where you'd implement order history logic
#         # For now, return a placeholder response
#         return ToolResult(
#             success=True,
#             data={
#                 "customer_email": email,
#                 "message": f"Order history feature coming soon! 🏔️ Will show last {_limit} orders.",
#                 "order_count": 0,
#                 "orders": []
#             },
#             error=None
#         )