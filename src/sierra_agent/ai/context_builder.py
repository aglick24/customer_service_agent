"""
Context Builder - Unified LLM Context Assembly

This module provides strongly-typed context building for all LLM interactions,
consolidating the scattered context assembly logic into a clean, maintainable system.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from sierra_agent.data.data_types import (
    Order,
    Product,
    Promotion,
    ToolResult,
)

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of LLM contexts we support."""
    CUSTOMER_SERVICE = "customer_service"  # Main customer response generation
    PLANNING = "planning"  # Tool selection and planning
    PLAN_UPDATE = "plan_update"  # Dynamic plan modification

@dataclass
class MinimalHistoryItem:
    """Minimal conversation history item with preserved identifiers."""
    user_question: str
    tool_result_summary: str
    identifiers: Dict[str, str]  # key-value pairs of important identifiers
    interaction_type: str  # order_lookup, product_search, etc.

@dataclass
class BaseContext:
    """Base context with common fields."""
    user_input: str
    context_type: ContextType
    timestamp: str = field(default_factory=lambda: __import__("datetime").datetime.now().isoformat())

@dataclass
class CustomerServiceContext(BaseContext):
    """Context for customer service response generation."""
    context_type: ContextType = ContextType.CUSTOMER_SERVICE

    # Business data
    tool_results: List[ToolResult] = field(default_factory=list)
    primary_result: Optional[ToolResult] = None

    # Conversation context
    conversation_context: Any = None  # The actual conversation context object

@dataclass
class PlanningContext(BaseContext):
    """Context for intelligent planning and tool selection."""
    context_type: ContextType = ContextType.PLANNING

    # Available data for planning
    available_data: Dict[str, Any] = field(default_factory=dict)
    available_tools: List[str] = field(default_factory=list)

    # Conversation state
    conversation_phase: str = "greeting"
    current_topic: str = "general"

    # Planning constraints
    max_steps: int = 5

    # Minimal history for context-aware planning
    recent_history: List[MinimalHistoryItem] = field(default_factory=list)

@dataclass
class PlanUpdateContext(BaseContext):
    """Context for updating plans based on execution results."""
    context_type: ContextType = ContextType.PLAN_UPDATE

    # Plan information (all fields need defaults due to BaseContext having defaults)
    # Removed original_plan field - no longer needed with EvolvingPlan system
    execution_results: List[ToolResult] = field(default_factory=list)
    remaining_steps: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)

