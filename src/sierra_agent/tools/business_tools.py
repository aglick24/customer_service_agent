"""
Business Tools

This module contains various business tools that provide access to business data
and operations for the Sierra Outfitters customer service system.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List

from ..data.data_provider import DataProvider
from ..data.data_types import Order, Product
from ..utils.branding import Branding

logger = logging.getLogger(__name__)


class BusinessTools:
    """Collection of business tools for customer service operations."""

    def __init__(self) -> None:
        self.data_provider = DataProvider()
        logger.info("BusinessTools initialized with DataProvider")

    def get_order_status(self, user_input: str) -> Dict[str, Any]:
        """Get order status and tracking information."""
        print(
            f"📦 [ORDER_STATUS] Processing order status request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Extract email and order number from user input
        email = self._extract_email(user_input)
        order_number = self._extract_order_number(user_input)
        
        if not email:
            print("❌ [ORDER_STATUS] No email found in user input")
            return {"error": "Please provide your email address to check order status."}
            
        if not order_number:
            print("❌ [ORDER_STATUS] No order number found in user input")
            return {"error": "Please provide your order number to check order status."}

        print(f"📦 [ORDER_STATUS] Looking up order {order_number} for {email}")

        # Use DataProvider to get order status
        order_data = self.data_provider.get_order_status(email, order_number)
        
        if not order_data:
            print(f"❌ [ORDER_STATUS] Order {order_number} not found for {email}")
            return {
                "error": f"Order {order_number} not found for email {email}. Please check your information."
            }

        print(f"✅ [ORDER_STATUS] Found order {order_number} with status: {order_data['order_info']['Status']}")

        result = {
            "order_number": order_data["order_info"]["OrderNumber"],
            "customer_name": order_data["order_info"]["CustomerName"],
            "status": order_data["order_info"]["Status"],
            "products": [p["ProductName"] for p in order_data["products"]],
            "tracking_number": order_data["order_info"]["TrackingNumber"],
            "tracking_url": order_data["tracking_url"]
        }

        print(f"📦 [ORDER_STATUS] Returning order status: {result}")
        return result



    def search_products(self, query: str) -> Dict[str, Any]:
        """Search for products based on query using DataProvider."""
        print(
            f"🔍 [PRODUCT_SEARCH] Searching products for query: '{query[:30]}{'...' if len(query) > 30 else ''}'"
        )

        # Use DataProvider to search products
        matching_products = self.data_provider.search_products(query)

        print(f"🔍 [PRODUCT_SEARCH] Found {len(matching_products)} matching products")

        result = {
            "query": query,
            "results_count": len(matching_products),
            "products": matching_products,
        }

        print("🔍 [PRODUCT_SEARCH] Returning search results")
        return result

    def get_product_details(self, user_input: str) -> Dict[str, Any]:
        """Get detailed product information using DataProvider."""
        print(
            f"📦 [PRODUCT_DETAILS] Processing product details request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Try to extract product SKU/ID first
        product_sku = self._extract_product_id(user_input)
        if product_sku:
            print(f"📦 [PRODUCT_DETAILS] Extracted product SKU: {product_sku}")
            product = self.data_provider.get_product_by_sku(product_sku)
            if product:
                print(f"✅ [PRODUCT_DETAILS] Found product by SKU: {product_sku}")
                return product

        # Try general search for product name
        search_results = self.data_provider.search_products(user_input)
        if search_results:
            print(f"✅ [PRODUCT_DETAILS] Found product via search")
            return search_results[0]

        print("❌ [PRODUCT_DETAILS] No product found")
        return {"error": "Product not found. Please provide a valid product name or SKU."}

    def get_product_recommendations(self, user_input: str) -> Dict[str, Any]:
        """Get product recommendations based on user input using DataProvider."""
        print(
            f"💡 [RECOMMENDATIONS] Processing recommendations request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Extract preferences from user input
        preferences = self._extract_preferences(user_input)
        category = self._extract_product_category(user_input)
        
        print(f"💡 [RECOMMENDATIONS] Detected preferences: {preferences}, category: {category}")

        # Get recommendations from DataProvider
        if category:
            recommendations = self.data_provider.get_products_by_category(category)
        else:
            # Use search to find products based on preferences
            search_terms = " ".join(preferences) if preferences else "hiking adventure"
            recommendations = self.data_provider.search_products(search_terms)

        if not recommendations:
            print("💡 [RECOMMENDATIONS] No specific recommendations, getting general search results")
            recommendations = self.data_provider.search_products("outdoor")[:3]

        print(f"💡 [RECOMMENDATIONS] Generated {len(recommendations)} recommendations")

        result = {
            "category": category,
            "preferences": preferences,
            "recommendations": recommendations,
            "reason": f"Based on your interest in {category or 'outdoor gear'}",
        }

        print("💡 [RECOMMENDATIONS] Returning recommendations")
        return result

    def get_company_info(self, user_input: str) -> Dict[str, Any]:
        """Get company information."""
        print(
            f"🏢 [COMPANY_INFO] Processing company info request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "company_name": Branding.COMPANY_NAME,
            "description": Branding.COMPANY_INTRO,
            "values": ["Quality", "Adventure", "Customer Service", "Sustainability"],
            "categories": [
                "Hiking & Backpacking",
                "Camping & Outdoor Living",
                "Water Sports",
                "Climbing",
            ],
        }

        print(f"🏢 [COMPANY_INFO] Returning company information: {len(result)} fields")
        return result

    def get_contact_info(self, user_input: str) -> Dict[str, Any]:
        """Get contact information."""
        print(
            f"📞 [CONTACT_INFO] Processing contact info request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "contact_info": Branding.CONTACT_INFO,
            "social_media": {
                "facebook": "SierraOutfitters",
                "instagram": "@sierraoutfitters",
                "twitter": "@SierraOutfitters",
            },
        }

        print(f"📞 [CONTACT_INFO] Returning contact information: {len(result)} fields")
        return result

    def get_policies(self, user_input: str) -> Dict[str, Any]:
        """Get company policies."""
        print(
            f"📋 [POLICIES] Processing policies request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "return_policy": "30-day return policy for unused items in original packaging",
            "shipping_info": "Free shipping on orders over $50, 2-5 business days",
            "warranty": "1-year warranty on all products",
            "privacy_policy": "We protect your personal information and never share it with third parties",
        }

        print(f"📋 [POLICIES] Returning company policies: {len(result)} fields")
        return result

    def log_complaint(self, user_input: str) -> Dict[str, Any]:
        """Log a customer complaint."""
        print(
            f"📝 [COMPLAINT] Processing complaint: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        complaint_id = f"COMP_{int(datetime.now().timestamp())}"

        result = {
            "complaint_id": complaint_id,
            "status": "Logged",
            "message": "Your complaint has been logged and will be reviewed by our team",
            "next_steps": "A customer service representative will contact you within 24 hours",
        }

        print(f"📝 [COMPLAINT] Complaint logged with ID: {complaint_id}")
        return result

    def get_escalation_info(self, user_input: str) -> Dict[str, Any]:
        """Get escalation information."""
        print(
            f"🚨 [ESCALATION] Processing escalation request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "escalation_contact": "Senior Customer Service Manager",
            "escalation_email": "escalations@sierraoutfitters.com",
            "response_time": "2-4 hours",
            "escalation_criteria": "Complex issues, multiple failed resolutions, urgent matters",
        }

        print(f"🚨 [ESCALATION] Returning escalation information: {len(result)} fields")
        return result

    def get_return_policy(self, user_input: str) -> Dict[str, Any]:
        """Get return policy information."""
        print(
            f"🔄 [RETURN_POLICY] Processing return policy request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "policy": "30-day return policy for unused items in original packaging",
            "process": "1. Contact customer service 2. Get return authorization 3. Ship item back 4. Receive refund",
            "contact": "returns@sierraoutfitters.com or 1-800-SIERRA-1",
        }

        print(f"🔄 [RETURN_POLICY] Returning return policy: {len(result)} fields")
        return result

    def initiate_return(self, user_input: str) -> Dict[str, Any]:
        """Initiate a return process."""
        print(
            f"🔄 [RETURN_INITIATE] Processing return initiation: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        return_id = f"RET_{int(datetime.now().timestamp())}"

        result = {
            "return_id": return_id,
            "status": "Initiated",
            "message": "Your return has been initiated successfully",
            "next_steps": "You will receive a return label via email within 1 hour",
        }

        print(f"🔄 [RETURN_INITIATE] Return initiated with ID: {return_id}")
        return result

    def get_shipping_options(self, user_input: str) -> Dict[str, Any]:
        """Get available shipping options."""
        print(
            f"🚚 [SHIPPING_OPTIONS] Processing shipping options request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "standard_shipping": {
                "cost": 5.99,
                "delivery_time": "5-7 business days",
                "description": "Standard ground shipping",
            },
            "express_shipping": {
                "cost": 12.99,
                "delivery_time": "2-3 business days",
                "description": "Express shipping with tracking",
            },
            "overnight_shipping": {
                "cost": 24.99,
                "delivery_time": "1 business day",
                "description": "Overnight delivery",
            },
        }

        print(
            f"🚚 [SHIPPING_OPTIONS] Returning shipping options: {len(result)} options"
        )
        return result

    def calculate_shipping(self, user_input: str) -> Dict[str, Any]:
        """Calculate shipping cost and delivery time."""
        print(
            f"💰 [SHIPPING_CALC] Processing shipping calculation: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "shipping_cost": 5.99,
            "delivery_time": "5-7 business days",
            "shipping_method": "Standard Ground",
            "estimated_delivery": (datetime.now() + timedelta(days=7)).strftime(
                "%Y-%m-%d"
            ),
        }

        print(
            f"💰 [SHIPPING_CALC] Calculated shipping: ${result['shipping_cost']}, {result['delivery_time']}"
        )
        return result

    def get_tracking_info(self, user_input: str) -> Dict[str, Any]:
        """Get package tracking information."""
        print(
            f"📦 [TRACKING] Processing tracking request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        tracking_number = self._extract_tracking_number(user_input)
        if not tracking_number:
            print("❌ [TRACKING] No tracking number found in user input")
            return {
                "error": "No tracking number found. Please provide your tracking number."
            }

        print(f"📦 [TRACKING] Extracted tracking number: {tracking_number}")

        result = {
            "tracking_number": tracking_number,
            "status": "In Transit",
            "current_location": "Distribution Center - Anytown, USA",
            "estimated_delivery": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%d"
            ),
            "tracking_url": f"https://tracking.sierraoutfitters.com/{tracking_number}",
        }

        print(f"📦 [TRACKING] Returning tracking information: {len(result)} fields")
        return result

    def get_current_promotions(self, user_input: str) -> Dict[str, Any]:
        """Get current promotions and deals."""
        print(
            f"🎉 [PROMOTIONS] Processing promotions request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "current_promotions": [
                {
                    "name": "Summer Sale",
                    "discount": "20% off",
                    "valid_until": "2024-08-31",
                    "categories": ["Hiking & Backpacking", "Camping & Outdoor Living"],
                },
                {
                    "name": "New Customer Discount",
                    "discount": "15% off",
                    "valid_until": "2024-12-31",
                    "categories": ["All Categories"],
                },
            ]
        }

        print(
            f"🎉 [PROMOTIONS] Returning {len(result['current_promotions'])} current promotions"
        )
        return result

    def check_discounts(self, user_input: str) -> Dict[str, Any]:
        """Check available discounts for customer."""
        print(
            f"💰 [DISCOUNTS] Processing discounts request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "available_discounts": [
                "Summer Sale: 20% off hiking gear",
                "New Customer: 15% off first order",
                "Bulk Order: 10% off orders over $200",
            ],
            "how_to_apply": "Enter discount code at checkout or contact customer service",
        }

        print(
            f"💰 [DISCOUNTS] Returning {len(result['available_discounts'])} available discounts"
        )
        return result

    def get_sale_items(self, user_input: str) -> Dict[str, Any]:
        """Get items currently on sale."""
        print(
            f"🏷️ [SALE_ITEMS] Processing sale items request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        result = {
            "sale_items": [
                {
                    "product_id": "PROD001",
                    "name": "Sierra Summit Hiking Boots",
                    "original_price": 129.99,
                    "sale_price": 103.99,
                    "discount": "20% off",
                },
                {
                    "product_id": "PROD003",
                    "name": "Trail Master Backpack",
                    "original_price": 89.99,
                    "sale_price": 71.99,
                    "discount": "20% off",
                },
            ],
            "sale_end_date": "2024-08-31",
        }

        print(f"🏷️ [SALE_ITEMS] Returning {len(result['sale_items'])} sale items")
        return result

    # Helper methods
    def _extract_order_id(self, text: str) -> Optional[str]:
        """Extract order ID from text."""
        print(
            f"🔍 [HELPER] Extracting order ID from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for patterns like ORD12345, Order 12345, #12345
        patterns = [r"ORD\d+", r"Order\s+(\d+)", r"#(\d+)", r"Track\s+#(\d+)"]

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
        print(
            f"🔍 [HELPER] Extracting product ID from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for patterns like PROD001, Product 001
        patterns = [r"PROD\d+", r"Product\s+(\d+)"]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                product_id = (
                    match.group(1) if len(match.groups()) > 0 else match.group(0)
                )
                print(f"🔍 [HELPER] Extracted product ID: {product_id}")
                return product_id

        print("🔍 [HELPER] No product ID found")
        return None

    def _extract_product_name(self, text: str) -> Optional[str]:
        """Extract product name/category from text."""
        print(
            f"🔍 [HELPER] Extracting product name from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for common product categories
        categories = [
            "hiking",
            "camping",
            "water",
            "climbing",
            "boots",
            "tent",
            "backpack",
        ]

        text_lower = text.lower()
        for category in categories:
            if category in text_lower:
                print(f"🔍 [HELPER] Extracted product category: {category}")
                return category

        print("🔍 [HELPER] No product category found")
        return None

    def _extract_tracking_number(self, text: str) -> Optional[str]:
        """Extract tracking number from text."""
        print(
            f"🔍 [HELPER] Extracting tracking number from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for patterns like TRK789456123, Tracking 789456123
        patterns = [r"TRK\d+", r"Tracking\s+(\d+)", r"Track\s+(\d+)"]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tracking_number = (
                    match.group(1) if len(match.groups()) > 0 else match.group(0)
                )
                print(f"🔍 [HELPER] Extracted tracking number: {tracking_number}")
                return tracking_number

        print("🔍 [HELPER] No tracking number found")
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        print(
            f"🔍 [HELPER] Extracting email from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        
        if match:
            email = match.group(0)
            print(f"🔍 [HELPER] Extracted email: {email}")
            return email

        print("🔍 [HELPER] No email found")
        return None

    def _extract_order_number(self, text: str) -> Optional[str]:
        """Extract order number from text."""
        print(
            f"🔍 [HELPER] Extracting order number from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for patterns like #W001, W001, Order #W001
        patterns = [r'#W\d+', r'W\d+', r'Order\s+#?W\d+']

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_number = match.group(0)
                # Ensure it starts with # if it's a W number
                if order_number.startswith('W') and not order_number.startswith('#'):
                    order_number = '#' + order_number
                print(f"🔍 [HELPER] Extracted order number: {order_number}")
                return order_number

        print("🔍 [HELPER] No order number found")
        return None



    def get_early_risers_promotion(self, user_input: str) -> Dict[str, Any]:
        """Check and provide Early Risers promotion if available."""
        print(
            f"🎉 [EARLY_RISERS] Processing Early Risers promotion request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Check if promotion is available
        promotion = self.data_provider.get_early_risers_promotion()

        if promotion:
            result = {
                "available": True,
                "discount_code": promotion["discount_code"],
                "discount_percentage": promotion["discount_percentage"],
                "valid_hours": promotion["valid_hours"],
                "description": promotion["description"],
                "message": f"🎉 Congratulations! You're eligible for our Early Risers promotion. Use code {promotion['discount_code']} for {promotion['discount_percentage']}% off your entire order!"
            }
        else:
            # Get current time information for better error message
            from datetime import datetime, timezone, timedelta
            pacific_tz = timezone(timedelta(hours=-8))
            current_time = datetime.now(pacific_tz)
            current_time_str = current_time.strftime("%I:%M %p")
            
            result = {
                "available": False,
                "message": f"The Early Risers promotion is only available from 8:00 AM to 10:00 AM Pacific Time. It's currently {current_time_str} PT, so the promotion is not active right now. Please check back during the early morning hours (8:00-10:00 AM PT) for exclusive discounts!",
                "valid_hours": "8:00 AM - 10:00 AM Pacific Time",
                "current_time": current_time_str + " PT",
                "next_available": "Tomorrow at 8:00 AM Pacific Time"
            }

        print(f"🎉 [EARLY_RISERS] Promotion check result: {result['available']}")
        return result


    def _extract_product_category(self, text: str) -> Optional[str]:
        """Extract product category from text."""
        text_lower = text.lower()
        
        # Common product categories from the catalog
        categories = [
            "backpack", "hiking", "adventure", "outdoor gear",
            "skis", "snow", "winter", "high-tech", "trail", "comfort",
            "food & beverage", "weatherproof", "versatile", "explorer",
            "rugged design", "trailblazing", "personal flight", "safety-enhanced",
            "stealth", "discretion", "advanced cloaking", "fashion", "lifestyle",
            "teleportation", "transport", "home decor", "lighting", "modern design",
            "luxury", "interior style"
        ]
        
        for category in categories:
            if category in text_lower:
                return category
        
        return None

    def _extract_preferences(self, text: str) -> List[str]:
        """Extract customer preferences from text."""
        text_lower = text.lower()
        preferences = []
        
        # Common preference keywords
        preference_keywords = [
            "hiking", "camping", "adventure", "outdoor", "winter", "summer",
            "comfort", "luxury", "budget", "premium", "lightweight", "durable",
            "waterproof", "high-tech", "traditional", "modern", "classic"
        ]
        
        for keyword in preference_keywords:
            if keyword in text_lower:
                preferences.append(keyword)
        
        return preferences

    def _extract_search_query(self, text: str) -> Optional[str]:
        """Extract search query from text."""
        # Remove common phrases and keep the main search term
        text_lower = text.lower()
        
        # Remove common phrases
        phrases_to_remove = [
            "i'm looking for", "i need", "i want", "show me", "find", "search for",
            "can you help me find", "looking for", "searching for", "to", "for"
        ]
        
        search_query = text_lower
        for phrase in phrases_to_remove:
            search_query = search_query.replace(phrase, "").strip()
        
        # Clean up extra spaces and common words
        search_query = " ".join([word for word in search_query.split() if len(word) > 2])
        
        # If we have a meaningful query left, return it
        if len(search_query) > 2:
            return search_query
        
        return None
