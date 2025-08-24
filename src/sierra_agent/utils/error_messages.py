"""
Error Messages and Standardized Responses

This module contains standardized error messages and responses for consistent
customer service interactions and error handling.
"""

from .branding import Branding


class ErrorMessages:
    """Standardized error messages for the Sierra Outfitters AI agent."""

    # Technical Issues
    TECHNICAL_DIFFICULTIES = (
        "I'm experiencing some technical difficulties right now. "
        "Please try again in a moment, or contact our human customer service team "
        f"at {Branding.CONTACT_INFO['phone']} for immediate assistance."
    )

    LLM_GENERATION_ISSUE = (
        "I'm having trouble generating a response at the moment. "
        "Let me try to help you with your request. "
        "If this continues, please contact our customer service team."
    )

    API_CONNECTION_ERROR = (
        "I'm unable to connect to our systems right now. "
        "Please check your internet connection and try again, "
        "or contact our customer service team for assistance."
    )

    # Customer Service Issues
    ORDER_NOT_FOUND = (
        "I couldn't find an order with that information. "
        "Please double-check your order number or email address. "
        "If you're still having trouble, our customer service team can help locate your order."
    )

    PRODUCT_NOT_AVAILABLE = (
        "I'm sorry, but that product doesn't appear to be available at the moment. "
        "This could be due to high demand or seasonal availability. "
        "Would you like me to suggest similar alternatives or check if it's available at a different time?"
    )

    INVALID_INPUT = (
        "I didn't quite understand that. Could you please rephrase your request? "
        "I'm here to help with orders, products, returns, and general questions about Sierra Outfitters."
    )

    # Intent Classification Issues
    INTENT_CLARIFICATION = (
        "I want to make sure I understand your request correctly. "
        "Are you looking for help with: an order, a product, customer service, "
        "or something else? Please let me know so I can assist you better."
    )

    # Tool Execution Issues
    TOOL_EXECUTION_ERROR = (
        "I'm having trouble accessing that information right now. "
        "Let me try a different approach, or you can contact our customer service team "
        "who will have direct access to our systems."
    )

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = (
        "I'm processing requests a bit slower than usual due to high demand. "
        "Please wait a moment and try again, or contact our customer service team "
        "for immediate assistance."
    )

    # Maintenance Mode
    SYSTEM_MAINTENANCE = (
        "Our system is currently undergoing scheduled maintenance. "
        "I can still help with general questions, but some features may be temporarily unavailable. "
        "Please try again in a few minutes, or contact our customer service team."
    )

    # Generic Helpful Responses
    GENERAL_HELP = (
        "I'm here to help you with Sierra Outfitters! I can assist with: "
        "• Order tracking and status updates\n"
        "• Product information and recommendations\n"
        "• Return and exchange requests\n"
        "• Shipping and delivery questions\n"
        "• General customer service inquiries\n\n"
        "What would you like help with today?"
    )

    FALLBACK_RESPONSE = (
        "I want to make sure I provide you with the best possible assistance. "
        "Could you please provide more details about what you're looking for? "
        "I'm here to help with all things Sierra Outfitters!"
    )

    @classmethod
    def get_apologetic_response(cls, original_message: str) -> str:
        """Get an apologetic response while maintaining the original message."""
        return (
            "I apologize for the confusion. Let me try to help you with that. "
            f"{original_message}"
        )

    @classmethod
    def get_escalation_message(cls, issue_type: str) -> str:
        """Get a message for escalating to human customer service."""
        return (
            f"I understand you're experiencing an issue with {issue_type}. "
            "This is something that would be best handled by our human customer service team. "
            f"Please call us at {Branding.CONTACT_INFO['phone']} or email us at "
            f"{Branding.CONTACT_INFO['email']} for immediate assistance. "
            "They'll be able to resolve this for you right away."
        )

    @classmethod
    def get_retry_message(cls, action: str, max_attempts: int = 3) -> str:
        """Get a message encouraging the user to retry an action."""
        return (
            f"I'm having trouble {action} right now. "
            f"This sometimes happens and usually resolves itself. "
            f"Please try again in a moment. If the issue persists after {max_attempts} attempts, "
            "please contact our customer service team for assistance."
        )