class ContextBuilder:
    """Unified context builder for all LLM interactions."""

    def __init__(self):
        """Initialize context builder."""

        logger.info("ContextBuilder initialized")

    def build_customer_service_context(
        self,
        user_input: str,
        tool_results: Optional[List[ToolResult]] = None,
        conversation_context=None
    ) -> CustomerServiceContext:
        """Build strongly-typed context for customer service responses."""

        tool_results = tool_results or []

        # Find primary result (prioritize business objects over dicts)
        primary_result = self._find_primary_tool_result(tool_results)

        return CustomerServiceContext(
            user_input=user_input,
            tool_results=tool_results,
            primary_result=primary_result,
            conversation_context=conversation_context
        )


    def build_planning_context(
        self,
        user_input: str,
        available_data: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        conversation_phase: str = "greeting",
        current_topic: str = "general",
        max_steps: int = 5,
        conversation_context=None
    ) -> PlanningContext:
        """Build strongly-typed context for planning."""

        # Extract minimal history for context-aware planning
        recent_history = self._extract_minimal_history(conversation_context, limit=2)

        return PlanningContext(
            user_input=user_input,
            available_data=available_data or {},
            available_tools=available_tools or [],
            conversation_phase=conversation_phase,
            current_topic=current_topic,
            max_steps=max_steps,
            recent_history=recent_history
        )


    # Removed build_plan_update_context - no longer needed with EvolvingPlan system


    def _extract_minimal_history(self, conversation_context, limit: int = 2) -> List[MinimalHistoryItem]:
        """Extract minimal conversation history with preserved identifiers."""
        if not conversation_context:
            return []

        try:
            # Get recent messages with tool results
            recent_messages = conversation_context.get_recent_messages_with_tool_results(limit=limit)

            history_items = []
            for message in recent_messages:
                if message.tool_results:
                    # Extract the user question that led to this result
                    user_messages = conversation_context.get_user_messages()
                    user_question = "Previous request"
                    if user_messages:
                        # Get the user message that came before this AI response
                        user_question = user_messages[-1].content if user_messages else "Previous request"

                    # Process each tool result in the message
                    for tool_result in message.tool_results:
                        if tool_result.success and tool_result.data:
                            summary, identifiers, interaction_type = self._summarize_tool_result_with_identifiers(tool_result)

                            history_item = MinimalHistoryItem(
                                user_question=user_question[:50] + "..." if len(user_question) > 50 else user_question,
                                tool_result_summary=summary,
                                identifiers=identifiers,
                                interaction_type=interaction_type
                            )

                            history_items.append(history_item)

            return history_items[-limit:] if len(history_items) > limit else history_items

        except Exception:

            return []

    def _summarize_tool_result_with_identifiers(self, tool_result: ToolResult) -> tuple[str, Dict[str, str], str]:
        """Summarize tool result preserving all identifiers."""
        identifiers = {}
        interaction_type = "unknown"

        if isinstance(tool_result.data, Order):
            order = tool_result.data
            identifiers = {
                "order_number": order.order_number,
                "customer_email": order.email,
                "customer_name": order.customer_name,
                "tracking_number": order.tracking_number or "none"
            }
            # Include product SKUs as identifiers
            if order.products_ordered:
                identifiers["product_skus"] = ", ".join(order.products_ordered)

            summary = f"Found Order {order.order_number} for {order.customer_name} - Status: {order.status}"
            interaction_type = "order_lookup"

        elif isinstance(tool_result.data, Product):
            product = tool_result.data
            identifiers = {
                "product_name": product.product_name,
                "sku": product.sku
            }
            summary = f"Found Product: {product.product_name} ({product.sku})"
            interaction_type = "product_lookup"

        elif isinstance(tool_result.data, list):
            if tool_result.data and isinstance(tool_result.data[0], Product):
                products = tool_result.data
                # Preserve all product identifiers
                identifiers = {
                    "product_count": str(len(products)),
                    "product_names": ", ".join([p.product_name for p in products[:3]]),
                    "skus": ", ".join([p.sku for p in products[:3]])
                }
                if len(products) > 3:
                    identifiers["additional_products"] = str(len(products) - 3)

                summary = f"Found {len(products)} products: {', '.join([p.product_name for p in products[:3]])}"
                if len(products) > 3:
                    summary += f" (and {len(products) - 3} more)"
                interaction_type = "product_search"
            else:
                summary = f"Found {len(tool_result.data)} results"
                identifiers = {"result_count": str(len(tool_result.data))}
                interaction_type = "general_search"

        elif isinstance(tool_result.data, Promotion):
            promo = tool_result.data
            identifiers = {
                "promotion_name": promo.name,
                "discount_code": promo.discount_code,
                "discount_percentage": str(promo.discount_percentage)
            }
            summary = f"Promotion: {promo.name} - {promo.discount_percentage}% off with code {promo.discount_code}"
            interaction_type = "promotion_lookup"

        elif isinstance(tool_result.data, dict):
            # Handle dictionary results - extract any identifiers
            summary = "Retrieved information"
            for key, value in tool_result.data.items():
                if any(id_key in key.lower() for id_key in ["id", "number", "code", "name", "email", "sku"]):
                    identifiers[key] = str(value)
            interaction_type = "data_lookup"

        else:
            summary = f"Retrieved {type(tool_result.data).__name__} data"
            identifiers = {"data_type": type(tool_result.data).__name__}
            interaction_type = "general_lookup"

        return summary, identifiers, interaction_type

    def _find_primary_tool_result(self, tool_results: List[ToolResult]) -> Optional[ToolResult]:
        """Find the most relevant tool result for response generation."""
        if not tool_results:
            return None

        # First check for failed results - they are often the most important for user communication
        for result in tool_results:
            if not result.success and result.error:
                # Failed business operations are high priority for user communication
                return result

        # Prioritize business objects over generic dicts
        business_object_types = (Order, Product, Promotion)

        for result in tool_results:
            if result.success and result.data:
                if isinstance(result.data, business_object_types):
                    return result
                if isinstance(result.data, list) and result.data:
                    if isinstance(result.data[0], business_object_types):
                        return result

        # Fall back to last successful result
        for result in reversed(tool_results):
            if result.success and result.data:

                return result

        return None

