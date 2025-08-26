"""
Tool Orchestrator

Extensible tool orchestrator that automatically discovers and registers tools
using the BaseTool interface. Makes adding new tools extremely easy.
"""

import logging
from typing import Any, Dict, List

from sierra_agent.data.data_provider import DataProvider
from sierra_agent.data.data_types import ToolResult

from .base_tool import BaseTool, ToolRegistry
from .order_tools import OrderStatusTool  # OrderHistoryTool commented out - not needed for assignment
from .catalog_tools import ProductCatalogTool, SmartRecommendationTool, ProductDetailsTool
from .business_tools import BusinessTools  # Keep for legacy support

logger = logging.getLogger(__name__)


class ToolOrchestrator:
    """Extensible tool orchestrator with automatic tool discovery and registration."""

    def __init__(self, data_provider: DataProvider = None) -> None:
        """Initialize ToolOrchestrator with extensible tool system."""
        
        # Initialize data provider
        if data_provider is None:
            data_provider = DataProvider()
        self.data_provider = data_provider
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        
        # Keep legacy business tools for backward compatibility
        self.business_tools = BusinessTools()
        self.legacy_tools = self._get_legacy_tools()
        
        # Auto-register all available tools
        self._register_all_tools()
        
        logger.info(f"ToolOrchestrator initialized with {len(self.tool_registry.list_tools())} tools")

    def _get_legacy_tools(self) -> Dict[str, Any]:
        """Get legacy tools for backward compatibility."""
        return {
            "get_early_risers_promotion": self.business_tools.get_early_risers_promotion,
            "get_company_info": self.business_tools.get_company_info,
            # "get_contact_info": self.business_tools.get_contact_info,  # COMMENTED OUT - Not needed for assignment
            # "get_policies": self.business_tools.get_policies,  # COMMENTED OUT - Not needed for assignment
        }

    def _register_all_tools(self) -> None:
        """Register all available tools automatically."""
        
        # Register new extensible tools
        tools_to_register = [
            OrderStatusTool(self.data_provider),
            # OrderHistoryTool(self.data_provider),  # COMMENTED OUT - Not needed for assignment requirements
            ProductCatalogTool(self.data_provider),
            SmartRecommendationTool(self.data_provider),
            ProductDetailsTool(self.data_provider),
        ]
        
        for tool in tools_to_register:
            self.tool_registry.register(tool)
            logger.debug(f"Registered tool: {tool.tool_name}")

    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool dynamically."""
        self.tool_registry.register(tool)
        logger.info(f"Dynamically registered tool: {tool.tool_name}")

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name with automatic fallback to legacy tools."""
        
        # First try new extensible tools
        if tool_name in self.tool_registry.list_tools():
            return self.tool_registry.execute_tool(tool_name, **kwargs)
        
        # Fallback to legacy tools for backward compatibility
        if tool_name in self.legacy_tools:
            try:
                legacy_tool = self.legacy_tools[tool_name]
                return legacy_tool(**kwargs)
            except Exception as e:
                logger.exception(f"Error executing legacy tool {tool_name}: {e}")
                return ToolResult(
                    success=False,
                    error=f"Legacy tool execution failed: {str(e)}",
                    data=None
                )
        
        # Tool not found
        available_tools = self.get_available_tools()
        return ToolResult(
            success=False,
            error=f"Tool '{tool_name}' not found. Available tools: {available_tools}",
            data=None
        )

    def get_available_tools(self) -> List[str]:
        """Get list of all available tools (new + legacy)."""
        new_tools = self.tool_registry.list_tools()
        legacy_tools = list(self.legacy_tools.keys())
        return sorted(new_tools + legacy_tools)

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool."""
        tool = self.tool_registry.get_tool(tool_name)
        if tool:
            return tool.get_parameter_schema()
        
        # Return basic schema for legacy tools
        if tool_name in self.legacy_tools:
            return {
                "tool_name": tool_name,
                "description": "Legacy tool - see business_tools.py for details",
                "parameters": {}
            }
        
        return {}

    def get_all_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all tools - useful for documentation/LLM context."""
        schemas = self.tool_registry.get_tool_schemas()
        
        # Add legacy tool schemas
        for tool_name in self.legacy_tools:
            schemas[tool_name] = self.get_tool_schema(tool_name)
        
        return schemas
    
    def get_tools_for_llm_planning(self) -> str:
        """Get formatted tool descriptions for LLM planning prompts."""
        # Get extensible tool descriptions (with automatic parameter info)
        extensible_descriptions = self.tool_registry.get_tools_for_llm_planning()
        
        # Add legacy tool descriptions
        legacy_descriptions = []
        legacy_tool_info = {
            "get_early_risers_promotion": "Check Early Risers promotion availability (8-10 AM PT)",
            "get_company_info": "Get Sierra Outfitters company information and values",
            # "get_contact_info": "Get contact details and social media information",  # COMMENTED OUT
            # "get_policies": "Get return, shipping, and warranty policy information"  # COMMENTED OUT
        }
        
        for tool_name in self.legacy_tools:
            description = legacy_tool_info.get(tool_name, "Legacy business tool")
            legacy_descriptions.append(f"- {tool_name}: {description}")
        
        # Combine all descriptions
        all_descriptions = []
        if extensible_descriptions:
            all_descriptions.append(extensible_descriptions)
        if legacy_descriptions:
            all_descriptions.extend(legacy_descriptions)
            
        return "\n".join(all_descriptions)

    def get_tool_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about tool execution."""
        return {
            "total_tools": len(self.get_available_tools()),
            "extensible_tools": len(self.tool_registry.list_tools()),
            "legacy_tools": len(self.legacy_tools),
            "tool_schemas_available": len(self.get_all_tool_schemas())
        }

    def get_tool_descriptions(self) -> str:
        """Get tool descriptions - alias for get_tools_for_llm_planning for backward compatibility."""
        return self.get_tools_for_llm_planning()

