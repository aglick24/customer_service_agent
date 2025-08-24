"""
Business Tools

This module contains various business tools that provide access to business data
and operations for the Sierra Outfitters customer service system.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..data.data_types import Product, Order, Customer
from ..utils.branding import Branding

logger = logging.getLogger(__name__)


class BusinessTools:
    """Collection of business tools for customer service operations."""
    
    def __init__(self) -> None:
        print("🛠️ [BUSINESS_TOOLS] Initializing BusinessTools...")
        self._initialize_mock_data()
        print("🛠️ [BUSINESS_TOOLS] BusinessTools initialized successfully")
        logger.info("BusinessTools initialized with mock data")
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock data for testing and demonstration."""
        print("🛠️ [BUSINESS_TOOLS] Initializing mock data...")
        
        # Mock products
        self.mock_products = [
            Product(
                id="PROD001",
                name="Sierra Summit Hiking Boots",
                category="Hiking & Backpacking",
                price=129.99,
                description="Premium hiking boots with waterproof membrane",
                availability=True,
                stock_quantity=25,
                tags=["hiking", "boots", "waterproof", "premium"]
            ),
            Product(
                id="PROD002",
                name="Adventure Pro Tent",
                category="Camping & Outdoor Living",
                price=199.99,
                description="3-person tent with weather protection",
                availability=True,
                stock_quantity=15,
                tags=["camping", "tent", "3-person", "weatherproof"]
            ),
            Product(
                id="PROD003",
                name="Trail Master Backpack",
                category="Hiking & Backpacking",
                price=89.99,
                description="45L hiking backpack with hydration system",
                availability=True,
                stock_quantity=30,
                tags=["hiking", "backpack", "hydration", "45L"]
            )
        ]
        print(f"🛠️ [BUSINESS_TOOLS] Created {len(self.mock_products)} mock products")
        
        # Mock orders
        self.mock_orders = [
            Order(
                order_id="ORD12345",
                customer_email="john.doe@example.com",
                customer_name="John Doe",
                items=[{"product_id": "PROD001", "quantity": 1, "price": 129.99}],
                total_amount=129.99,
                status="Shipped",
                order_date=datetime.now() - timedelta(days=2),
                estimated_delivery=datetime.now() + timedelta(days=1),
                shipping_address="123 Main St, Anytown, USA",
                tracking_number="TRK789456123"
            ),
            Order(
                order_id="ORD12346",
                customer_email="jane.smith@example.com",
                customer_name="Jane Smith",
                items=[{"product_id": "PROD002", "quantity": 1, "price": 199.99}],
                total_amount=199.99,
                status="Processing",
                order_date=datetime.now() - timedelta(days=1),
                estimated_delivery=datetime.now() + timedelta(days=3)
            )
        ]
        print(f"🛠️ [BUSINESS_TOOLS] Created {len(self.mock_orders)} mock orders")
        
        # Mock customers
        self.mock_customers = [
            Customer(
                customer_id="CUST001",
                email="john.doe@example.com",
                name="John Doe",
                phone="555-0123",
                preferences={"category": "hiking", "size": "10"},
                order_history=["ORD12345"]
            ),
            Customer(
                customer_id="CUST002",
                email="jane.smith@example.com",
                name="Jane Smith",
                phone="555-0456",
                preferences={"category": "camping", "size": "8"},
                order_history=["ORD12346"]
            )
        ]
        print(f"🛠️ [BUSINESS_TOOLS] Created {len(self.mock_customers)} mock customers")
        
        print("🛠️ [BUSINESS_TOOLS] Mock data initialization complete")
    
    def get_order_status(self, user_input: str) -> Dict[str, Any]:
        """Get order status based on user input."""
        print(f"📦 [ORDER_STATUS] Processing order status request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        order_id = self._extract_order_id(user_input)
        if not order_id:
            print("❌ [ORDER_STATUS] No order ID found in user input")
            return {"error": "No order ID found. Please provide your order number."}
        
        print(f"📦 [ORDER_STATUS] Extracted order ID: {order_id}")
        
        order = self._find_order(order_id)
        if not order:
            print(f"❌ [ORDER_STATUS] Order {order_id} not found")
            return {"error": f"Order {order_id} not found. Please check your order number."}
        
        print(f"✅ [ORDER_STATUS] Found order {order_id} with status: {order.status}")
        
        result = {
            "order_id": order.order_id,
            "status": order.status,
            "customer_name": order.customer_name,
            "order_date": order.order_date.strftime("%Y-%m-%d"),
            "estimated_delivery": order.estimated_delivery.strftime("%Y-%m-%d") if order.estimated_delivery else "Not available",
            "tracking_number": order.tracking_number,
            "total_amount": order.total_amount
        }
        
        print(f"📦 [ORDER_STATUS] Returning order status: {result}")
        return result
    
    def get_order_details(self, user_input: str) -> Dict[str, Any]:
        """Get detailed order information."""
        print(f"📋 [ORDER_DETAILS] Processing order details request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        order_id = self._extract_order_id(user_input)
        if not order_id:
            print("❌ [ORDER_DETAILS] No order ID found in user input")
            return {"error": "No order ID found. Please provide your order number."}
        
        print(f"📋 [ORDER_DETAILS] Extracted order ID: {order_id}")
        
        order = self._find_order(order_id)
        if not order:
            print(f"❌ [ORDER_DETAILS] Order {order_id} not found")
            return {"error": f"Order {order_id} not found. Please check your order number."}
        
        print(f"✅ [ORDER_DETAILS] Found order {order_id}")
        
        result = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "items": order.items,
            "total_amount": order.total_amount,
            "status": order.status,
            "order_date": order.order_date.strftime("%Y-%m-%d"),
            "estimated_delivery": order.estimated_delivery.strftime("%Y-%m-%d") if order.estimated_delivery else "Not available",
            "shipping_address": order.shipping_address
        }
        
        print(f"📋 [ORDER_DETAILS] Returning order details: {len(result)} fields")
        return result
    
    def get_shipping_info(self, user_input: str) -> Dict[str, Any]:
        """Get shipping information for an order."""
        print(f"🚚 [SHIPPING_INFO] Processing shipping info request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        order_id = self._extract_order_id(user_input)
        if not order_id:
            print("❌ [SHIPPING_INFO] No order ID found in user input")
            return {"error": "No order ID found. Please provide your order number."}
        
        print(f"🚚 [SHIPPING_INFO] Extracted order ID: {order_id}")
        
        order = self._find_order(order_id)
        if not order:
            print(f"❌ [SHIPPING_INFO] Order {order_id} not found")
            return {"error": f"Order {order_id} not found. Please check your order number."}
        
        print(f"✅ [SHIPPING_INFO] Found order {order_id}")
        
        result = {
            "order_id": order.order_id,
            "shipping_address": order.shipping_address,
            "tracking_number": order.tracking_number,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery.strftime("%Y-%m-%d") if order.estimated_delivery else "Not available"
        }
        
        print(f"🚚 [SHIPPING_INFO] Returning shipping info: {len(result)} fields")
        return result
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Search for products based on query."""
        print(f"🔍 [PRODUCT_SEARCH] Searching products for query: '{query[:30]}{'...' if len(query) > 30 else ''}'")
        
        query_lower = query.lower()
        matching_products = []
        
        for product in self.mock_products:
            if (query_lower in product.name.lower() or 
                query_lower in product.category.lower() or 
                any(query_lower in tag.lower() for tag in product.tags)):
                matching_products.append(product.to_dict())
        
        print(f"🔍 [PRODUCT_SEARCH] Found {len(matching_products)} matching products")
        
        result = {
            "query": query,
            "results_count": len(matching_products),
            "products": matching_products
        }
        
        print(f"🔍 [PRODUCT_SEARCH] Returning search results")
        return result
    
    def get_product_details(self, user_input: str) -> Dict[str, Any]:
        """Get detailed product information."""
        print(f"📦 [PRODUCT_DETAILS] Processing product details request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        # Try to extract product ID first
        product_id = self._extract_product_id(user_input)
        if product_id:
            print(f"📦 [PRODUCT_DETAILS] Extracted product ID: {product_id}")
            product = self._find_product(product_id)
            if product:
                print(f"✅ [PRODUCT_DETAILS] Found product by ID: {product_id}")
                return product.to_dict()
        
        # Try to extract product name
        product_name = self._extract_product_name(user_input)
        if product_name:
            print(f"📦 [PRODUCT_DETAILS] Extracted product name: {product_name}")
            # Find product by name
            for product in self.mock_products:
                if product_name in product.name.lower():
                    print(f"✅ [PRODUCT_DETAILS] Found product by name: {product.name}")
                    return product.to_dict()
        
        # Return first available product as fallback
        print(f"🔄 [PRODUCT_DETAILS] No specific product found, returning first available product")
        return self.mock_products[0].to_dict()
    
    def get_product_recommendations(self, user_input: str) -> Dict[str, Any]:
        """Get product recommendations based on user input."""
        print(f"💡 [RECOMMENDATIONS] Processing recommendations request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        category = self._extract_product_name(user_input)
        if not category:
            category = "Hiking & Backpacking"
            print(f"💡 [RECOMMENDATIONS] No specific category detected, using default: {category}")
        
        print(f"💡 [RECOMMENDATIONS] Detected category: {category}")
        
        # Filter products by category
        category_products = [p for p in self.mock_products if category.lower() in p.category.lower()]
        
        recommendations = []
        for product in category_products[:3]:  # Top 3 recommendations
            recommendations.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description[:100] + "..." if len(product.description) > 100 else product.description
            })
        
        print(f"💡 [RECOMMENDATIONS] Generated {len(recommendations)} recommendations")
        
        result = {
            "category": category,
            "recommendations": recommendations,
            "reason": f"Based on your interest in {category.lower()} gear"
        }
        
        print(f"💡 [RECOMMENDATIONS] Returning recommendations")
        return result
    
    def get_company_info(self, user_input: str) -> Dict[str, Any]:
        """Get company information."""
        print(f"🏢 [COMPANY_INFO] Processing company info request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "company_name": Branding.COMPANY_NAME,
            "description": Branding.COMPANY_INTRO,
            "values": ["Quality", "Adventure", "Customer Service", "Sustainability"],
            "categories": ["Hiking & Backpacking", "Camping & Outdoor Living", "Water Sports", "Climbing"]
        }
        
        print(f"🏢 [COMPANY_INFO] Returning company information: {len(result)} fields")
        return result
    
    def get_contact_info(self, user_input: str) -> Dict[str, Any]:
        """Get contact information."""
        print(f"📞 [CONTACT_INFO] Processing contact info request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "contact_info": Branding.CONTACT_INFO,
            "social_media": {
                "facebook": "SierraOutfitters",
                "instagram": "@sierraoutfitters",
                "twitter": "@SierraOutfitters"
            }
        }
        
        print(f"📞 [CONTACT_INFO] Returning contact information: {len(result)} fields")
        return result
    
    def get_policies(self, user_input: str) -> Dict[str, Any]:
        """Get company policies."""
        print(f"📋 [POLICIES] Processing policies request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "return_policy": "30-day return policy for unused items in original packaging",
            "shipping_info": "Free shipping on orders over $50, 2-5 business days",
            "warranty": "1-year warranty on all products",
            "privacy_policy": "We protect your personal information and never share it with third parties"
        }
        
        print(f"📋 [POLICIES] Returning company policies: {len(result)} fields")
        return result
    
    def log_complaint(self, user_input: str) -> Dict[str, Any]:
        """Log a customer complaint."""
        print(f"📝 [COMPLAINT] Processing complaint: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        complaint_id = f"COMP_{int(datetime.now().timestamp())}"
        
        result = {
            "complaint_id": complaint_id,
            "status": "Logged",
            "message": "Your complaint has been logged and will be reviewed by our team",
            "next_steps": "A customer service representative will contact you within 24 hours"
        }
        
        print(f"📝 [COMPLAINT] Complaint logged with ID: {complaint_id}")
        return result
    
    def get_escalation_info(self, user_input: str) -> Dict[str, Any]:
        """Get escalation information."""
        print(f"🚨 [ESCALATION] Processing escalation request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "escalation_contact": "Senior Customer Service Manager",
            "escalation_email": "escalations@sierraoutfitters.com",
            "response_time": "2-4 hours",
            "escalation_criteria": "Complex issues, multiple failed resolutions, urgent matters"
        }
        
        print(f"🚨 [ESCALATION] Returning escalation information: {len(result)} fields")
        return result
    
    def get_return_policy(self, user_input: str) -> Dict[str, Any]:
        """Get return policy information."""
        print(f"🔄 [RETURN_POLICY] Processing return policy request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "policy": "30-day return policy for unused items in original packaging",
            "process": "1. Contact customer service 2. Get return authorization 3. Ship item back 4. Receive refund",
            "contact": "returns@sierraoutfitters.com or 1-800-SIERRA-1"
        }
        
        print(f"🔄 [RETURN_POLICY] Returning return policy: {len(result)} fields")
        return result
    
    def initiate_return(self, user_input: str) -> Dict[str, Any]:
        """Initiate a return process."""
        print(f"🔄 [RETURN_INITIATE] Processing return initiation: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        return_id = f"RET_{int(datetime.now().timestamp())}"
        
        result = {
            "return_id": return_id,
            "status": "Initiated",
            "message": "Your return has been initiated successfully",
            "next_steps": "You will receive a return label via email within 1 hour"
        }
        
        print(f"🔄 [RETURN_INITIATE] Return initiated with ID: {return_id}")
        return result
    
    def get_shipping_options(self, user_input: str) -> Dict[str, Any]:
        """Get available shipping options."""
        print(f"🚚 [SHIPPING_OPTIONS] Processing shipping options request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "standard_shipping": {
                "cost": 5.99,
                "delivery_time": "5-7 business days",
                "description": "Standard ground shipping"
            },
            "express_shipping": {
                "cost": 12.99,
                "delivery_time": "2-3 business days",
                "description": "Express shipping with tracking"
            },
            "overnight_shipping": {
                "cost": 24.99,
                "delivery_time": "1 business day",
                "description": "Overnight delivery"
            }
        }
        
        print(f"🚚 [SHIPPING_OPTIONS] Returning shipping options: {len(result)} options")
        return result
    
    def calculate_shipping(self, user_input: str) -> Dict[str, Any]:
        """Calculate shipping cost and delivery time."""
        print(f"💰 [SHIPPING_CALC] Processing shipping calculation: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "shipping_cost": 5.99,
            "delivery_time": "5-7 business days",
            "shipping_method": "Standard Ground",
            "estimated_delivery": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }
        
        print(f"💰 [SHIPPING_CALC] Calculated shipping: ${result['shipping_cost']}, {result['delivery_time']}")
        return result
    
    def get_tracking_info(self, user_input: str) -> Dict[str, Any]:
        """Get package tracking information."""
        print(f"📦 [TRACKING] Processing tracking request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        tracking_number = self._extract_tracking_number(user_input)
        if not tracking_number:
            print("❌ [TRACKING] No tracking number found in user input")
            return {"error": "No tracking number found. Please provide your tracking number."}
        
        print(f"📦 [TRACKING] Extracted tracking number: {tracking_number}")
        
        result = {
            "tracking_number": tracking_number,
            "status": "In Transit",
            "current_location": "Distribution Center - Anytown, USA",
            "estimated_delivery": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "tracking_url": f"https://tracking.sierraoutfitters.com/{tracking_number}"
        }
        
        print(f"📦 [TRACKING] Returning tracking information: {len(result)} fields")
        return result
    
    def get_current_promotions(self, user_input: str) -> Dict[str, Any]:
        """Get current promotions and deals."""
        print(f"🎉 [PROMOTIONS] Processing promotions request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "current_promotions": [
                {
                    "name": "Summer Sale",
                    "discount": "20% off",
                    "valid_until": "2024-08-31",
                    "categories": ["Hiking & Backpacking", "Camping & Outdoor Living"]
                },
                {
                    "name": "New Customer Discount",
                    "discount": "15% off",
                    "valid_until": "2024-12-31",
                    "categories": ["All Categories"]
                }
            ]
        }
        
        print(f"🎉 [PROMOTIONS] Returning {len(result['current_promotions'])} current promotions")
        return result
    
    def check_discounts(self, user_input: str) -> Dict[str, Any]:
        """Check available discounts for customer."""
        print(f"💰 [DISCOUNTS] Processing discounts request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "available_discounts": [
                "Summer Sale: 20% off hiking gear",
                "New Customer: 15% off first order",
                "Bulk Order: 10% off orders over $200"
            ],
            "how_to_apply": "Enter discount code at checkout or contact customer service"
        }
        
        print(f"💰 [DISCOUNTS] Returning {len(result['available_discounts'])} available discounts")
        return result
    
    def get_sale_items(self, user_input: str) -> Dict[str, Any]:
        """Get items currently on sale."""
        print(f"🏷️ [SALE_ITEMS] Processing sale items request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        result = {
            "sale_items": [
                {
                    "product_id": "PROD001",
                    "name": "Sierra Summit Hiking Boots",
                    "original_price": 129.99,
                    "sale_price": 103.99,
                    "discount": "20% off"
                },
                {
                    "product_id": "PROD003",
                    "name": "Trail Master Backpack",
                    "original_price": 89.99,
                    "sale_price": 71.99,
                    "discount": "20% off"
                }
            ],
            "sale_end_date": "2024-08-31"
        }
        
        print(f"🏷️ [SALE_ITEMS] Returning {len(result['sale_items'])} sale items")
        return result
    
    # Helper methods
    def _extract_order_id(self, text: str) -> Optional[str]:
        """Extract order ID from text."""
        print(f"🔍 [HELPER] Extracting order ID from: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Look for patterns like ORD12345, Order 12345, #12345
        patterns = [
            r'ORD\d+',
            r'Order\s+(\d+)',
            r'#(\d+)',
            r'Track\s+#(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
                print(f"🔍 [HELPER] Extracted order ID: {order_id}")
                return order_id
        
        print("🔍 [HELPER] No order ID found")
        return None
    
    def _extract_product_id(self, text: str) -> Optional[str]:
        """Extract product ID from text."""
        print(f"🔍 [HELPER] Extracting product ID from: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Look for patterns like PROD001, Product 001
        patterns = [
            r'PROD\d+',
            r'Product\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                product_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
                print(f"🔍 [HELPER] Extracted product ID: {product_id}")
                return product_id
        
        print("🔍 [HELPER] No product ID found")
        return None
    
    def _extract_product_name(self, text: str) -> Optional[str]:
        """Extract product name/category from text."""
        print(f"🔍 [HELPER] Extracting product name from: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Look for common product categories
        categories = ["hiking", "camping", "water", "climbing", "boots", "tent", "backpack"]
        
        text_lower = text.lower()
        for category in categories:
            if category in text_lower:
                print(f"🔍 [HELPER] Extracted product category: {category}")
                return category
        
        print("🔍 [HELPER] No product category found")
        return None
    
    def _extract_tracking_number(self, text: str) -> Optional[str]:
        """Extract tracking number from text."""
        print(f"🔍 [HELPER] Extracting tracking number from: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Look for patterns like TRK789456123, Tracking 789456123
        patterns = [
            r'TRK\d+',
            r'Tracking\s+(\d+)',
            r'Track\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tracking_number = match.group(1) if len(match.groups()) > 0 else match.group(0)
                print(f"🔍 [HELPER] Extracted tracking number: {tracking_number}")
                return tracking_number
        
        print("🔍 [HELPER] No tracking number found")
        return None
    
    def _find_order(self, order_id: str) -> Optional[Order]:
        """Find order by ID."""
        print(f"🔍 [HELPER] Finding order with ID: {order_id}")
        
        for order in self.mock_orders:
            if order.order_id == order_id:
                print(f"✅ [HELPER] Found order: {order_id}")
                return order
        
        print(f"❌ [HELPER] Order not found: {order_id}")
        return None
    
    def _find_product(self, product_id: str) -> Optional[Product]:
        """Find product by ID."""
        print(f"🔍 [HELPER] Finding product with ID: {product_id}")
        
        for product in self.mock_products:
            if product.id == product_id:
                print(f"✅ [HELPER] Found product: {product_id}")
                return product
        
        print(f"❌ [HELPER] Product not found: {product_id}")
        return None
