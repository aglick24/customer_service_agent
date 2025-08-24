"""
Sierra Agent - AI-Powered Customer Service Platform

A comprehensive AI customer service platform with real-time quality monitoring,
detailed analytics, and intelligent business tool orchestration.
"""

__version__ = "1.0.0"
__author__ = "Sierra Outfitters Development Team"
__email__ = "dev@sierraoutfitters.com"

# Core components
from .core.agent import SierraAgent, AgentConfig
from .core.conversation import Conversation, Message, CustomerContext, ConversationState

# AI and LLM components
from .ai.llm_client import LLMClient, UsageStats

# Analytics and quality monitoring
from .analytics.quality_scorer import QualityScorer
from .analytics.conversation_analytics import ConversationAnalytics

# Business tools and orchestration
from .tools.tool_orchestrator import ToolOrchestrator
from .tools.business_tools import BusinessTools

# Data types and models
from .data.data_types import (
    IntentType, SentimentType, QualityLevel,
    Product, Order, Customer, QualityScore,
    ConversationMetrics, ToolResult, BusinessRule
)

# Utility modules
from .utils.branding import Branding
from .utils.error_messages import ErrorMessages

__all__ = [
    # Core
    "SierraAgent",
    "AgentConfig",
    "Conversation",
    "Message",
    "CustomerContext",
    "ConversationState",
    
    # AI/LLM
    "LLMClient",
    "UsageStats",
    
    # Analytics
    "QualityScorer",
    "ConversationAnalytics",
    
    # Tools
    "ToolOrchestrator",
    "BusinessTools",
    
    # Data Types
    "IntentType",
    "SentimentType",
    "QualityLevel",
    "Product",
    "Order",
    "Customer",
    "QualityScore",
    "ConversationMetrics",
    "ToolResult",
    "BusinessRule",
    
    # Utils
    "Branding",
    "ErrorMessages",
]
