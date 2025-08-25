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

    def get_order_status(self, user_input: str, conversation_context=None) -> ToolResult:
        """Get order status and tracking information - simplified approach."""
        print(f"📦 [ORDER_STATUS] Processing order status request: '{user_input[:50]}...'")

        # Simple extraction - no complex continuation logic
        email = self._extract_email(user_input)
        order_number = self._extract_order_number(user_input)

        # If missing data, return error with helpful message
        if not email or not order_number:
            return ToolResult(
                success=False,
                error="I need both your email address and order number to look up your order. Please provide both in your message.",
                data=None
            )

        print(f"📦 [ORDER_STATUS] Looking up order {order_number} for {email}")

        # Get order from data provider
        order = self.data_provider.get_order_status(email, order_number)

        if not order:
            return ToolResult(
                success=False,
                error=f"Order {order_number} not found for {email}. Please check your details.",
                data=None
            )

        print(f"✅ [ORDER_STATUS] Found order {order_number}")
        return ToolResult(success=True, data=order, error=None)



    def search_products(self, user_input: str, conversation_context=None) -> ToolResult:
        """Search for products based on query using DataProvider."""
        print(
            f"🔍 [PRODUCT_SEARCH] Searching products for query: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'"
        )

        # Use DataProvider to search products
        matching_products = self.data_provider.search_products(user_input)

        print(f"🔍 [PRODUCT_SEARCH] Found {len(matching_products)} matching products")

        if not matching_products:
            return ToolResult(
                success=False,
                error=f"I couldn't find any products matching '{user_input}'. Try using different keywords like 'hiking', 'camping', or 'boots'.",
                data=None
            )

        # Return the list of Product objects directly
        print("🔍 [PRODUCT_SEARCH] Returning search results")
        return ToolResult(
            success=True,
            data=matching_products,  # List[Product]
            error=None
        )

    def get_product_details(self, user_input: str, conversation_context=None) -> ToolResult:
        """Get detailed product information - simplified approach."""
        print(f"📦 [PRODUCT_DETAILS] Processing: '{user_input[:50]}...'")

        # Try to extract product SKU/ID first
        product_sku = self._extract_product_id(user_input)
        if product_sku:
            product = self.data_provider.get_product_by_sku(product_sku)
            if product:
                return ToolResult(success=True, data=product, error=None)

        # Try general search for product name
        search_results = self.data_provider.search_products(user_input)
        if search_results:
            return ToolResult(success=True, data=search_results[0], error=None)

        return ToolResult(
            success=False,
            error="Product not found. Please provide a valid product name or SKU.",
            data=None
        )

    def get_product_recommendations(self, user_input: str, conversation_context=None) -> ToolResult:
        """Get product recommendations - simplified approach."""
        print(f"💡 [RECOMMENDATIONS] Processing: '{user_input[:50]}...'")

        # Extract preferences from user input
        preferences = self._extract_preferences(user_input)
        category = self._extract_product_category(user_input)

        # Get recommendations from DataProvider
        if category:
            recommendations = self.data_provider.get_products_by_category(category)
        else:
            # Use search to find products based on preferences
            search_terms = " ".join(preferences) if preferences else "outdoor hiking"
            recommendations = self.data_provider.search_products(search_terms)

        # Fallback to general outdoor products
        if not recommendations:
            recommendations = self.data_provider.search_products("outdoor")[:5]

        if not recommendations:
            return ToolResult(
                success=False,
                error="No product recommendations available at this time.",
                data=None
            )

        print(f"💡 [RECOMMENDATIONS] Generated {len(recommendations)} recommendations")
        return ToolResult(success=True, data=recommendations, error=None)

    def get_company_info(self, user_input: str, conversation_context=None) -> ToolResult:
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

    def get_contact_info(self, user_input: str, conversation_context=None) -> ToolResult:
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

    def get_policies(self, user_input: str, conversation_context=None) -> ToolResult:
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
        """Extract order number from text with improved pattern matching."""
        print(
            f"🔍 [HELPER] Extracting order number from: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )

        # Comprehensive patterns for order numbers including flexible formatting
        patterns = [
            r"#\s*W\s*\d+",           # #W001, # W001, #W 001
            r"\bW\s*-?\s*\d+\b",      # W001, W-001, W 001 (with word boundaries)
            r"order\s+#?\s*W\s*-?\s*\d+",  # Order W001, order #W001, order W-001
            r"order\s+number\s+#?\s*W\s*-?\s*\d+",  # order number W001
            r"my\s+order\s+#?\s*W\s*-?\s*\d+",      # my order W001
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract just the core order number part
                order_text = match.group(0)
                
                # Find the W and number part
                w_match = re.search(r"W\s*-?\s*(\d+)", order_text, re.IGNORECASE)
                if w_match:
                    number_part = w_match.group(1)
                    order_number = f"#W{number_part.zfill(3)}"  # Ensure consistent format like #W001
                    print(f"🔍 [HELPER] Extracted order number: {order_number}")
                    return order_number

        print("🔍 [HELPER] No order number found")
        return None



    def get_early_risers_promotion(self, user_input: str, conversation_context=None) -> ToolResult:
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

