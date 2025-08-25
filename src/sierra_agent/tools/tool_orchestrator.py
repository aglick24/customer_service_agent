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
        print("🎭 [ORCHESTRATOR] Initializing ToolOrchestrator...")
        
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

        print(f"🎭 [ORCHESTRATOR] Initialized with {len(self.available_tools)} business tools")
        logger.info("ToolOrchestrator initialized")

    def _register_custom_tools(self) -> None:
        """Register built-in custom tools."""
        print("🎭 [ORCHESTRATOR] Registering custom tools...")

        # Add any built-in custom tools here
        # For now, we'll leave this empty as tools are added dynamically

        print("🎭 [ORCHESTRATOR] Custom tools registration complete")

    def execute_tool(self, tool_name: str, user_input: str, conversation_context=None) -> ToolResult:
        """Execute a specific tool by name - simple coordination."""
        try:
            # Check if tool is available
            if tool_name not in self.available_tools:
                available_tools = list(self.available_tools.keys())
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not available. Available tools: {available_tools}",
                    data=None
                )

            # Execute the tool with standard parameters
            tool_method = self.available_tools[tool_name]
            
            # Clean tool signature: tool(user_input, conversation_context)
            result = tool_method(user_input, conversation_context=conversation_context)
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
        print(f"➕ [ORCHESTRATOR] Adding custom tool: {tool_name}")

        try:
            if tool_name in self.custom_tools:
                print(f"⚠️ [ORCHESTRATOR] Tool {tool_name} already exists, overwriting")

            self.custom_tools[tool_name] = tool_function
            print(f"✅ [ORCHESTRATOR] Custom tool {tool_name} added successfully")

            return True

        except Exception as e:
            print(f"❌ [ORCHESTRATOR] Error adding custom tool {tool_name}: {e}")
            logger.error(f"Error adding custom tool {tool_name}: {e}")
            return False

    def remove_custom_tool(self, tool_name: str) -> bool:
        """Remove a custom tool from the orchestrator."""
        print(f"➖ [ORCHESTRATOR] Removing custom tool: {tool_name}")

        try:
            if tool_name in self.custom_tools:
                del self.custom_tools[tool_name]
                print(f"✅ [ORCHESTRATOR] Custom tool {tool_name} removed successfully")
                return True
            print(f"⚠️ [ORCHESTRATOR] Tool {tool_name} not found in custom tools")
            return False

        except Exception as e:
            print(f"❌ [ORCHESTRATOR] Error removing custom tool {tool_name}: {e}")
            logger.error(f"Error removing custom tool {tool_name}: {e}")
            return False

    def get_tool_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about tool execution."""
        print("📊 [ORCHESTRATOR] Getting tool execution statistics...")

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

        print(f"📊 [ORCHESTRATOR] Statistics: {stats}")
        return stats
