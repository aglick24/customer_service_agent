"""
Branding and Company Information

This module contains Sierra Outfitters branding guidelines, company information,
and messaging templates for consistent customer interactions.
"""

class Branding:
    """Sierra Outfitters branding and company information."""
    
    # Company Information
    COMPANY_NAME = "Sierra Outfitters"
    COMPANY_INTRO = "Sierra Outfitters - Your Premier Outdoor Gear Destination"
    COMPANY_TAGLINE = "Adventure Awaits - Gear Up with Sierra Outfitters"
    
    # Brand Voice Guidelines
    BRAND_GUIDANCE = """
    Sierra Outfitters Brand Voice:
    - Enthusiastic about outdoor activities and adventure
    - Knowledgeable about outdoor gear and equipment
    - Helpful and customer-focused
    - Professional yet approachable
    - Emphasize quality, durability, and performance
    - Connect with outdoor enthusiasts and nature lovers
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
        "Safety & Survival Gear"
    ]
    
    # Company Values
    COMPANY_VALUES = [
        "Quality and Durability",
        "Customer Satisfaction",
        "Outdoor Expertise",
        "Environmental Responsibility",
        "Adventure and Exploration"
    ]
    
    # Contact Information
    CONTACT_INFO = {
        "phone": "1-800-SIERRA-1",
        "email": "customerservice@sierraoutfitters.com",
        "website": "www.sierraoutfitters.com",
        "hours": "Mon-Fri: 8AM-8PM, Sat-Sun: 9AM-6PM (Mountain Time)"
    }
    
    # Social Media
    SOCIAL_MEDIA = {
        "instagram": "@sierraoutfitters",
        "facebook": "SierraOutfitters",
        "twitter": "@SierraOutfit",
        "youtube": "SierraOutfittersTV"
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
        """Get a standard welcome message."""
        return f"Welcome to {cls.COMPANY_NAME}! {cls.COMPANY_TAGLINE}"
    
    @classmethod
    def get_closing_message(cls) -> str:
        """Get a standard closing message."""
        return f"Thank you for choosing {cls.COMPANY_NAME}. Adventure awaits!"
    
    @classmethod
    def get_company_description(cls) -> str:
        """Get a comprehensive company description."""
        return f"""
        {cls.COMPANY_INTRO}
        
        We are your premier destination for high-quality outdoor gear and equipment. 
        From hiking and camping to climbing and water sports, we provide the tools 
        you need for your next adventure.
        
        Our expert team is passionate about outdoor activities and committed to 
        helping you find the perfect gear for your needs.
        """
