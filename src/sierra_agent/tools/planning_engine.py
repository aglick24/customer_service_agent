"""
Planning Engine

This module generates strategic execution plans for customer requests instead of
reactive tool execution. It analyzes customer needs and creates multi-step plans
that can handle complex scenarios with conditional logic and dependencies.
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass

from ..data.data_types import (
    Plan, PlanStep, PlanStepType, PlanPriority, PlanStatus,
    PlanningRequest, IntentType, BusinessRule
)
from ..ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class PlanningStrategy:
    """Strategy for plan generation."""
    name: str
    description: str
    complexity_level: str  # SIMPLE, MODERATE, COMPLEX
    max_steps: int
    supports_conditionals: bool
    supports_loops: bool
    estimated_planning_time: float  # in seconds


class PlanningEngine:
    """Generates strategic execution plans for customer requests."""
    
    def __init__(self, thinking_llm: Optional[Union[Any, 'LLMClient']] = None) -> None:
        print("🧠 [PLANNING] Initializing Planning Engine...")
        
        # Initialize LLM client for intelligent planning
        self.llm_client = thinking_llm or self._initialize_llm_client()
        print("🧠 [PLANNING] LLM client initialized")
        
        # Planning strategies for different complexity levels
        self.planning_strategies = self._initialize_planning_strategies()
        print(f"🧠 [PLANNING] Initialized {len(self.planning_strategies)} planning strategies")
        
        # Plan templates for common scenarios
        self.plan_templates = self._initialize_plan_templates()
        print(f"🧠 [PLANNING] Loaded {len(self.plan_templates)} plan templates")
        
        # Business rules cache
        self.business_rules_cache: Dict[str, BusinessRule] = {}
        
        print("🧠 [PLANNING] Planning Engine initialization complete!")
        logger.info("Planning Engine initialized successfully")
    
    def _initialize_llm_client(self) -> LLMClient:
        """Initialize the LLM client for planning."""
        try:
            return LLMClient()
        except Exception as e:
            print(f"❌ [PLANNING] Error initializing LLM client: {e}")
            logger.error(f"Error initializing LLM client: {e}")
            return self._create_mock_llm_client()
    
    def _create_mock_llm_client(self):
        """Create a mock LLM client for fallback."""
        class MockLLMClient:
            def generate_plan(self, request):
                return self._generate_simple_plan(request)
            
            def _generate_simple_plan(self, request):
                # Simple fallback planning logic
                steps = [
                    PlanStep(
                        step_id="step_1",
                        step_type=PlanStepType.TOOL_EXECUTION,
                        name="Analyze Request",
                        description="Analyze customer request to understand needs",
                        tool_name="analyze_request",
                        parameters={"input": request.customer_input}
                    ),
                    PlanStep(
                        step_id="step_2",
                        step_type=PlanStepType.TOOL_EXECUTION,
                        name="Execute Primary Tool",
                        description="Execute the main tool for the request",
                        tool_name="execute_primary_tool",
                        parameters={"request": request.customer_input},
                        dependencies=["step_1"]
                    )
                ]
                
                return Plan(
                    plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                    name="Simple Fallback Plan",
                    description="Basic plan for customer request",
                    customer_request=request.customer_input,
                    steps=steps,
                    estimated_duration=30
                )
        
        return MockLLMClient()
    
    def _initialize_planning_strategies(self) -> Dict[str, PlanningStrategy]:
        """Initialize different planning strategies."""
        return {
            "simple": PlanningStrategy(
                name="Simple Linear",
                description="Linear execution of tools without complex logic",
                complexity_level="SIMPLE",
                max_steps=5,
                supports_conditionals=False,
                supports_loops=False,
                estimated_planning_time=2.0
            ),
            "moderate": PlanningStrategy(
                name="Conditional Planning",
                description="Planning with conditional branches based on results",
                complexity_level="MODERATE",
                max_steps=10,
                supports_conditionals=True,
                supports_loops=False,
                estimated_planning_time=5.0
            ),
            "complex": PlanningStrategy(
                name="Advanced Planning",
                description="Complex planning with loops, conditionals, and optimization",
                complexity_level="COMPLEX",
                max_steps=20,
                supports_conditionals=True,
                supports_loops=True,
                estimated_planning_time=10.0
            )
        }
    
    def _initialize_plan_templates(self) -> Dict[str, Plan]:
        """Initialize plan templates for common scenarios."""
        templates = {}
        
        # Order status template
        order_status_steps = [
            PlanStep(
                step_id="validate_order_id",
                step_type=PlanStepType.VALIDATION,
                name="Validate Order ID",
                description="Validate the provided order ID format",
                tool_name="validate_order_id",
                parameters={}
            ),
            PlanStep(
                step_id="get_order_status",
                step_type=PlanStepType.TOOL_EXECUTION,
                name="Get Order Status",
                description="Retrieve current order status",
                tool_name="get_order_status",
                parameters={},
                dependencies=["validate_order_id"]
            ),
            PlanStep(
                step_id="get_shipping_info",
                step_type=PlanStepType.TOOL_EXECUTION,
                name="Get Shipping Information",
                description="Retrieve shipping and tracking information",
                tool_name="get_shipping_info",
                parameters={},
                dependencies=["get_order_status"]
            )
        ]
        
        templates["order_status"] = Plan(
            plan_id="template_order_status",
            name="Order Status Inquiry",
            description="Handle order status and shipping inquiries",
            customer_request="Order status inquiry",
            steps=order_status_steps,
            estimated_duration=45
        )
        
        # Product inquiry template
        product_inquiry_steps = [
            PlanStep(
                step_id="analyze_product_request",
                step_type=PlanStepType.TOOL_EXECUTION,
                name="Analyze Product Request",
                description="Analyze customer's product needs",
                tool_name="analyze_product_request",
                parameters={}
            ),
            PlanStep(
                step_id="search_products",
                step_type=PlanStepType.TOOL_EXECUTION,
                name="Search Products",
                description="Search for matching products",
                tool_name="search_products",
                parameters={},
                dependencies=["analyze_product_request"]
            ),
            PlanStep(
                step_id="get_recommendations",
                step_type=PlanStepType.TOOL_EXECUTION,
                name="Get Recommendations",
                description="Provide product recommendations",
                tool_name="get_product_recommendations",
                parameters={},
                dependencies=["search_products"]
            )
        ]
        
        templates["product_inquiry"] = Plan(
            plan_id="template_product_inquiry",
            name="Product Inquiry",
            description="Handle product searches and recommendations",
            customer_request="Product inquiry",
            steps=product_inquiry_steps,
            estimated_duration=60
        )
        
        return templates
    
    def generate_plan(self, request: PlanningRequest) -> Plan:
        """Generate an execution plan for a customer request."""
        print(f"🧠 [PLANNING] Generating plan for: '{request.customer_input[:50]}{'...' if len(request.customer_input) > 50 else ''}'")
        
        start_time = time.time()
        
        try:
            # Determine planning strategy based on request complexity
            strategy = self._select_planning_strategy(request)
            print(f"🧠 [PLANNING] Selected strategy: {strategy.name}")
            
            # Check if we have a suitable template
            template = self._find_suitable_template(request)
            if template:
                print(f"🧠 [PLANNING] Using template: {template.name}")
                plan = self._customize_template(template, request)
            else:
                print(f"🧠 [PLANNING] Generating custom plan...")
                plan = self._generate_custom_plan(request, strategy)
            
            # Validate and optimize the plan
            plan = self._validate_and_optimize_plan(plan, request)
            
            planning_time = time.time() - start_time
            print(f"🧠 [PLANNING] Plan generated in {planning_time:.2f} seconds")
            print(f"🧠 [PLANNING] Plan contains {len(plan.steps)} steps")
            
            return plan
            
        except Exception as e:
            print(f"❌ [PLANNING] Error generating plan: {e}")
            logger.error(f"Error generating plan: {e}")
            return self._generate_fallback_plan(request)
    
    def _select_planning_strategy(self, request: PlanningRequest) -> PlanningStrategy:
        """Select the appropriate planning strategy based on request complexity."""
        # Simple heuristics for strategy selection
        input_length = len(request.customer_input)
        urgency = request.urgency_level
        
        if urgency == "CRITICAL" or input_length > 200:
            return self.planning_strategies["complex"]
        elif input_length > 100 or len(request.available_tools) > 5:
            return self.planning_strategies["moderate"]
        else:
            return self.planning_strategies["simple"]
    
    def _find_suitable_template(self, request: PlanningRequest) -> Optional[Plan]:
        """Find a suitable plan template for the request."""
        # Simple keyword matching for template selection
        input_lower = request.customer_input.lower()
        
        if any(keyword in input_lower for keyword in ["order", "status", "tracking", "shipping"]):
            return self.plan_templates["order_status"]
        elif any(keyword in input_lower for keyword in ["product", "item", "gear", "equipment", "recommend"]):
            return self.plan_templates["product_inquiry"]
        
        return None
    
    def _customize_template(self, template: Plan, request: PlanningRequest) -> Plan:
        """Customize a template plan for the specific request."""
        # Create a copy of the template
        customized_plan = Plan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=template.name,
            description=template.description,
            customer_request=request.customer_input,
            steps=template.steps.copy(),
            estimated_duration=template.estimated_duration,
            priority=self._determine_priority(request)
        )
        
        # Customize step parameters based on the request
        for step in customized_plan.steps:
            if step.tool_name:
                step.parameters.update(self._customize_step_parameters(step, request))
        
        return customized_plan
    
    def _customize_step_parameters(self, step: PlanStep, request: PlanningRequest) -> Dict[str, Any]:
        """Customize step parameters based on the request."""
        params = {}
        
        if step.tool_name == "validate_order_id":
            # Extract order ID from request if present
            import re
            order_match = re.search(r'order[:\s]*([A-Z0-9]+)', request.customer_input, re.IGNORECASE)
            if order_match:
                params["order_id"] = order_match.group(1)
        
        elif step.tool_name == "search_products":
            # Extract product keywords
            params["query"] = request.customer_input
            params["category"] = self._extract_product_category(request.customer_input)
        
        return params
    
    def _extract_product_category(self, text: str) -> Optional[str]:
        """Extract product category from text."""
        categories = {
            "hiking": ["hiking", "backpacking", "trail", "mountain"],
            "camping": ["camping", "tent", "sleeping", "outdoor living"],
            "clothing": ["clothing", "jacket", "pants", "shirt", "boots"],
            "equipment": ["equipment", "gear", "tools", "accessories"]
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return None
    
    def _generate_custom_plan(self, request: PlanningRequest, strategy: PlanningStrategy) -> Plan:
        """Generate a custom plan using the LLM client."""
        try:
            # Use LLM to generate plan
            plan = self.llm_client.generate_plan(request)
            plan.plan_id = f"plan_{uuid.uuid4().hex[:8]}"
            plan.priority = self._determine_priority(request)
            return plan
        except Exception as e:
            print(f"⚠️ [PLANNING] LLM planning failed, using fallback: {e}")
            return self._generate_fallback_plan(request)
    
    def _generate_fallback_plan(self, request: PlanningRequest) -> Plan:
        """Generate a simple fallback plan."""
        steps = [
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL_EXECUTION,
                name="Process Request",
                description="Process the customer request using available tools",
                tool_name="process_customer_request",
                parameters={"input": request.customer_input}
            )
        ]
        
        return Plan(
            plan_id=f"fallback_{uuid.uuid4().hex[:8]}",
            name="Fallback Plan",
            description="Simple fallback plan for customer request",
            customer_request=request.customer_input,
            steps=steps,
            estimated_duration=30,
            priority=PlanPriority.LOW
        )
    
    def _determine_priority(self, request: PlanningRequest) -> PlanPriority:
        """Determine the priority level for a plan."""
        urgency = request.urgency_level
        
        if urgency == "CRITICAL":
            return PlanPriority.CRITICAL
        elif urgency == "HIGH":
            return PlanPriority.HIGH
        elif urgency == "LOW":
            return PlanPriority.LOW
        else:
            return PlanPriority.MEDIUM
    
    def _validate_and_optimize_plan(self, plan: Plan, request: PlanningRequest) -> Plan:
        """Validate and optimize the generated plan."""
        print(f"🔍 [PLANNING] Validating and optimizing plan...")
        
        # Validate dependencies
        plan = self._validate_dependencies(plan)
        
        # Optimize step order
        plan = self._optimize_step_order(plan)
        
        # Estimate duration
        plan.estimated_duration = self._estimate_plan_duration(plan)
        
        print(f"🔍 [PLANNING] Plan validation and optimization complete")
        return plan
    
    def _validate_dependencies(self, plan: Plan) -> Plan:
        """Validate that all step dependencies are valid."""
        step_ids = {step.step_id for step in plan.steps}
        
        for step in plan.steps:
            invalid_deps = [dep for dep in step.dependencies if dep not in step_ids]
            if invalid_deps:
                print(f"⚠️ [PLANNING] Removing invalid dependencies: {invalid_deps}")
                step.dependencies = [dep for dep in step.dependencies if dep in step_ids]
        
        return plan
    
    def _optimize_step_order(self, plan: Plan) -> Plan:
        """Optimize the order of steps for better execution."""
        # Simple topological sort for dependencies
        steps_dict = {step.step_id: step for step in plan.steps}
        visited = set()
        temp_visited = set()
        ordered_steps = []
        
        def visit(step_id):
            if step_id in temp_visited:
                raise ValueError("Circular dependency detected")
            if step_id in visited:
                return
            
            temp_visited.add(step_id)
            step = steps_dict[step_id]
            
            for dep in step.dependencies:
                visit(dep)
            
            temp_visited.remove(step_id)
            visited.add(step_id)
            ordered_steps.append(step)
        
        for step in plan.steps:
            if step.step_id not in visited:
                visit(step.step_id)
        
        plan.steps = ordered_steps
        return plan
    
    def _estimate_plan_duration(self, plan: Plan) -> int:
        """Estimate the total duration of plan execution."""
        total_duration = 0
        
        for step in plan.steps:
            if step.step_type == PlanStepType.TOOL_EXECUTION:
                total_duration += 15  # Base tool execution time
            elif step.step_type == PlanStepType.VALIDATION:
                total_duration += 5   # Validation time
            elif step.step_type == PlanStepType.CONDITIONAL_BRANCH:
                total_duration += 10  # Decision time
            else:
                total_duration += 10  # Default time
        
        return total_duration
    
    def get_planning_statistics(self) -> Dict[str, Any]:
        """Get statistics about the planning engine."""
        return {
            "strategies": len(self.planning_strategies),
            "templates": len(self.plan_templates),
            "business_rules_cache_size": len(self.business_rules_cache)
        }
