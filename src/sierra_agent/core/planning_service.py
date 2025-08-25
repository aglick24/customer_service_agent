"""
Planning Service

Handles intelligent plan generation and analysis for customer service requests.
Extracted from SierraAgent to improve separation of concerns.
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List

from ..data.data_types import (
    MultiTurnPlan,
    PlanStatus,
    PlanStep,
    ToolResult,
)

logger = logging.getLogger(__name__)

class PlanningService:
    """Service responsible for analyzing requests and generating execution plans."""

    def __init__(self, llm_service=None, tool_orchestrator=None):
        """Initialize the planning service with unified LLM service."""
        
        # Store dependencies for intelligent planning
        self.llm_service = llm_service
        self.tool_orchestrator = tool_orchestrator
        
        # Initialize LLM service if not provided
        if self.llm_service is None:
            try:
                from ..ai.llm_service import LLMService
                self.llm_service = LLMService()
                
            except Exception as e:
                
                self.llm_service = None
        
        logger.info("PlanningService initialized with unified LLM service")

    def generate_plan(self, user_input: str, session_id: str = None, available_data: Dict[str, Any] = None) -> MultiTurnPlan:
        """Generate a comprehensive plan for handling the user request."""
        
        try:
            # Analyze the request to determine what needs to be done
            plan_context = self._analyze_request(user_input)

            # Generate plan steps based on the request and available context
            steps = self._generate_plan_steps(user_input, plan_context, available_data)

            # Create the plan
            plan_id = f"plan_{uuid.uuid4().hex[:8]}"

            # Get request type from context
            request_type = plan_context.get("request_type", "general")

            plan = MultiTurnPlan(
                plan_id=plan_id,
                customer_request=user_input,
                steps=steps,
                status=PlanStatus.PENDING,
                created_at=datetime.now(),
                conversation_context={
                    "session_id": session_id,
                    "original_request": user_input,
                    "request_type": request_type
                }
            )

            return plan

        except Exception as e:
            
            # Create a fallback plan
            return self._create_fallback_plan(user_input)

    def _analyze_request(self, user_input: str) -> Dict[str, Any]:
        """Analyze the user request to understand what needs to be done."""
        
        user_lower = user_input.lower()
        context: Dict[str, Any] = {"request_type": "general", "complexity": "simple"}

        # Detect order-related requests
        if any(keyword in user_lower for keyword in ["order", "track", "delivery", "shipping", "#w", "order number"]):
            context["request_type"] = "order_status"
            # Intent removed - using request_type only

        # Detect product-related requests
        elif any(keyword in user_lower for keyword in ["product", "recommend", "looking for", "need", "buy", "search"]):
            context["request_type"] = "product_inquiry"
            # Intent removed - using request_type only

        # Detect promotion requests
        elif any(keyword in user_lower for keyword in ["discount", "promotion", "code", "early risers", "sale"]):
            context["request_type"] = "promotion"
            # Intent removed - using request_type only

        # Detect complex multi-part requests
        if len(user_input.split()) > 20 or "and" in user_lower or "also" in user_lower:
            context["complexity"] = "complex"

        return context

    def _generate_plan_steps(self, user_input: str, context: Dict[str, Any], available_data: Dict[str, Any] = None) -> List[PlanStep]:
        """Generate specific plan steps based on the request context and available data."""
        steps = []
        request_type = context.get("request_type", "general")
        available_data = available_data or {}

        if request_type == "order_status":
            # Check if we already have order data
            if "current_order" in available_data:
                
                user_lower = user_input.lower()
                if any(word in user_lower for word in ["products", "items", "details", "specific"]):
                    # User wants product details for existing order
                    product_step = PlanStep(
                        step_id=f"step_{uuid.uuid4().hex[:8]}",
                        name="Get Product Details",
                        description="Get detailed information for products in the order",
                        tool_name="get_product_details",
                        parameters={"user_input": user_input}
                    )
                    steps.append(product_step)
                else:
                    # Just format existing order status
                    format_step = PlanStep(
                        step_id=f"step_{uuid.uuid4().hex[:8]}",
                        name="Format Order Status",
                        description="Format existing order information for display",
                        tool_name="format_order_status",
                        parameters={"user_input": user_input}
                    )
                    steps.append(format_step)
            else:
                # Need to get order data first
                extract_step = PlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    name="Extract Order Information",
                    description="Extract email and order number from user input",
                    tool_name="extract_order_info",
                    parameters={"user_input": user_input}
                )
                order_step = PlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    name="Get Order Status",
                    description="Retrieve order status and tracking information",
                    tool_name="get_order_status",
                    parameters={},
                    dependencies=[extract_step.step_id]
                )
                steps.extend([extract_step, order_step])

        elif request_type == "product_inquiry":
            analyze_step = PlanStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                name="Understand Product Needs",
                description="Analyze what the customer is looking for",
                tool_name="analyze_product_request",
                parameters={"user_input": user_input}
            )
            search_step = PlanStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                name="Search Products",
                description="Search and recommend relevant products",
                tool_name="search_products",
                parameters={},
                dependencies=[analyze_step.step_id]
            )
            steps.extend([analyze_step, search_step])

        elif request_type == "promotion":
            steps.append(
                PlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    name="Check Early Risers Promotion",
                    description="Verify time and generate promotion code if eligible",
                    tool_name="get_early_risers_promotion",
                    parameters={"user_input": user_input}
                )
            )

        else:
            # General inquiry - create adaptive plan
            steps.append(
                PlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    name="Handle General Inquiry",
                    description="Provide general customer service assistance",
                    tool_name="handle_general_inquiry",
                    parameters={"user_input": user_input}
                )
            )

        return steps

    def _create_fallback_plan(self, user_input: str) -> MultiTurnPlan:
        """Create a simple fallback plan when plan generation fails."""
        fallback_step = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:8]}",
            name="General Assistance",
            description="Provide general customer service help",
            tool_name="handle_general_inquiry",
            parameters={"user_input": user_input}
        )

        return MultiTurnPlan(
            plan_id=f"fallback_{uuid.uuid4().hex[:8]}",
            # Removed intent field from MultiTurnPlan
            customer_request=user_input,
            steps=[fallback_step],
            status=PlanStatus.PENDING,
            created_at=datetime.now()
        )

    def suggest_steps_with_llm(self, user_input: str, available_data: Dict[str, Any], conversation_context=None) -> List[str]:
        """Use unified LLM service to intelligently suggest required steps based on context."""
        
        if not self.llm_service:
            
            return self.suggest_steps_rule_based(user_input, available_data)
        
        try:
            # Get available tools from orchestrator
            available_tools = self.tool_orchestrator.get_available_tools() if self.tool_orchestrator else []
            
            # Use unified LLM service for planning
            suggested_steps = self.llm_service.generate_planning_suggestions(
                user_input=user_input,
                available_data=available_data,
                available_tools=available_tools,
                conversation_phase="exploration",  # Could get from conversation_context
                current_topic="general",  # Could get from conversation_context
                max_steps=5,
                conversation_context=conversation_context
            )
            
            return suggested_steps
                
        except Exception as e:
            
            return self.suggest_steps_rule_based(user_input, available_data)
    
    def suggest_steps_rule_based(self, user_input: str, available_data: Dict[str, Any]) -> List[str]:
        """Rule-based step suggestion as fallback."""
        
        steps = []
        user_lower = user_input.lower()
        
        # Context-driven step determination
        if any(ref in user_lower for ref in ["my order", "the order", "that order"]):
            if "current_order" in available_data:
                # We have order data, what does user want to do with it?
                if any(word in user_lower for word in ["products", "items", "details"]):
                    steps.append("get_product_details")
                if any(word in user_lower for word in ["related", "similar", "recommend"]):
                    steps.append("get_product_recommendations")
                if any(word in user_lower for word in ["status", "tracking"]):
                    # Order status already known, format response
                    steps.append("format_order_status")
            else:
                # Need to get order first
                steps.append("get_order_status")
        
        elif any(word in user_lower for word in ["products", "gear", "recommend", "show me"]):
            # Generic product request with context-aware enhancement
            if "current_order" in available_data and any(ref in user_lower for ref in ["related", "similar", "like"]):
                # Product search based on order history
                steps.extend(["get_product_details", "get_product_recommendations"])
            else:
                # General product search 
                steps.append("search_products")
        
        elif any(word in user_lower for word in ["promotion", "discount", "code", "sale"]):
            steps.append("get_early_risers_promotion")
        
        # Fallback for unclear requests
        if not steps:
            steps.append("get_company_info")
            
        return steps
    
    def update_plan_with_llm_service(self, plan: MultiTurnPlan, execution_results: List[ToolResult]) -> List[PlanStep]:
        """Update plan using unified LLM service based on execution results."""
        
        if not self.llm_service:
            
            return []
        
        # Quick check if request appears satisfied
        has_order_data = any(hasattr(result.data, 'order_number') for result in execution_results if result.success and result.data)
        has_product_data = any(isinstance(result.data, list) and len(result.data) > 0 for result in execution_results if result.success and result.data)
        
        user_lower = plan.customer_request.lower()
        
        if (("order" in user_lower or "status" in user_lower) and has_order_data) or \
           (("product" in user_lower or "item" in user_lower) and (has_order_data or has_product_data)):
            
            return []
        
        try:
            # Get remaining steps
            remaining_steps = [step.tool_name for step in plan.steps if not step.is_completed]
            
            if not remaining_steps:
                
                return []
            
            # Get available tools
            available_tools = self.tool_orchestrator.get_available_tools() if self.tool_orchestrator else []
            
            # Use unified LLM service for plan updates
            updated_steps = self.llm_service.update_plan_suggestions(
                user_input=plan.customer_request,
                original_plan=plan,
                execution_results=execution_results,
                remaining_steps=remaining_steps,
                available_tools=available_tools
            )
            
            return updated_steps
                
        except Exception as e:
            
            return []
    
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