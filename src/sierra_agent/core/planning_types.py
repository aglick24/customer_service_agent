"""Planning-specific data types

These types are separated from basic data types to avoid circular imports
with tool orchestrator and other components.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sierra_agent.data.data_types import BusinessData, ToolResult, Order, Product
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator


@dataclass
class ExecutedStep:
    """Record of a completed execution step."""
    tool_name: str
    parameters: Dict[str, Any]
    result: ToolResult
    executed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def was_successful(self) -> bool:
        return self.result.success
    
    @property
    def result_data(self) -> Optional[BusinessData]:
        return self.result.data if self.result.success else None


@dataclass
class ConversationContext:
    """Unified context system - replaces all other context approaches."""
    # Core business data
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    order_number: Optional[str] = None
    current_order: Optional[Order] = None
    found_products: List[Product] = field(default_factory=list)
    search_query: Optional[str] = None
    customer_preferences: List[str] = field(default_factory=list)
    
    # Consolidated context storage
    interaction_summaries: List[str] = field(default_factory=list)  # Replaces MinimalHistoryItem
    metadata: Dict[str, Union[str, int, float, bool, List[str]]] = field(default_factory=dict)  # Replaces context_storage
    
    def update_from_result(self, result: ToolResult) -> None:
        """Update context with new tool result data."""
        if not result.success or not result.data:
            return
            
        if isinstance(result.data, Order):
            self.current_order = result.data
            self.customer_email = result.data.email
            self.order_number = result.data.order_number
        elif isinstance(result.data, list) and result.data and isinstance(result.data[0], Product):
            self.found_products = result.data
        elif isinstance(result.data, Product):
            if result.data not in self.found_products:
                self.found_products.append(result.data)
                
    def get_tool_params(self, tool_name: str, user_input: str = "") -> Dict[str, Any]:
        """Get parameters for a tool using accumulated context."""
        if tool_name == "get_order_status":
            email = self.customer_email or self._extract_email(user_input)
            order_num = self.order_number or self._extract_order_number(user_input)
            name = self.customer_name or self._extract_name(user_input)
            params = {"email": email, "order_number": order_num}
            if name:
                params["name"] = name
            return params
        elif tool_name == "get_product_details":
            if self.current_order:
                return {"skus": self.current_order.products_ordered}
            return {"skus": []}
        elif tool_name == "get_product_info":
            # Extract SKU from user input or use order context
            if self.current_order and self.current_order.products_ordered:
                # If user is asking about their ordered products, return the first SKU
                # For multiple products, the planner should call this tool multiple times
                return {"product_identifier": self.current_order.products_ordered[0]}
            # Otherwise try to extract from user input
            # This is a simple implementation - could be enhanced
            return {"product_identifier": user_input}
        elif tool_name == "search_products":
            query = self.search_query or user_input
            return {"query": query}
        elif tool_name == "get_product_recommendations":
            # If we have order context, use the order products as preferences for recommendations
            if self.current_order and self.current_order.products_ordered:
                # Convert order SKUs to product preferences by getting product names
                product_preferences = []
                for sku in self.current_order.products_ordered:
                    # Use the SKU directly as a preference term
                    product_preferences.append(sku)
                return {"category": None, "preferences": product_preferences}
            else:
                return {"category": None, "preferences": self.customer_preferences}
        # elif tool_name == "get_order_history":  # COMMENTED OUT - Not needed for assignment
        #     email = self.customer_email or self._extract_email(user_input)
        #     return {"email": email, "limit": 10}
        else:
            return {}
    
    def has_required_params(self, tool_name: str, params: Dict[str, Any]) -> bool:
        """Check if we have sufficient parameters for a tool."""
        if tool_name == "get_order_status":
            return bool(params.get("email") and params.get("order_number"))
        elif tool_name == "get_product_details":
            return bool(params.get("skus"))
        elif tool_name == "search_products":
            return bool(params.get("query"))
        elif tool_name == "get_product_info":
            return bool(params.get("product_identifier"))
        # elif tool_name == "get_order_history":  # COMMENTED OUT - Not needed for assignment
        #     return bool(params.get("email"))
        else:
            return True
            
    def _extract_email(self, text: str) -> Optional[str]:
        """Simple email extraction."""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None
    
    def _extract_order_number(self, text: str) -> Optional[str]:
        """Simple order number extraction."""
        match = re.search(r'#?([A-Z]\d+)', text, re.IGNORECASE)
        if match:
            # Always return with # prefix to match data format
            return f"#{match.group(1)}"
        return None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Simple name extraction - look for proper names."""
        # Look for patterns like "I'm John", "My name is Jane", "John Smith", etc.
        patterns = [
            r"(?:I'm|I am|my name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$",  # Just a name by itself
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # First Last name pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.strip(), re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    # Unified context methods - replace all scattered context systems
    def to_available_data(self) -> Dict[str, Union[Order, List[Product], str, int, float, bool, List[str]]]:
        """Replace Conversation.get_available_data() calls"""
        available: Dict[str, Union[Order, List[Product], str, int, float, bool, List[str]]] = {}
        if self.current_order:
            available["current_order"] = self.current_order
        if self.found_products:
            available["recent_products"] = self.found_products
        if self.customer_email:
            available["customer_email"] = self.customer_email
        if self.order_number:
            available["order_number"] = self.order_number
        available.update(self.metadata)  # Include generic metadata
        return available
    
    def add_interaction_summary(self, summary: str) -> None:
        """Replace MinimalHistoryItem.append() calls"""
        self.interaction_summaries.append(summary)
        if len(self.interaction_summaries) > 5:  # Keep last 5
            self.interaction_summaries = self.interaction_summaries[-5:]
    
    def get_prompt_context(self) -> str:
        """Replace all history formatting methods"""
        if not self.interaction_summaries:
            return ""
        return "Recent Context:\n" + "\n".join(f"- {summary}" for summary in self.interaction_summaries) + "\n\n"
    
    def get_conversation_context_string(self, phase: str, topic: str, executed_steps: List) -> str:
        """Replace manual context string building in adaptive_planning_service"""
        context_parts = []
        context_parts.append(f"Phase: {phase}")
        context_parts.append(f"Topic: {topic}")
        if executed_steps:
            step_names = [step.tool_name if hasattr(step, 'tool_name') else str(step) for step in executed_steps]
            context_parts.append(f"Executed: {step_names}")
        return ", ".join(context_parts)
    
    def get_tool_validation_context(self, original_request: str) -> str:
        """Replace manual context strings for validation"""
        return f"Original request: {original_request}"


@dataclass
class EvolvingPlan:
    """A plan that evolves during execution and across conversation turns."""
    plan_id: str
    original_request: str
    context: ConversationContext = field(default_factory=ConversationContext)
    executed_steps: List[ExecutedStep] = field(default_factory=list)
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def determine_next_action(self, user_input: str) -> Optional[str]:
        """Determine what tool to execute based on user input and context."""
        user_lower = user_input.lower()
        
        # Order-related requests
        if any(word in user_lower for word in ["order", "track", "#w"]):
            if not self.context.current_order:
                return "get_order_status"
            elif "product" in user_lower:
                return "get_product_details"
        
        # Product-related requests
        elif any(word in user_lower for word in ["product", "recommend", "search"]):
            if "recommend" in user_lower and self.context.current_order:
                return "get_product_recommendations"
            else:
                return "search_products"
                
        # Promotion requests
        elif any(word in user_lower for word in ["discount", "promotion", "early risers"]):
            return "get_early_risers_promotion"
            
        return None
    
    def execute_action(self, action: str, user_input: str, tool_orchestrator: ToolOrchestrator, enhanced_params: Optional[Dict[str, Any]] = None) -> Optional[ExecutedStep]:
        """Execute an action using current context."""
        # Update context with current user input
        if "search" in user_input.lower() or "find" in user_input.lower():
            self.context.search_query = user_input
            
        # Extract and store any new information from user input
        self._update_context_from_user_input(user_input)
            
        # Use enhanced parameters if provided, otherwise get from context
        if enhanced_params:
            params = enhanced_params
        else:
            params = self.context.get_tool_params(action, user_input)
        
        # Check if we have enough parameters
        if not self.context.has_required_params(action, params):
            return None
            
        # Execute the tool
        result = tool_orchestrator.execute_tool(action, **params)
        
        # Create execution record
        executed_step = ExecutedStep(
            tool_name=action,
            parameters=params,
            result=result
        )
        
        # Update plan state
        self.executed_steps.append(executed_step)
        if result.success:
            self.context.update_from_result(result)
        
        return executed_step
    
    def _update_context_from_user_input(self, user_input: str) -> None:
        """Extract and store any new information from user input."""
        # Extract email if we don't have one
        if not self.context.customer_email:
            email = self.context._extract_email(user_input)
            if email:
                self.context.customer_email = email
                
        # Extract order number if we don't have one
        if not self.context.order_number:
            order_num = self.context._extract_order_number(user_input)
            if order_num:
                self.context.order_number = order_num
                
        # Extract name if we don't have one
        if not self.context.customer_name:
            name = self.context._extract_name(user_input)
            if name:
                self.context.customer_name = name
    
    def print_plan(self) -> None:
        """Print current plan state."""
        print(f"\n📋 EVOLVING PLAN: {self.plan_id}")
        print(f"🎯 Original Request: {self.original_request}")
        print(f"📊 Status: {'COMPLETE' if self.is_complete else 'IN_PROGRESS'}")
        
        if self.executed_steps:
            print(f"✅ Executed Steps:")
            for step in self.executed_steps:
                icon = "✅" if step.was_successful else "❌"
                print(f"  {icon} {step.tool_name}")
        
        context_keys = []
        if self.context.customer_email: context_keys.append("email")
        if self.context.current_order: context_keys.append("order")
        if self.context.found_products: context_keys.append("products")
        if context_keys:
            print(f"💾 Context: {', '.join(context_keys)}")
        print()