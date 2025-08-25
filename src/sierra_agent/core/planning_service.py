"""
Planning Service

Handles intelligent plan generation and analysis for customer service requests.
Extracted from SierraAgent to improve separation of concerns.
"""

import json
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
        print("🎯 [PLANNING] Initializing planning service with unified LLM service...")
        
        # Store dependencies for intelligent planning
        self.llm_service = llm_service
        self.tool_orchestrator = tool_orchestrator
        
        # Initialize LLM service if not provided
        if self.llm_service is None:
            try:
                from ..ai.llm_service import LLMService
                self.llm_service = LLMService()
                print("🎯 [PLANNING] Unified LLM service initialized for planning")
            except Exception as e:
                print(f"⚠️ [PLANNING] Could not initialize LLM service: {e}")
                self.llm_service = None
        
        print("🎯 [PLANNING] Planning service initialized successfully")
        logger.info("PlanningService initialized with unified LLM service")

    def generate_plan(self, user_input: str, session_id: str = None, available_data: Dict[str, Any] = None) -> MultiTurnPlan:
        """Generate a comprehensive plan for handling the user request."""
        print(f"🧠 [PLANNING] Generating plan for: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")

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

            print(f"🧠 [PLANNING] Generated plan '{plan_id}' with {len(steps)} steps")
            return plan

        except Exception as e:
            print(f"❌ [PLANNING] Error generating plan: {e}")
            # Create a fallback plan
            return self._create_fallback_plan(user_input)

    def _analyze_request(self, user_input: str) -> Dict[str, Any]:
        """Analyze the user request to understand what needs to be done."""
        print(f"🔍 [PLANNING] Analyzing request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")

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

        print(f"🔍 [PLANNING] Request type: {context['request_type']}, complexity: {context['complexity']}")
        return context

    def _generate_plan_steps(self, user_input: str, context: Dict[str, Any], available_data: Dict[str, Any] = None) -> List[PlanStep]:
        """Generate specific plan steps based on the request context and available data."""
        steps = []
        request_type = context.get("request_type", "general")
        available_data = available_data or {}

        if request_type == "order_status":
            # Check if we already have order data
            if "current_order" in available_data:
                print(f"🔍 [PLANNING] Found existing order data, checking what user wants to know")
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

        print(f"🛠️ [PLANNING] Generated {len(steps)} plan steps for {request_type}")
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

    def should_use_planning(self, user_input: str) -> bool:
        """Determine if a request needs full planning or can use reactive mode."""
        # Simple heuristics for planning vs reactive mode
        user_lower = user_input.lower()
        
        # Complex requests need planning
        if len(user_input.split()) > 20:
            return True
            
        # Multi-part requests need planning  
        if any(word in user_lower for word in ["and", "also", "plus", "additionally"]):
            return True
            
        # Complex business operations need planning
        if any(phrase in user_lower for phrase in [
            "check my order and", "order status and", "recommend and",
            "search for products and", "promotion and"
        ]):
            return True
            
        # Simple single requests can be reactive
        return False
    
    def suggest_steps_with_llm(self, user_input: str, available_data: Dict[str, Any], conversation_context=None) -> List[str]:
        """Use unified LLM service to intelligently suggest required steps based on context."""
        print(f"🤖 [PLANNING] Using unified LLM service to suggest steps for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        if not self.llm_service:
            print("⚠️ [PLANNING] No LLM service available, falling back to rule-based planning")
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
            
            print(f"🤖 [PLANNING] Unified LLM service suggested {len(suggested_steps)} steps: {suggested_steps}")
            return suggested_steps
                
        except Exception as e:
            print(f"❌ [PLANNING] Error in unified LLM planning: {e}")
            print("⚠️ [PLANNING] Falling back to rule-based planning")
            return self.suggest_steps_rule_based(user_input, available_data)
    
    def suggest_steps_rule_based(self, user_input: str, available_data: Dict[str, Any]) -> List[str]:
        """Rule-based step suggestion as fallback."""
        print(f"🔍 [PLANNING] Using rule-based planning for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
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
            
        print(f"🔍 [PLANNING] Rule-based planning suggested {len(steps)} steps: {steps}")
        return steps
    
    def analyze_planning_context(self, user_input: str, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation context to determine planning requirements."""
        print(f"🧠 [PLANNING] Analyzing planning context for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        available_data = conversation_data.get("available_data", {})
        request_analysis = self._analyze_user_request(user_input, available_data)
        
        # Choose planning method based on complexity and availability
        use_llm = (
            self.llm_client is not None and 
            (len(available_data) > 0 or self._is_complex_request(user_input))
        )
        
        if use_llm:
            suggested_steps = self.suggest_steps_with_llm(user_input, available_data)
        else:
            suggested_steps = self.suggest_steps_rule_based(user_input, available_data)
        
        return {
            "available_data": available_data,
            "request_needs": request_analysis["needs"],
            "references_previous": request_analysis["references_previous"],
            "suggested_steps": suggested_steps,
            "planning_method": "llm" if use_llm else "rule_based",
            "conversation_context": conversation_data
        }
    
    def _get_available_tools_description(self) -> str:
        """Get description of available tools from the orchestrator."""
        if not self.tool_orchestrator:
            return "No tool orchestrator available - using default tools"
        
        try:
            available_tools = self.tool_orchestrator.get_available_tools()
            tool_descriptions = []
            
            # Map tool names to descriptions
            tool_info = {
                "get_order_status": "Look up order information by order number and email",
                "search_products": "Find products matching customer criteria",
                "get_product_details": "Get detailed information for specific products", 
                "get_product_recommendations": "Find products similar to or related to existing ones",
                "get_early_risers_promotion": "Check for available promotions and discounts",
                "get_company_info": "Get general company information",
                "get_contact_info": "Get contact information for customer service",
                "get_policies": "Get information about company policies"
            }
            
            for tool in available_tools:
                if tool in tool_info:
                    tool_descriptions.append(f"- {tool}: {tool_info[tool]}")
                else:
                    tool_descriptions.append(f"- {tool}: Available business tool")
            
            return "\n".join(tool_descriptions)
            
        except Exception as e:
            print(f"⚠️ [PLANNING] Error getting tool descriptions: {e}")
            return "Error retrieving available tools"
    
    def _get_available_tool_names(self) -> List[str]:
        """Get list of available tool names."""
        if not self.tool_orchestrator:
            # Return default tools if no orchestrator
            return ["get_order_status", "search_products", "get_product_details", 
                   "get_product_recommendations", "get_early_risers_promotion", 
                   "get_company_info", "get_contact_info", "get_policies"]
        
        try:
            return self.tool_orchestrator.get_available_tools()
        except Exception as e:
            print(f"⚠️ [PLANNING] Error getting available tools: {e}")
            return []
    
    def _format_available_data_for_llm(self, available_data: Dict[str, Any]) -> str:
        """Format available data for LLM context."""
        if not available_data:
            return "No previous context available."
        
        formatted = []
        for key, value in available_data.items():
            if key == "current_order" and hasattr(value, 'order_number'):
                formatted.append(f"- Current Order: {value.order_number} for {value.customer_name}")
            elif key == "recent_products" and isinstance(value, list):
                formatted.append(f"- Recent Products: {len(value)} products found")
            else:
                formatted.append(f"- {key}: {type(value).__name__} data available")
        
        return "\n".join(formatted) if formatted else "No specific context data."
    
    def _analyze_user_request(self, user_input: str, available_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what the user is asking for."""
        user_lower = user_input.lower()
        needs = []
        references_previous = False
        
        # Check for references to previous context
        if any(ref in user_lower for ref in ["my order", "the order", "my", "that order"]):
            references_previous = True
            
        # Determine what user needs
        if any(word in user_lower for word in ["status", "tracking", "delivery", "shipped"]):
            needs.append("order_status")
        if any(word in user_lower for word in ["products", "items", "gear", "details"]):
            needs.append("product_info")
        if any(word in user_lower for word in ["related", "similar", "like", "recommend"]):
            needs.append("related_products")
        if any(word in user_lower for word in ["promotion", "discount", "code", "sale"]):
            needs.append("promotion_info")
            
        return {
            "needs": needs,
            "references_previous": references_previous,
            "user_input_lower": user_lower
        }
    
    def _is_complex_request(self, user_input: str) -> bool:
        """Determine if a request is complex enough to warrant LLM planning."""
        user_lower = user_input.lower()
        
        # Complex indicators
        complexity_indicators = [
            len(user_input.split()) > 10,  # Long requests
            any(word in user_lower for word in ["and", "but", "also", "plus"]),  # Multiple requests
            any(word in user_lower for word in ["similar", "related", "like", "recommend"]),  # Relational requests
            user_input.count("?") > 1,  # Multiple questions
        ]
        
        return any(complexity_indicators)
    
    def update_plan_with_llm_service(self, plan: MultiTurnPlan, execution_results: List[ToolResult]) -> List[str]:
        """Update plan using unified LLM service based on execution results."""
        print(f"🔄 [PLANNING] Updating plan using unified LLM service after {len(execution_results)} execution results")
        
        if not self.llm_service:
            print("⚠️ [PLANNING] No LLM service available for plan updates")
            return []
        
        # Quick check if request appears satisfied
        has_order_data = any(hasattr(result.data, 'order_number') for result in execution_results if result.success and result.data)
        has_product_data = any(isinstance(result.data, list) and len(result.data) > 0 for result in execution_results if result.success and result.data)
        
        user_lower = plan.customer_request.lower()
        
        if (("order" in user_lower or "status" in user_lower) and has_order_data) or \
           (("product" in user_lower or "item" in user_lower) and (has_order_data or has_product_data)):
            print("🔄 [PLANNING] Request appears satisfied with existing results")
            return []
        
        try:
            # Get remaining steps
            remaining_steps = [step.tool_name for step in plan.steps if not step.is_completed]
            
            if not remaining_steps:
                print("🔄 [PLANNING] No remaining steps, no updates needed")
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
            
            print(f"🔄 [PLANNING] Unified LLM service suggested {len(updated_steps)} updated steps: {updated_steps}")
            return updated_steps
                
        except Exception as e:
            print(f"❌ [PLANNING] Error updating plan: {e}")
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