"""Clean Data Types for Sierra Agent

Basic business data types only - no planning types to avoid circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


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


# Business data types for tools
BusinessData = Union[Order, Product, List[Product], Promotion, Dict[str, Any]]


@dataclass
class ToolResult:
    """Strongly typed container for tool execution results."""
    data: Optional[BusinessData] = None
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert ToolResult to dictionary format."""
        if not self.success:
            return {
                "success": False,
                "error": self.error,
                "data": None
            }
        
        # Handle different data types consistently
        serialized_data = None  # Initialize to satisfy mypy
        
        if self.data is None:
            serialized_data = None
        elif hasattr(self.data, "to_dict"):
            serialized_data = self.data.to_dict()
        elif isinstance(self.data, list):
            serialized_data = [
                item.to_dict() if hasattr(item, "to_dict") else item
                for item in self.data
            ]
        elif isinstance(self.data, dict):
            serialized_data = self.data

        return {
            "success": True,
            "error": None,
            "data": serialized_data
        }

    def serialize_for_context(self) -> str:
        """Format result data for LLM context."""
        if not self.success:
            return f"Error: {self.error or 'Unknown error'}"
        if not self.data:
            return "No data available"
            
        if isinstance(self.data, Order):
            return self._format_order(self.data)
        elif isinstance(self.data, list) and self.data and isinstance(self.data[0], Product):
            return self._format_product_list(self.data)
        elif isinstance(self.data, Product):
            return self._format_product(self.data)
        elif isinstance(self.data, Promotion):
            return self._format_promotion(self.data)
        elif isinstance(self.data, dict):
            return self._format_dict(self.data)
        else:
            return str(self.data)[:500]
    
    def _format_order(self, order: Order) -> str:
        products = "\n".join(f"    - {sku}" for sku in order.products_ordered)
        
        # Generate full tracking URL if tracking number is available
        tracking_info = "Not available"
        if order.tracking_number:
            tracking_url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={order.tracking_number}"
            tracking_info = f"{order.tracking_number} - Track at: {tracking_url}"
        
        return f"""Order Details:
  Order Number: {order.order_number}
  Customer: {order.customer_name}
  Status: {order.status}
  Products Ordered:
{products}
  Tracking: {tracking_info}"""
    
    def _format_product_list(self, products: List[Product]) -> str:
        items = [f"- {p.product_name} ({p.sku}): {p.description}" for p in products[:5]]
        result = "Products Found:\n" + "\n".join(items)
        if len(products) > 5:
            result += f"\n(Showing 5 of {len(products)} products)"
        return result
    
    def _format_product(self, product: Product) -> str:
        return f"""{product.product_name} ({product.sku})
Description: {product.description}
Inventory: {product.inventory}"""
    
    def _format_promotion(self, promotion: Promotion) -> str:
        return f"""{promotion.name}
Discount: {promotion.discount_percentage}%
Code: {promotion.discount_code}
Valid: {promotion.valid_hours}"""
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary data for LLM context, with special handling for known structures."""
        # Special handling for Early Risers promotion results
        if "available" in data and "message" in data:
            status = "Available" if data.get("available") else "Not Currently Available"
            message = data.get("message", "")
            result = f"Early Risers Promotion Status: {status}"
            if message:
                result += f"\nDetails: {message}"
            return result
        
        # General dictionary formatting
        formatted_items = []
        for key, value in data.items():
            # Convert keys to title case for readability
            display_key = key.replace("_", " ").title()
            formatted_items.append(f"{display_key}: {value}")
        
        return "\n".join(formatted_items)