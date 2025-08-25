"""
Tool Orchestrator

This module coordinates the execution of various business tools based on
customer intent and provides a unified interface for tool management.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from ..ai.llm_client import LLMClient
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
    """Orchestrates the execution of business tools based on customer intent."""

    def __init__(
        self, low_latency_llm: Optional[Union[Any, "LLMClient"]] = None
    ) -> None:
        self.business_tools = BusinessTools()

        # Available business tools registry (for plan-based execution)
        self.available_tools = {
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

        # Initialize LLM client
        self.llm_client = self._initialize_llm_client()

        # Tool cache for performance
        self.tool_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info("ToolOrchestrator initialized")

    def _register_custom_tools(self) -> None:
        """Register built-in custom tools."""
        print("🎭 [ORCHESTRATOR] Registering custom tools...")

        # Add any built-in custom tools here
        # For now, we'll leave this empty as tools are added dynamically

        print("🎭 [ORCHESTRATOR] Custom tools registration complete")

    def _initialize_llm_client(self):
        """Initialize the LLM client."""
        try:
            from ..ai.llm_client import LLMClient

            client = LLMClient()
            return client
        except Exception as e:
            logger.error(f"Error creating LLM client: {e}")
            raise e

    def execute_tool(self, tool_name: str, user_input: str) -> ToolResult:
        """Execute a specific tool by name for plan-based execution."""
        try:
            # Check if tool is available
            if tool_name not in self.available_tools:
                available_tools = list(self.available_tools.keys())
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not available. Available tools: {available_tools}",
                    data=None
                )

            # Execute the tool
            tool_method = self.available_tools[tool_name]
            result = tool_method(user_input)

            # All mapped tools return ToolResult objects
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
            "cached_results": len(self.tool_cache),
            "cache_ttl": self.cache_ttl,
        }

        print(f"📊 [ORCHESTRATOR] Statistics: {stats}")
        return stats

    def clear_cache(self) -> None:
        """Clear the tool execution cache."""
        print("🧹 [ORCHESTRATOR] Clearing tool execution cache...")

        cache_size = len(self.tool_cache)
        self.tool_cache.clear()

        print(f"🧹 [ORCHESTRATOR] Cache cleared, removed {cache_size} entries")
        logger.info("Tool execution cache cleared")

    def get_cached_result(
        self, request_type: str, user_input: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        print(f"🔍 [ORCHESTRATOR] Checking cache for request type: {request_type}")

        cache_key = f"{request_type}_{hash(user_input)}"

        if cache_key in self.tool_cache:
            cached_data = self.tool_cache[cache_key]
            age = time.time() - cached_data["timestamp"]

            if age < self.cache_ttl:
                print(
                    f"✅ [ORCHESTRATOR] Cache hit for key: {cache_key} (age: {age:.1f}s)"
                )
                return cached_data["results"]
            print(
                f"⏰ [ORCHESTRATOR] Cache expired for key: {cache_key} (age: {age:.1f}s)"
            )
            del self.tool_cache[cache_key]
        else:
            print(f"❌ [ORCHESTRATOR] Cache miss for key: {cache_key}")

        return None
