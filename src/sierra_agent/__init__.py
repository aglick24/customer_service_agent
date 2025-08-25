"""
Sierra Agent Package

AI-powered customer service agent for Sierra Outfitters with real-time
quality monitoring, comprehensive analytics, and intelligent planning.
"""

from .core.agent import AgentConfig, SierraAgent
from .utils.branding import Branding
from .utils.error_messages import ErrorMessages

__version__ = "2.0.0"
__all__ = [
    "AgentConfig",
    "Branding",
    "ErrorMessages",
    "SierraAgent",
]
