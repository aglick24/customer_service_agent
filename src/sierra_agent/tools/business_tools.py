"""
Business Tools

This module contains various business tools that provide access to business data
and operations for the Sierra Outfitters customer service system.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional

from sierra_agent.data.data_provider import DataProvider
from sierra_agent.data.data_types import ToolResult
from sierra_agent.utils.branding import Branding

logger = logging.getLogger(__name__)

class BusinessTools:
    """Collection of business tools for customer service operations."""

    def __init__(self) -> None:
        self.data_provider = DataProvider()
        logger.info("BusinessTools initialized with DataProvider")

    def get_order_status(self, email: str, order_number: str) -> ToolResult:
        """Get order status and tracking information."""

        # Validate required parameters
        if not email or not order_number:
            return ToolResult(
                success=False,
                error="Both email address and order number are required.",
                data=None
            )

        # Get order from data provider
        order = self.data_provider.get_order_status(email, order_number)

        if not order:
            return ToolResult(
                success=False,
                error=Branding.get_adventure_error_message("order_not_found"),
                data=None
            )

        return ToolResult(success=True, data=order, error=None)

    def search_products(self, query: str) -> ToolResult:
        """Search for products based on query."""

        if not query or not query.strip():
            return ToolResult(
                success=False,
                error="Search query is required.",
                data=None
            )

        # Use DataProvider to search products
        matching_products = self.data_provider.search_products(query.strip())

        if not matching_products:
            return ToolResult(
                success=False,
                error=Branding.get_adventure_error_message("product_not_found"),
                data=None
            )

        return ToolResult(
            success=True,
            data=matching_products,  # List[Product]
            error=None
        )

    def get_product_details(self, skus: List[str]) -> ToolResult:
        """Get detailed product information for specific SKUs."""

        if not skus:
            return ToolResult(
                success=False,
                error="At least one product SKU is required.",
                data=None
            )

        # Get products for each SKU
        products = []
        for sku in skus:
            if not sku or not sku.strip():
                continue
            product = self.data_provider.get_product_by_sku(sku.strip())
            if product:
                products.append(product)

        if not products:
            return ToolResult(
                success=False,
                error=f"No products found for SKUs: {', '.join(skus)}",
                data=None
            )

        # Return single product if only one, list if multiple
        return ToolResult(success=True, data=products if len(products) > 1 else products[0], error=None)

    def get_product_recommendations(self, category: Optional[str] = None, preferences: Optional[List[str]] = None) -> ToolResult:
        """Get product recommendations based on category and preferences."""

        # Get recommendations from DataProvider
        if category:
            recommendations = self.data_provider.get_products_by_category(category)
        elif preferences:
            # Use search to find products based on preferences
            search_terms = " ".join(preferences)
            recommendations = self.data_provider.search_products(search_terms)
        else:
            # Default to outdoor products
            recommendations = self.data_provider.search_products("outdoor")[:5]

        if not recommendations:
            return ToolResult(
                success=False,
                error=Branding.get_adventure_error_message("product_not_found"),
                data=None
            )

        return ToolResult(success=True, data=recommendations, error=None)

    def get_company_info(self) -> ToolResult:
        """Get company information."""

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

        return ToolResult(
            success=True,
            data=result,
            error=None
        )

    def get_contact_info(self) -> ToolResult:
        """Get contact information."""

        result = {
            "contact_info": Branding.CONTACT_INFO,
            "social_media": {
                "facebook": "SierraOutfitters",
                "instagram": "@sierraoutfitters",
                "twitter": "@SierraOutfitters",
            },
        }

        return ToolResult(
            success=True,
            data=result,
            error=None
        )

    def get_policies(self) -> ToolResult:
        """Get company policies."""

        result = {
            "return_policy": "30-day return policy for unused items in original packaging",
            "shipping_info": "Free shipping on orders over $50, 2-5 business days",
            "warranty": "1-year warranty on all products",
            "privacy_policy": "We protect your personal information and never share it with third parties",
        }

        return ToolResult(
            success=True,
            data=result,
            error=None
        )

    # Helper methods

    def _extract_product_id(self, text: str) -> Optional[str]:
        """Extract product ID from text."""

        # Look for patterns like PROD001, Product 001
        patterns = [r"PROD\d+", r"Product\s+(\d+)"]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return (
                    match.group(1) if len(match.groups()) > 0 else match.group(0)
                )


        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""

        # Look for email pattern
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        match = re.search(email_pattern, text)

        if match:
            return match.group(0)


        return None

    def _extract_order_number(self, text: str) -> Optional[str]:
        """Extract order number from text with improved pattern matching."""

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
                    return f"#W{number_part.zfill(3)}"  # Ensure consistent format like #W001


        return None

    def get_early_risers_promotion(self) -> ToolResult:
        """Check and provide Early Risers promotion if available."""

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

