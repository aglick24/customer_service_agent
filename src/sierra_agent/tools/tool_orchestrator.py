"""
Tool Orchestrator

This module coordinates the execution of various business tools and
provides a unified interface for tool management with proper dependency injection.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from ..data.data_types import ToolResult
from .business_tools import BusinessTools

logger = logging.getLogger(__name__)

@dataclass
class ToolExecutionResult:
    """Result of tool execution."""

    tool_name: str
    success: bool
    data: Any
    execution_time: float
    error_message: Optional[str] = None

class ToolOrchestrator:
    """Orchestrates the execution of business tools with clean separation of concerns."""

    def __init__(self) -> None:
        """Initialize ToolOrchestrator - pure tool coordination."""
        
        self.business_tools = BusinessTools()

        # Available business tools registry (for plan-based execution)
        self.available_tools: Dict[str, Callable[..., Any]] = {
            "get_order_status": self.business_tools.get_order_status,
            "search_products": self.business_tools.search_products,
            "get_product_details": self.business_tools.get_product_details,
            "get_product_recommendations": self.business_tools.get_product_recommendations,
            "get_early_risers_promotion": self.business_tools.get_early_risers_promotion,
            "get_company_info": self.business_tools.get_company_info,
            "get_contact_info": self.business_tools.get_contact_info,
            "get_policies": self.business_tools.get_policies,
        }
        # Custom tools registry
        self.custom_tools: Dict[str, Callable] = {}

        logger.info("ToolOrchestrator initialized")

    def _register_custom_tools(self) -> None:
        """Register built-in custom tools."""
        
        # Add any built-in custom tools here
        # For now, we'll leave this empty as tools are added dynamically

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a specific tool by name with typed parameters."""
        try:
            # Check if tool is available
            if tool_name not in self.available_tools:
                available_tools = list(self.available_tools.keys())
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not available. Available tools: {available_tools}",
                    data=None
                )

            # Execute the tool with typed parameters
            tool_method = self.available_tools[tool_name]
            
            # Call tool with unpacked keyword arguments
            result = tool_method(**kwargs)
            return result

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {e!s}",
                data=None
            )

    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        business_tools = [
            method
            for method in dir(self.business_tools)
            if callable(getattr(self.business_tools, method))
            and not method.startswith("_")
        ]

        custom_tools = list(self.custom_tools.keys())

        all_tools = business_tools + custom_tools
        return all_tools

    def add_custom_tool(self, tool_name: str, tool_function: Callable) -> bool:
        """Add a custom tool to the orchestrator."""
        
        try:
            self.custom_tools[tool_name] = tool_function
            
            return True

        except Exception as e:
            
            logger.error(f"Error adding custom tool {tool_name}: {e}")
            return False

    def remove_custom_tool(self, tool_name: str) -> bool:
        """Remove a custom tool from the orchestrator."""
        
        try:
            if tool_name in self.custom_tools:
                del self.custom_tools[tool_name]
                
                return True
            
            return False

        except Exception as e:
            
            logger.error(f"Error removing custom tool {tool_name}: {e}")
            return False

    def get_tool_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about tool execution."""
        
        stats = {
            "total_tools": len(self.get_available_tools()),
            "business_tools": len(
                [
                    m
                    for m in dir(self.business_tools)
                    if callable(getattr(self.business_tools, m))
                    and not m.startswith("_")
                ]
            ),
            "custom_tools": len(self.custom_tools),
        }

        return stats
