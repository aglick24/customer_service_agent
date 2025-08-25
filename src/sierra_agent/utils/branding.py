"""
Branding and Company Information

This module contains Sierra Outfitters branding guidelines, company information,
and messaging templates for consistent customer interactions with adventure personality.
"""

import random
from typing import List


class Branding:
    """Sierra Outfitters branding and company information with adventure personality."""

    # Company Information
    COMPANY_NAME = "Sierra Outfitters"
    COMPANY_INTRO = "🏔️ Sierra Outfitters - Your Premier Outdoor Adventure Destination! 🏔️"
    COMPANY_TAGLINE = "Adventure Awaits - Gear Up and Conquer the Unknown! 🏔️"

    # Adventure Catchphrases
    ADVENTURE_CATCHPHRASES = [
        "Onward into the unknown! 🏔️",
        "Adventure is calling! 🏔️",
        "The mountains are waiting for you! 🏔️", 
        "Your next adventure starts here! 🏔️",
        "Happy trails! 🏔️",
        "Adventure awaits! 🏔️"
    ]

    # Mountain Emojis for Various Uses
    MOUNTAIN_EMOJIS = ["🏔️", "⛰️", "🗻", "🏕️", "🥾", "🧗", "🎒"]

    # Brand Voice Guidelines - Adventure Personality (Balanced)
    BRAND_GUIDANCE = """
    Sierra Outfitters Brand Voice - Outdoor Adventure Spirit:
    - Show enthusiasm for outdoor activities and adventures
    - Use mountain emojis (🏔️) occasionally for friendly emphasis  
    - Include adventure catchphrases like "Onward into the unknown!" when appropriate
    - Reference outdoor themes naturally: mountains, peaks, trails, adventures
    - Be knowledgeable about outdoor gear with an adventurer's perspective
    - Helpful and customer-focused with an outdoor enthusiast's spirit
    - Professional yet adventurous and approachable
    - Connect with outdoor enthusiasts while remaining accessible to all
    - Make interactions feel welcoming and adventure-ready
    """

    # Product Categories
    PRODUCT_CATEGORIES = [
        "Hiking & Backpacking",
        "Camping & Outdoor Living",
        "Climbing & Mountaineering",
        "Water Sports & Fishing",
        "Winter Sports & Snow Gear",
        "Outdoor Clothing & Footwear",
        "Electronics & Navigation",
        "Safety & Survival Gear",
    ]

    # Company Values
    COMPANY_VALUES = [
        "Quality and Durability",
        "Customer Satisfaction",
        "Outdoor Expertise",
        "Environmental Responsibility",
        "Adventure and Exploration",
    ]

    # Contact Information
    CONTACT_INFO = {
        "phone": "1-800-SIERRA-1",
        "email": "customerservice@sierraoutfitters.com",
        "website": "www.sierraoutfitters.com",
        "hours": "Mon-Fri: 8AM-8PM, Sat-Sun: 9AM-6PM (Mountain Time)",
    }

    # Social Media
    SOCIAL_MEDIA = {
        "instagram": "@sierraoutfitters",
        "facebook": "SierraOutfitters",
        "twitter": "@SierraOutfit",
        "youtube": "SierraOutfittersTV",
    }

    # Return Policy
    RETURN_POLICY = """
    Sierra Outfitters Return Policy:
    - 30-day return window for most items
    - Free returns on all orders
    - Must be in original condition with tags
    - Some restrictions apply to safety equipment
    """

    # Shipping Information
    SHIPPING_INFO = """
    Sierra Outfitters Shipping:
    - Free standard shipping on orders over $50
    - 2-3 business days for standard delivery
    - Express shipping available (1-2 business days)
    - International shipping to select countries
    """

    @classmethod
    def get_welcome_message(cls) -> str:
        """Get an adventure-themed welcome message."""
        emoji = random.choice(cls.MOUNTAIN_EMOJIS)
        return f"{emoji} Welcome to {cls.COMPANY_NAME}! {cls.COMPANY_TAGLINE} {emoji}"

    @classmethod
    def get_closing_message(cls) -> str:
        """Get an adventure-themed closing message."""
        catchphrase = random.choice(cls.ADVENTURE_CATCHPHRASES)
        return f"Thank you for choosing {cls.COMPANY_NAME}! {catchphrase}"

    @classmethod
    def get_random_catchphrase(cls) -> str:
        """Get a random adventure catchphrase."""
        return random.choice(cls.ADVENTURE_CATCHPHRASES)

    @classmethod
    def get_random_mountain_emoji(cls) -> str:
        """Get a random mountain/outdoor emoji."""
        return random.choice(cls.MOUNTAIN_EMOJIS)

    @classmethod
    def get_adventure_greeting(cls) -> str:
        """Get a friendly adventure-themed greeting."""
        greetings = [
            "🏔️ Ready for your next outdoor adventure?",
            "What can we help you with for your outdoor pursuits?",
            "🏔️ Your adventure gear headquarters is here to help!",
            "Let's gear you up for the trails ahead!",
            "How can we prepare you for your next adventure?"
        ]
        return random.choice(greetings)

    @classmethod
    def get_company_description(cls) -> str:
        """Get a comprehensive company description with adventure personality."""
        return f"""
        {cls.COMPANY_INTRO}

        🏔️ We are your premier destination for high-quality outdoor gear and equipment. Whether you're hiking mountain trails, exploring the wilderness, or camping under the stars, we provide the essential tools for your outdoor adventures.

        Our expert team consists of passionate outdoor enthusiasts who are committed to helping you find the perfect gear for your adventures and expeditions.

        From dawn on the mountain peaks to evening around the campfire, Sierra Outfitters is your trusted companion for every outdoor journey. Adventure awaits! 🏔️
        """

    @classmethod
    def format_adventure_response(cls, base_response: str) -> str:
        """Add adventure personality to any response."""
        emoji = random.choice(cls.MOUNTAIN_EMOJIS)
        catchphrase = random.choice(cls.ADVENTURE_CATCHPHRASES)
        
        # Add mountain emoji to start if not already present
        if not any(e in base_response for e in cls.MOUNTAIN_EMOJIS):
            base_response = f"{emoji} {base_response}"
        
        # Add catchphrase if response doesn't already end with one
        if not any(phrase.split('!')[0] in base_response for phrase in cls.ADVENTURE_CATCHPHRASES):
            base_response = f"{base_response}\n\n{catchphrase}"
            
        return base_response

    # Adventure-themed error messages
    ADVENTURE_ERROR_MESSAGES = {
        "order_not_found": "🏔️ Hmm, that order seems to have wandered off the trail! Double-check your email and order number, and we'll get you back on track. Happy trails! 🏔️",
        "product_not_found": "🏔️ Those products must be hiding in the wilderness! Try different search terms and we'll help you discover the perfect gear. Adventure is calling! 🏔️", 
        "general_error": "🏔️ Looks like we hit a rocky patch on the trail! Don't worry - let's regroup and try again! 🏔️",
        "promotion_not_active": "🏔️ The Early Risers promotion is currently resting! Check back between 8:00-10:00 AM PT for exclusive discounts. Adventure awaits! 🏔️"
    }

    @classmethod
    def get_adventure_error_message(cls, error_type: str = "general_error") -> str:
        """Get an adventure-themed error message."""
        return cls.ADVENTURE_ERROR_MESSAGES.get(error_type, cls.ADVENTURE_ERROR_MESSAGES["general_error"])
