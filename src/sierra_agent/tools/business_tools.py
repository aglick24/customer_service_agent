"""
Business Tools

This module contains various business tools that provide access to business data
and operations for the Sierra Outfitters customer service system.
"""

import logging
from datetime import datetime, timedelta, timezone

from sierra_agent.data.data_provider import DataProvider
from sierra_agent.data.data_types import ToolResult
from sierra_agent.utils.branding import Branding

logger = logging.getLogger(__name__)

class BusinessTools:
    """Collection of business tools for customer service operations."""

    def __init__(self) -> None:
        self.data_provider = DataProvider()
        logger.info("BusinessTools initialized with DataProvider")

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

    def get_early_risers_promotion(self) -> ToolResult:
        """Check and provide Early Risers promotion if available."""
        promotion = self.data_provider.get_early_risers_promotion()

        if promotion:
            result = {
                "available": True,
                "discount_code": promotion.discount_code,
                "discount_percentage": promotion.discount_percentage,
                "valid_hours": promotion.valid_hours,
                "description": promotion.description,
                "message": f"🎉 Congratulations! You're eligible for our Early Risers promotion. Use code {promotion.discount_code} for {promotion.discount_percentage}% off your entire order!"
            }

            return ToolResult(success=True, data=result, error=None)
            
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

