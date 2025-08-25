"""
Business Tools

This module contains various business tools that provide access to business data
and operations for the Sierra Outfitters customer service system.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional

from ..data.data_provider import DataProvider
from ..data.data_types import ToolResult
from ..utils.branding import Branding

logger = logging.getLogger(__name__)


class BusinessTools:
    """Collection of business tools for customer service operations."""

    def __init__(self) -> None:
        self.data_provider = DataProvider()
        logger.info("BusinessTools initialized with DataProvider")

    def get_order_status(self, user_input: str) -> ToolResult:
        """Get order status and tracking information."""
        print(
            f"📦 [ORDER_STATUS] Processing order status request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Extract email and order number from user input
        email = self._extract_email(user_input)
        order_number = self._extract_order_number(user_input)

        if not email:
            print("❌ [ORDER_STATUS] No email found in user input")
            return ToolResult(
                success=False,
                error="Please provide your email address to check order status.",
                data=None
            )

        if not order_number:
            print("❌ [ORDER_STATUS] No order number found in user input")
            return ToolResult(
                success=False,
                error="Please provide your order number to check order status.",
                data=None
            )

        print(f"📦 [ORDER_STATUS] Looking up order {order_number} for {email}")

        # Use DataProvider to get typed Order object
        order = self.data_provider.get_order_status(email, order_number)

        if not order:
            print(f"❌ [ORDER_STATUS] Order {order_number} not found for {email}")
            return ToolResult(
                success=False,
                error=f"Order {order_number} not found for email {email}. Please check your information.",
                data=None
            )

        print(f"✅ [ORDER_STATUS] Found order {order_number} with status: {order.status}")

        # Return the typed Order object wrapped in ToolResult
        print("📦 [ORDER_STATUS] Returning typed Order object")
        return ToolResult(
            success=True,
            data=order,  # Keep the typed Order object!
            error=None
        )



    def search_products(self, query: str) -> ToolResult:
        """Search for products based on query using DataProvider."""
        print(
            f"🔍 [PRODUCT_SEARCH] Searching products for query: '{query[:30]}{'...' if len(query) > 30 else ''}'"
        )

        # Use DataProvider to search products
        matching_products = self.data_provider.search_products(query)

        print(f"🔍 [PRODUCT_SEARCH] Found {len(matching_products)} matching products")

        if not matching_products:
            return ToolResult(
                success=False,
                error=f"No products found for '{query}'. Please try a different search term.",
                data=None
            )

        # Return the list of Product objects directly
        print("🔍 [PRODUCT_SEARCH] Returning search results")
        return ToolResult(
            success=True,
            data=matching_products,  # List[Product]
            error=None
        )

    def get_product_details(self, user_input: str) -> ToolResult:
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
                return ToolResult(success=True, data=product, error=None)

        # Try general search for product name
        search_results = self.data_provider.search_products(user_input)
        if search_results:
            print("✅ [PRODUCT_DETAILS] Found product via search")
            return ToolResult(success=True, data=search_results[0], error=None)

        print("❌ [PRODUCT_DETAILS] No product found")
        return ToolResult(
            success=False,
            error="Product not found. Please provide a valid product name or SKU.",
            data=None
        )

    def get_product_recommendations(self, user_input: str) -> ToolResult:
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

        if not recommendations:
            return ToolResult(
                success=False,
                error="No product recommendations available at this time.",
                data=None
            )

        print(f"💡 [RECOMMENDATIONS] Generated {len(recommendations)} recommendations")

        # Return the list of Product objects directly
        print("💡 [RECOMMENDATIONS] Returning recommendations")
        return ToolResult(
            success=True,
            data=recommendations,  # List[Product]
            error=None
        )

    def get_company_info(self, user_input: str) -> ToolResult:
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
        return ToolResult(
            success=True,
            data=result,
            error=None
        )

    def get_contact_info(self, user_input: str) -> ToolResult:
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
        return ToolResult(
            success=True,
            data=result,
            error=None
        )

    def get_policies(self, user_input: str) -> ToolResult:
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
        return ToolResult(
            success=True,
            data=result,
            error=None
        )


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


    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        print(
            f"🔍 [HELPER] Extracting email from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Look for email pattern
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
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
        patterns = [r"#W\d+", r"W\d+", r"Order\s+#?W\d+"]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_number = match.group(0)
                # Ensure it starts with # if it's a W number
                if order_number.startswith("W") and not order_number.startswith("#"):
                    order_number = "#" + order_number
                print(f"🔍 [HELPER] Extracted order number: {order_number}")
                return order_number

        print("🔍 [HELPER] No order number found")
        return None



    def get_early_risers_promotion(self, user_input: str) -> ToolResult:
        """Check and provide Early Risers promotion if available."""
        print(
            f"🎉 [EARLY_RISERS] Processing Early Risers promotion request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Check if promotion is available
        promotion = self.data_provider.get_early_risers_promotion()

        if promotion:
            # Create a comprehensive promotion result using the Promotion object
            result = {
                "available": True,
                "discount_code": promotion.discount_code,
                "discount_percentage": promotion.discount_percentage,
                "valid_hours": promotion.valid_hours,
                "description": promotion.description,
                "message": f"🎉 Congratulations! You're eligible for our Early Risers promotion. Use code {promotion.discount_code} for {promotion.discount_percentage}% off your entire order!"
            }

            return ToolResult(success=True, data=result, error=None)
        # Get current time information for better error message
        from datetime import timezone
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
        return ToolResult(success=True, data=result, error=None)


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