class LLMPromptBuilder:
    """Builds LLM prompts from strongly-typed contexts."""

    def __init__(self):
        """Initialize prompt builder."""

    def build_customer_service_prompt(self, context: CustomerServiceContext) -> str:
        """Build customer service prompt from context."""

        # Format business data using existing serialization
        business_data = self._format_business_data(context.tool_results, context.primary_result)

        # Format conversation summary
        history_context = self._format_conversation_summary(context.conversation_context)

        # Construct prompt with clear structure and outdoor personality
        return f"""You are a friendly customer service agent for Sierra Outfitters, a premium outdoor gear retailer. 

BRAND PERSONALITY:
- Show enthusiasm for outdoor activities and adventures
- Include occasional mountain emojis (🏔️) for friendly emphasis
- Reference outdoor themes naturally: trails, peaks, adventures, gear
- Use phrases like "Onward into the unknown!" when appropriate
- Be helpful with an outdoorsy, adventurous spirit

{history_context}Current Customer Request: "{context.user_input}"

Current Business Data:
{business_data}

Instructions:
- Provide a helpful, accurate response using ONLY the business data above
- Reference specific identifiers (order numbers, SKUs, names) exactly as provided
- Be specific and include relevant details from the data
- If referencing previous interactions, use the exact identifiers provided
- If no relevant data is available, explain what information you need
- CRITICAL: Never invent, assume, or hallucinate product details, names, or SKUs not in the data
- CRITICAL: Use the EXACT product names and descriptions as provided in the business data
- If some products are missing from the data, acknowledge what you found and what's missing
- For product recommendations, only suggest items that exist in your actual data
- If asked for recommendations but no recommendation data is provided, offer to look up specific recommendations rather than inventing products
- If the actual products don't match outdoor themes, be honest about what they are
- Include outdoor enthusiasm naturally when appropriate, but accuracy comes first
- NEVER make up product names, SKUs, or descriptions that aren't in the provided business data"""


    def build_planning_prompt(self, context: PlanningContext) -> str:
        """Build planning prompt from context."""

        # Format available data summary
        data_summary = self._format_available_data_summary(context.available_data)

        # Format available tools
        tools_description = self._format_available_tools(context.available_tools)

        # Format minimal history for planning context
        history_context = self._format_minimal_history_for_planning(context.recent_history)

        return f"""You are a customer service planning assistant for Sierra Outfitters, an outdoor gear company with an adventurous spirit. 🏔️
Analyze the customer's request and suggest the specific steps needed to fulfill it.

{history_context}Current Customer Request: "{context.user_input}"
Conversation Phase: {context.conversation_phase}
Current Topic: {context.current_topic}

Available Context Data:
{data_summary}

Available Tools:
{tools_description}

Planning Rules:
1. If customer mentions specific order number/email, use get_order_status tool
2. If we already have order data and customer wants related products, use get_product_recommendations tool  
3. For general product requests, use search_products tool
4. Consider previous interactions and available identifiers to avoid redundant operations
5. Always suggest the minimum necessary steps to fulfill the request
6. Maximum {context.max_steps} steps allowed
7. Only suggest tools that are available in the system

Respond with ONLY a JSON array of tool names from the available tools list, no other text:
["tool1", "tool2"]"""


    def build_plan_update_prompt(self, context: PlanUpdateContext) -> str:
        """Build plan update prompt from context."""

        # Format execution results
        execution_summary = self._format_execution_results(context.execution_results)

        # Format tools
        tools_description = self._format_available_tools(context.available_tools)

        return f"""You are updating a customer service plan based on execution results.

Original Request: "{context.user_input}"
Plan ID: no_plan

Execution Results So Far:
{execution_summary}

Remaining Planned Steps:
{context.remaining_steps}

Available Tools:
{tools_description}

Update Instructions:
1. Only suggest additional tools if the execution results indicate the customer's request is NOT fully satisfied
2. Consider what data we now have available from completed steps
3. Avoid redundant operations
4. Maximum efficiency - suggest the minimum necessary steps

Based on the execution results, should we:
1. Continue with remaining steps as planned
2. Add new steps to handle unexpected results
3. Skip steps that are no longer needed (return empty array)

Respond with ONLY a JSON array of tool names for the next steps:
["tool1", "tool2"]"""


    def _format_minimal_history(self, history_items: List[MinimalHistoryItem]) -> str:
        """Format minimal history with preserved identifiers."""
        if not history_items:
            return ""

        formatted = ["Recent Context:"]
        for item in history_items:
            # Format identifiers for easy reference
            id_parts = []
            for key, value in item.identifiers.items():
                if value and value != "none":
                    id_parts.append(f"{key}: {value}")

            identifier_str = f" ({', '.join(id_parts)})" if id_parts else ""
            formatted.append(f"- {item.tool_result_summary}{identifier_str}")

        return "\n".join(formatted) + "\n\n"

    def _format_conversation_summary(self, conversation_context) -> str:
        """Generate a simple formatted conversation summary for the prompt."""
        if not conversation_context or not hasattr(conversation_context, "get_available_data"):
            return ""

        available_data = conversation_context.get_available_data()
        if not available_data:
            return ""

        summary_parts = []

        # Add order context if available
        if "current_order" in available_data:
            order = available_data["current_order"]
            summary_parts.append(f"Previous: User asked about order {order.order_number} for {order.email}")
            summary_parts.append(f"Response: Found order for {order.customer_name}, status={order.status}, products={', '.join(order.products_ordered)}")

        # Add product search context if available
        if "recent_products" in available_data:
            products = available_data["recent_products"]
            if products:
                product_names = [p.product_name for p in products[:2] if hasattr(p, "product_name")]
                summary_parts.append("Previous: User searched for products")
                summary_parts.append(f"Response: Found products including {', '.join(product_names)}")

        if summary_parts:
            return "Recent Context:\n- " + "\n- ".join(summary_parts) + "\n\n"
        return ""

    def _format_minimal_history_for_planning(self, history_items: List[MinimalHistoryItem]) -> str:
        """Format minimal history for planning context."""
        if not history_items:
            return ""

        formatted = ["Previous Interactions (for context):"]
        for item in history_items:
            # Include interaction type for planning decisions
            formatted.append(f"- {item.interaction_type}: {item.tool_result_summary}")

            # Add key identifiers that might influence planning
            key_identifiers = []
            for key, value in item.identifiers.items():
                if key in ["order_number", "customer_email", "product_skus", "sku"] and value and value != "none":
                    key_identifiers.append(f"{key}: {value}")

            if key_identifiers:
                formatted.append(f"  Available: {', '.join(key_identifiers)}")

        return "\n".join(formatted) + "\n\n"

    def _format_business_data(self, tool_results: List[ToolResult], primary_result: Optional[ToolResult]) -> str:
        """Format business data using existing ToolResult serialization."""
        if not tool_results:
            return "No business data available."

        if primary_result:
            if primary_result.success:
                # Use the excellent existing serialization
                context_data = primary_result.serialize_for_context()
                print(f"📄 LLM CONTEXT DATA:\n{context_data}\n")
                return context_data
            # Handle failed primary result
            error_msg = primary_result.error if primary_result.error else "Operation failed"
            return f"ERROR: {error_msg}"

        # Format multiple results (both successful and failed)
        formatted_results = []
        for i, result in enumerate(tool_results, 1):
            if result.success:
                formatted_results.append(f"Result {i}:\n{result.serialize_for_context()}")
            else:
                # Include failed results with error information
                error_msg = result.error if result.error else "Operation failed"
                formatted_results.append(f"Result {i} (FAILED):\n{error_msg}")

        return "\n\n".join(formatted_results) if formatted_results else "No results available."

    def _format_available_data_summary(self, available_data: Dict[str, Any]) -> str:
        """Format available data for planning context."""
        if not available_data:
            return "No previous context available."

        formatted = []
        for key, value in available_data.items():
            if key == "current_order" and hasattr(value, "order_number"):
                formatted.append(f"- Current Order: {value.order_number} for {value.customer_name}")
            elif key == "recent_products" and isinstance(value, list):
                formatted.append(f"- Recent Products: {len(value)} products found")
            else:
                formatted.append(f"- {key}: {type(value).__name__} data available")

        return "\n".join(formatted)

    def _format_available_tools(self, tools: List[str]) -> str:
        """Format available tools with descriptions from registry."""
        if not tools:
            return "No tools available."

        # Use hardcoded descriptions (tool orchestrator integration removed)
        tool_descriptions = {
            "get_order_status": "Look up order information by order number and email",
            "browse_catalog": "Browse and search Sierra Outfitters product catalog",
            "get_product_info": "Get detailed information for specific products by SKU or name",
            "get_recommendations": "Get personalized product recommendations based on customer context",
            "get_early_risers_promotion": "Check for available promotions and discounts",
            "get_company_info": "Get general company information",
            "get_contact_info": "Get contact information for customer service",
            "get_policies": "Get information about company policies"
        }

        formatted = []
        for tool in tools:
            description = tool_descriptions.get(tool, "Available business tool")
            formatted.append(f"- {tool}: {description}")

        return "\n".join(formatted)

    def _format_execution_results(self, results: List[ToolResult]) -> str:
        """Format execution results for plan update context."""
        if not results:
            return "No execution results yet."

        formatted = []
        for i, result in enumerate(results, 1):
            if result.success:
                data_type = type(result.data).__name__ if result.data else "Unknown"
                formatted.append(f"Step {i}: SUCCESS - Tool executed, returned {data_type}")
            else:
                formatted.append(f"Step {i}: FAILED - Tool failed: {result.error}")

        return "\n".join(formatted)
