"""
Base Tool Interface

Provides the foundation for all business tools to ensure consistent behavior
and easy extensibility for new tool types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union

from sierra_agent.data.data_types import ToolResult


@dataclass
class ToolParameter:
    """Defines a tool parameter with validation rules."""
    name: str
    param_type: Type
    required: bool = True
    description: str = ""
    default: Any = None
    validation_rules: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Abstract base class for all business tools."""
    
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Return the unique name for this tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of what this tool does."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Return the parameters this tool accepts."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given parameters."""
        pass
    
    def validate_parameters(self, **kwargs) -> Optional[str]:
        """
        Validate parameters before execution.
        
        Returns:
            None if valid, error message if invalid
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"
            
            if param.name in kwargs:
                value = kwargs[param.name]
                # Allow None for optional parameters
                if value is not None and not isinstance(value, param.param_type):
                    return f"Parameter {param.name} must be of type {param.param_type.__name__}"
                
                # Custom validation rules
                if param.validation_rules:
                    error = self._validate_custom_rules(param, value)
                    if error:
                        return error
        
        return None
    
    def _validate_custom_rules(self, param: ToolParameter, value: Any) -> Optional[str]:
        """Apply custom validation rules."""
        rules = param.validation_rules or {}
        
        if 'min_length' in rules and hasattr(value, '__len__'):
            min_length = rules['min_length']
            if isinstance(min_length, int) and len(value) < min_length:
                return f"Parameter {param.name} must be at least {min_length} characters"
        
        if 'max_length' in rules and hasattr(value, '__len__'):
            max_length = rules['max_length']
            if isinstance(max_length, int) and len(value) > max_length:
                return f"Parameter {param.name} must be at most {max_length} characters"
        
        if 'min_value' in rules and isinstance(value, (int, float)):
            min_value = rules['min_value']
            if isinstance(min_value, (int, float)) and value < min_value:
                return f"Parameter {param.name} must be at least {min_value}"
        
        if 'max_value' in rules and isinstance(value, (int, float)):
            max_value = rules['max_value']
            if isinstance(max_value, (int, float)) and value > max_value:
                return f"Parameter {param.name} must be at most {max_value}"
        
        if 'pattern' in rules and isinstance(value, str):
            import re
            pattern = rules['pattern']
            if isinstance(pattern, str) and not re.match(pattern, value):
                return f"Parameter {param.name} format is invalid"
        
        return None
    
    def get_full_description(self) -> str:
        """Get description with parameters automatically included."""
        base_desc = self.description
        
        if not self.parameters:
            return base_desc
            
        # Separate required and optional parameters
        required = [p.name for p in self.parameters if p.required]
        optional = [p.name for p in self.parameters if not p.required]
        
        param_parts = []
        if required:
            param_parts.append(f"requires: {', '.join(required)}")
        if optional:
            param_parts.append(f"optional: {', '.join(optional)}")
        
        if param_parts:
            return f"{base_desc} ({'; '.join(param_parts)})"
        return base_desc

    def get_parameter_schema(self) -> Dict[str, Any]:
        """Return the parameter schema for documentation/introspection."""
        return {
            "tool_name": self.tool_name,
            "description": self.get_full_description(),  # Use full description with params
            "parameters": {
                param.name: {
                    "type": param.param_type.__name__,
                    "required": param.required,
                    "description": param.description,
                    "default": param.default
                }
                for param in self.parameters
            }
        }


class ToolRegistry:
    """Registry for managing available tools dynamically."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a new tool."""
        self._tools[tool.tool_name] = tool
    
    def unregister(self, tool_name: str) -> None:
        """Remove a tool from the registry."""
        if tool_name in self._tools:
            del self._tools[tool_name]
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tools.keys())
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools."""
        return {
            name: tool.get_parameter_schema() 
            for name, tool in self._tools.items()
        }
    
    def get_tools_for_llm_planning(self) -> str:
        """Get tool descriptions formatted for LLM planning prompts."""
        descriptions = []
        for name, tool in self._tools.items():
            descriptions.append(f"- {name}: {tool.get_full_description()}")
        return "\n".join(descriptions)
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool with validation."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found. Available: {self.list_tools()}",
                data=None
            )
        
        # Validate parameters
        validation_error = tool.validate_parameters(**kwargs)
        if validation_error:
            return ToolResult(
                success=False,
                error=f"Parameter validation failed: {validation_error}",
                data=None
            )
        
        # Execute tool
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                data=None
            )