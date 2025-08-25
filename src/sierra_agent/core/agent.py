"""
Sierra Agent - Core Agent Implementation

This module implements the core Sierra Agent functionality for customer service,
including intent classification, response generation, and tool orchestration.
"""

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..ai.llm_client import LLMClient
from ..core.conversation import Conversation
from ..data.data_types import (
    IntentType,
    MultiTurnPlan,
    PlanStatus,
    PlanStep,
    ToolResult,
)
from ..tools.tool_orchestrator import ToolOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the Sierra Agent."""

    quality_check_interval: int = 3
    analytics_update_interval: int = 5
    max_conversation_length: int = 50
    enable_quality_monitoring: bool = True
    enable_analytics: bool = True
    # LLM Configuration
    thinking_model: str = "gpt-4o"  # For complex reasoning and planning
    low_latency_model: str = "gpt-4o-mini"  # For fast responses and simple tasks
    enable_dual_llm: bool = True  # Whether to use dual LLM setup


class SierraAgent:
    """Base AI Agent for Sierra Outfitters customer service."""

    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        self.config = config or AgentConfig()

        self.conversation = Conversation()

        if self.config.enable_dual_llm:
            self.thinking_llm = LLMClient(
                model_name=self.config.thinking_model, max_tokens=2000
            )
            self.low_latency_llm = LLMClient(
                model_name=self.config.low_latency_model, max_tokens=1000
            )
        else:
            self.thinking_llm = LLMClient(
                model_name=self.config.thinking_model, max_tokens=2000
            )
            self.low_latency_llm = self.thinking_llm

        self.tool_orchestrator = ToolOrchestrator(low_latency_llm=self.low_latency_llm)


        self.session_id: Optional[str] = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0

        logger.info("SierraAgent initialized successfully")

    def get_llm_status(self) -> Dict[str, Any]:
        """Get the status of both LLM clients."""
        return {
            "thinking_llm": {
                "model": self.thinking_llm.model_name,
                "available": True,
                "usage_stats": self.thinking_llm.get_usage_stats(),
            },
            "low_latency_llm": {
                "model": self.low_latency_llm.model_name,
                "available": True,
                "usage_stats": self.low_latency_llm.get_usage_stats(),
            },
            "dual_llm_enabled": self.config.enable_dual_llm,
        }

    def switch_llm_mode(self, enable_dual: bool) -> None:
        """Switch between single and dual LLM modes."""
        if enable_dual and not self.config.enable_dual_llm:
            print("🔄 [AGENT] Switching to dual LLM mode...")
            self.config.enable_dual_llm = True
            # Reinitialize low latency LLM if needed
            if self.low_latency_llm == self.thinking_llm:
                self.low_latency_llm = LLMClient(
                    model_name=self.config.low_latency_model, max_tokens=1000
                )
                print(
                    f"🔄 [AGENT] Low latency LLM initialized: {self.config.low_latency_model}"
                )
        elif not enable_dual and self.config.enable_dual_llm:
            print("🔄 [AGENT] Switching to single LLM mode...")
            self.config.enable_dual_llm = False
            self.low_latency_llm = self.thinking_llm
            print("🔄 [AGENT] Now using single LLM for all operations")

    def start_conversation(self) -> str:
        """Start a new conversation session."""
        print("🚀 [AGENT] Starting new conversation session...")

        # Generate session ID
        self.session_id = f"session_{int(time.time())}"
        print(f"🚀 [AGENT] Generated session ID: {self.session_id}")

        # Reset interaction counter
        self.interaction_count = 0

        # Reset conversation
        self.conversation.clear_conversation()

        # Add system message
        self.conversation.add_system_message(f"Session {self.session_id} started")

        logger.info(f"Started conversation session {self.session_id}")
        print(f"✅ [AGENT] Conversation session {self.session_id} started successfully")

        return self.session_id

    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response."""
        print(
            f"\n👤 [AGENT] Processing user input: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'"
        )
        print(
            f"👤 [AGENT] Session: {self.session_id}, Interaction: {self.interaction_count + 1}"
        )

        try:
            # Add user message to conversation
            self.conversation.add_user_message(user_input)

            # Increment interaction counter
            self.interaction_count += 1

            # Generate plan for user request
            plan = self._generate_plan(user_input)
            print(f"🧠 [AGENT] Generated plan: {plan.plan_id}")

            # Print the plan in readable format
            plan.print_plan()

            # Execute plan steps
            execution_results = self._execute_plan(plan)
            print(f"🛠️ [AGENT] Plan execution completed. Status: {plan.status}")

            # Generate response from plan results
            response = self._generate_response_from_plan(plan, execution_results)

            # NEW: Add AI response with tool results to conversation
            successful_tool_results = []
            for step_result in execution_results["steps"]:
                if step_result["success"] and isinstance(step_result["result"], ToolResult):
                    successful_tool_results.append(step_result["result"])

            self.conversation.add_ai_message_with_results(
                content=response,
                tool_results=successful_tool_results,
                intent=str(plan.intent.value) if plan.intent else None,
                plan_id=plan.plan_id
            )

            # Check if quality monitoring is needed
            if (
                self.config.enable_quality_monitoring
                and self.interaction_count % self.config.quality_check_interval == 0
            ):
                self._check_conversation_quality()

            # Check if analytics update is needed
            if (
                self.config.enable_analytics
                and self.interaction_count % self.config.analytics_update_interval == 0
            ):
                self._update_analytics()

            return response

        except Exception as e:
            print(f"❌ [AGENT] Error processing user input: {e}")
            logger.error(f"Error processing user input: {e}")

            # Generate fallback response
            fallback_response = "I'm experiencing some technical difficulties right now. Please try again in a moment."

            # Add fallback response to conversation
            self.conversation.add_ai_message(fallback_response)

            return fallback_response

    def _generate_plan(self, user_input: str) -> MultiTurnPlan:
        """Generate a comprehensive plan for handling the user request."""
        print(f"🧠 [PLAN] Generating plan for: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")

        try:
            # Analyze the request to determine what needs to be done
            plan_context = self._analyze_request(user_input)

            # Generate plan steps based on the request
            steps = self._generate_plan_steps(user_input, plan_context)

            # Create the plan
            plan_id = f"plan_{uuid.uuid4().hex[:8]}"

            # Get intent from context (now always an IntentType enum)
            intent_enum = plan_context.get("primary_intent", IntentType.GENERAL_INQUIRY)

            plan = MultiTurnPlan(
                plan_id=plan_id,
                intent=intent_enum,
                customer_request=user_input,
                steps=steps,
                status=PlanStatus.PENDING,
                created_at=datetime.now(),
                conversation_context={"session_id": self.session_id, "original_request": user_input}
            )

            print(f"🧠 [PLAN] Generated plan '{plan_id}' with {len(steps)} steps")
            return plan

        except Exception as e:
            print(f"❌ [PLAN] Error generating plan: {e}")
            # Create a fallback plan
            return self._create_fallback_plan(user_input)

    def _analyze_request(self, user_input: str) -> Dict[str, Any]:
        """Analyze the user request to understand what needs to be done."""
        print(f"🔍 [ANALYSIS] Analyzing request: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")

        user_lower = user_input.lower()
        context: Dict[str, Any] = {"request_type": "general", "complexity": "simple"}

        # Detect order-related requests
        if any(keyword in user_lower for keyword in ["order", "track", "delivery", "shipping", "#w", "order number"]):
            context["request_type"] = "order_status"
            context["primary_intent"] = IntentType.ORDER_STATUS

        # Detect product-related requests
        elif any(keyword in user_lower for keyword in ["product", "recommend", "looking for", "need", "buy", "search"]):
            context["request_type"] = "product_inquiry"
            context["primary_intent"] = IntentType.PRODUCT_INQUIRY

        # Detect promotion requests
        elif any(keyword in user_lower for keyword in ["discount", "promotion", "code", "early risers", "sale"]):
            context["request_type"] = "promotion"
            context["primary_intent"] = IntentType.EARLY_RISERS_PROMOTION

        # Detect complex multi-part requests
        if len(user_input.split()) > 20 or "and" in user_lower or "also" in user_lower:
            context["complexity"] = "complex"

        print(f"🔍 [ANALYSIS] Request type: {context['request_type']}, complexity: {context['complexity']}")
        return context

    def _generate_plan_steps(self, user_input: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Generate specific plan steps based on the request context."""
        import uuid

        steps = []
        request_type = context.get("request_type", "general")

        if request_type == "order_status":
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

        print(f"🛠️ [STEPS] Generated {len(steps)} plan steps for {request_type}")
        return steps

    def _execute_plan(self, plan: MultiTurnPlan) -> Dict[str, Any]:
        """Execute all steps in the plan."""
        print(f"🚀 [EXECUTION] Executing plan '{plan.plan_id}' with {len(plan.steps)} steps")

        plan.status = PlanStatus.IN_PROGRESS
        execution_results: Dict[str, Any] = {"steps": [], "overall_success": True}

        # NEW: Progressive context accumulation during execution
        execution_context = plan.conversation_context.copy()
        print(f"🧠 [EXECUTION] Starting with base context: {list(execution_context.keys())}")

        # NEW: Execute steps in dependency order
        execution_order = self._resolve_step_dependencies(plan.steps)
        print(f"🔗 [EXECUTION] Dependency-resolved execution order: {[step.name for step in execution_order]}")

        for step in execution_order:
            print(f"🔧 [EXECUTION] Executing step: {step.name}")

            try:
                # Gather data from dependency steps
                dependency_data = self._gather_dependency_data(step, execution_results["steps"])

                # Execute the step with accumulated context and dependency data
                result = self._execute_plan_step(step, execution_context, dependency_data)
                step.result = result
                step.is_completed = True

                # NEW: Accumulate context with step results for future steps
                if isinstance(result, ToolResult):
                    step_context_key = f"step_{step.step_id}_result"
                    execution_context[step_context_key] = result  # Store the full ToolResult
                    
                    # Add semantic keys based on result type for easier access (only for successful results)
                    if result.success and hasattr(result.data, '__class__'):
                        data_type = result.data.__class__.__name__
                        if data_type == "Order":
                            execution_context["current_order"] = result.data
                        elif data_type == "list" and len(result.data) > 0:
                            if hasattr(result.data[0], '__class__') and result.data[0].__class__.__name__ == "Product":
                                execution_context["found_products"] = result.data
                    
                    status_msg = "(success)" if result.success else "(failed)"
                    print(f"🧠 [EXECUTION] Updated context with {step_context_key} {status_msg}, total keys: {len(execution_context)}")

                execution_results["steps"].append({
                    "step_id": step.step_id,
                    "name": step.name,
                    "success": True,
                    "result": result
                })

                print(f"✅ [EXECUTION] Step '{step.name}' completed successfully")

            except Exception as e:
                print(f"❌ [EXECUTION] Step '{step.name}' failed: {e}")
                step.result = {"error": str(e)}
                execution_results["overall_success"] = False

                # Store failed step result in context for debugging
                if isinstance(step.result, dict) and "error" in step.result:
                    step_context_key = f"step_{step.step_id}_result"
                    execution_context[step_context_key] = step.result
                    print(f"🧠 [EXECUTION] Updated context with failed step {step_context_key}, total keys: {len(execution_context)}")
                else:
                    print(f"🧠 [EXECUTION] Not updating context due to step execution failure")

                execution_results["steps"].append({
                    "step_id": step.step_id,
                    "name": step.name,
                    "success": False,
                    "error": str(e)
                })

        # Update plan status and store final context
        plan.status = PlanStatus.COMPLETED if execution_results["overall_success"] else PlanStatus.FAILED
        plan.conversation_context = execution_context  # Store accumulated context back to plan

        print(f"🏁 [EXECUTION] Plan execution completed. Status: {plan.status}")
        print(f"🧠 [EXECUTION] Final context keys: {list(execution_context.keys())}")
        return execution_results

    def _execute_plan_step(self, step: PlanStep, context: Dict[str, Any], dependency_data: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute a single plan step."""
        print(f"⚙️ [STEP] Executing: {step.tool_name}")

        # Handle special analysis steps - convert to ToolResult format
        if step.tool_name == "extract_order_info":
            result_data = self._extract_order_info(step.parameters["user_input"])
            return ToolResult(success=True, data=result_data, error=None)
        if step.tool_name == "analyze_product_request":
            result_data = self._analyze_product_request(step.parameters["user_input"])
            return ToolResult(success=True, data=result_data, error=None)
        if step.tool_name == "handle_general_inquiry":
            result_data = self._handle_general_inquiry(step.parameters["user_input"])
            return ToolResult(success=True, data=result_data, error=None)

        # Execute business tool via orchestrator (now returns ToolResult)
        tool_mapping = {
            "get_order_status": True,
            "search_products": True,
            "get_product_recommendations": True,
            "get_early_risers_promotion": True,
        }

        if step.tool_name in tool_mapping:
            # Use the original user input for tool execution
            original_input = step.parameters.get("user_input") or context.get("original_request", "")
            return self.tool_orchestrator.execute_tool(step.tool_name, original_input)
        return ToolResult(
            success=False,
            error=f"Unknown tool: {step.tool_name}",
            data=None
        )

    def _resolve_step_dependencies(self, steps: List[PlanStep]) -> List[PlanStep]:
        """Resolve step dependencies and return steps in execution order."""
        print(f"🔗 [DEPENDENCIES] Resolving dependencies for {len(steps)} steps")

        # Create lookup map by step name
        step_by_name = {step.name: step for step in steps}
        completed_steps = set()
        execution_order = []
        remaining_steps = list(steps)

        # Safety counter to prevent infinite loops
        max_iterations = len(steps) * 2
        iterations = 0

        while remaining_steps and iterations < max_iterations:
            iterations += 1
            made_progress = False

            for step in remaining_steps[:]:  # Copy list to avoid modification during iteration
                # Check if all dependencies are satisfied
                dependencies_satisfied = True
                for dep_name in step.dependencies:
                    if dep_name not in completed_steps:
                        dependencies_satisfied = False
                        print(f"🔗 [DEPENDENCIES] Step '{step.name}' waiting for dependency '{dep_name}'")
                        break

                if dependencies_satisfied:
                    print(f"✅ [DEPENDENCIES] Step '{step.name}' ready for execution")
                    execution_order.append(step)
                    completed_steps.add(step.name)
                    remaining_steps.remove(step)
                    made_progress = True

            if not made_progress:
                # Handle circular dependencies or missing dependencies
                print("⚠️ [DEPENDENCIES] Circular or missing dependencies detected")
                print(f"⚠️ [DEPENDENCIES] Remaining steps: {[s.name for s in remaining_steps]}")
                print(f"⚠️ [DEPENDENCIES] Completed steps: {list(completed_steps)}")

                # Add remaining steps to execution order (fallback)
                execution_order.extend(remaining_steps)
                break

        print(f"🔗 [DEPENDENCIES] Final execution order: {[s.name for s in execution_order]}")
        return execution_order

    def _gather_dependency_data(self, step: PlanStep, completed_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gather data from completed dependency steps."""
        print(f"📊 [DEPENDENCIES] Gathering dependency data for step '{step.name}'")

        dependency_data = {}

        for dep_step_id in step.dependencies:
            # Find the completed step with this step_id
            for completed_step in completed_steps:
                if completed_step["step_id"] == dep_step_id and completed_step["success"]:
                    step_result = completed_step["result"]
                    if isinstance(step_result, ToolResult) and step_result.success:
                        dependency_data[dep_step_id] = step_result.data
                        print(f"📊 [DEPENDENCIES] Found data for dependency step '{dep_step_id}'")
                    break

        print(f"📊 [DEPENDENCIES] Gathered {len(dependency_data)} dependency data items")
        return dependency_data

    def _generate_response_from_plan(self, plan: MultiTurnPlan, execution_results: Dict[str, Any]) -> str:
        """Generate a response based on plan execution results."""
        print(f"💭 [RESPONSE] Generating response for plan '{plan.plan_id}'")

        # Debug: Print execution results
        print(f"💭 [RESPONSE] Execution results: {execution_results}")

        # Collect all successful ToolResult objects
        successful_tool_results = []
        for step_result in execution_results["steps"]:
            if step_result["success"] and isinstance(step_result["result"], ToolResult):
                successful_tool_results.append(step_result["result"])

        print(f"💭 [RESPONSE] Found {len(successful_tool_results)} successful ToolResults")

        if not successful_tool_results:
            return "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team."

        # Find the most relevant business data (prioritize business objects over extraction results)
        primary_tool_result = None
        for tool_result in successful_tool_results:
            if tool_result.success and tool_result.data:
                # Prioritize typed business objects (Order, Product, Promotion) over dicts
                from ..data.data_types import Order, Product, Promotion
                if isinstance(tool_result.data, (Order, Product, Promotion)):
                    primary_tool_result = tool_result
                    break

        # If no primary business object found, use the last successful result
        if not primary_tool_result and successful_tool_results:
            primary_tool_result = successful_tool_results[-1]

        # Convert IntentType enum to string format expected by LLM client
        intent_mapping = {
            IntentType.ORDER_STATUS: "order_status",
            IntentType.PRODUCT_INQUIRY: "product_inquiry",
            IntentType.EARLY_RISERS_PROMOTION: "promotion_inquiry",
            IntentType.RETURN_REQUEST: "return_request",
            IntentType.COMPLAINT: "complaint",
            IntentType.SHIPPING_INFO: "shipping_info",
            IntentType.PROMOTION_INQUIRY: "promotion_inquiry",
            IntentType.GENERAL_INQUIRY: "customer_service",
            IntentType.CUSTOMER_SERVICE: "customer_service"
        }

        plan_intent = getattr(plan, "intent", IntentType.CUSTOMER_SERVICE)
        intent_string = intent_mapping.get(plan_intent, "customer_service")

        # NEW: Build conversational context using the Conversation class
        conversational_context = self.conversation.build_conversational_context(
            current_tool_results=successful_tool_results,
            intent=intent_string
        )

        # Build context for LLM client with conversational context
        context = {
            "user_input": plan.customer_request,
            "customer_request": plan.customer_request,
            "primary_tool_result": primary_tool_result,  # Main ToolResult for response
            "conversational_context": conversational_context,  # Rich conversation context
            "intent": intent_string,
            "sentiment": "neutral"  # Default sentiment
        }

        print(f"💭 [RESPONSE] Built context with conversational context: {len(conversational_context)} characters")

        # Use LLM to generate natural response
        response = self.tool_orchestrator.llm_client.generate_response(context)
        return response

    def _create_fallback_plan(self, user_input: str) -> MultiTurnPlan:
        """Create a simple fallback plan when plan generation fails."""
        import uuid
        from datetime import datetime

        fallback_step = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:8]}",
            name="General Assistance",
            description="Provide general customer service help",
            tool_name="handle_general_inquiry",
            parameters={"user_input": user_input}
        )

        return MultiTurnPlan(
            plan_id=f"fallback_{uuid.uuid4().hex[:8]}",
            intent=IntentType.GENERAL_INQUIRY,
            customer_request=user_input,
            steps=[fallback_step],
            status=PlanStatus.PENDING,
            created_at=datetime.now()
        )

    def _extract_order_info(self, user_input: str) -> Dict[str, Any]:
        """Extract order information from user input."""
        # Use existing extraction logic from business tools
        email = self.tool_orchestrator.business_tools._extract_email(user_input)
        order_number = self.tool_orchestrator.business_tools._extract_order_number(user_input)

        return {
            "email": email,
            "order_number": order_number,
            "extraction_successful": bool(email and order_number)
        }

    def _analyze_product_request(self, user_input: str) -> Dict[str, Any]:
        """Analyze what products the customer is looking for."""
        preferences = self.tool_orchestrator.business_tools._extract_preferences(user_input)
        category = self.tool_orchestrator.business_tools._extract_product_category(user_input)
        
        # Handle generic product requests
        user_lower = user_input.lower()
        if (category is None and len(preferences) == 0 and 
            any(word in user_lower for word in ["products", "gear", "items", "equipment", "show me"])):
            # For generic requests, use "outdoor" as default category to get some results
            category = "outdoor gear"
            preferences = ["outdoor", "adventure"]
            print(f"🔍 [ANALYSIS] Generic product request detected, using fallback category: {category}")

        return {
            "preferences": preferences,
            "category": category,
            "search_query": user_input
        }

    def _handle_general_inquiry(self, user_input: str) -> Dict[str, Any]:
        """Handle general customer service inquiries."""
        return {
            "inquiry_type": "general",
            "user_input": user_input,
            "response": "I'm here to help you with any questions about Sierra Outfitters products, orders, or services."
        }

    def _analyze_sentiment(self, user_input: str) -> str:
        """Analyze the user's sentiment."""

        try:
            sentiment = self._analyze_sentiment_mock(user_input)

            return sentiment

        except Exception as e:
            print(f"❌ [SENTIMENT] Error analyzing sentiment: {e}")
            print("🔄 [SENTIMENT] Falling back to NEUTRAL sentiment")
            return "NEUTRAL"

    def _analyze_sentiment_mock(self, user_input: str) -> str:
        """Mock sentiment analysis for testing."""
        user_input_lower = user_input.lower()

        # Simple keyword-based sentiment analysis
        positive_words = [
            "thank", "thanks", "great", "awesome", "love", "perfect", "excellent", "happy", "satisfied"
        ]
        negative_words = [
            "angry", "frustrated", "disappointed", "upset", "terrible", "awful", "hate", "problem", "issue", "broken"
        ]

        positive_count = sum(1 for word in positive_words if word in user_input_lower)
        negative_count = sum(1 for word in negative_words if word in user_input_lower)

        if positive_count > negative_count:
            sentiment = "POSITIVE"
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"

        return sentiment


    def _check_conversation_quality(self) -> None:
        """Check and update conversation quality."""
        print(
            f"📊 [QUALITY] Starting quality check for interaction {self.interaction_count}"
        )

        try:
            # Simplified quality check - just use a mock score
            quality_score = 0.8
            print(f"📊 [QUALITY] Mock quality score: {quality_score}")

            # Update conversation with quality score
            self.conversation.update_quality_score(quality_score)
            print(f"📊 [QUALITY] Updated conversation with quality score: {quality_score}")

            self.last_quality_check = self.interaction_count
            print("📊 [QUALITY] Quality check completed successfully")

        except Exception as e:
            print(f"❌ [QUALITY] Error during quality check: {e}")
            logger.error(f"Error during quality check: {e}")

    def _update_analytics(self) -> None:
        """Update conversation analytics."""
        print(
            f"📈 [ANALYTICS] Starting analytics update for interaction {self.interaction_count}"
        )

        try:
            # Simplified analytics - just log
            if self.session_id:
                print(f"📈 [ANALYTICS] Mock analytics update for session: {self.session_id}")
                self.last_analytics_update = self.interaction_count
                print("📈 [ANALYTICS] Analytics update completed successfully")
            else:
                print("⚠️ [ANALYTICS] No valid session ID, skipping analytics update")

        except Exception as e:
            print(f"❌ [ANALYTICS] Error updating analytics: {e}")
            logger.error(f"Error updating analytics: {e}")

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        print(
            f"📋 [SUMMARY] Generating conversation summary for session: {self.session_id}"
        )

        try:
            summary = {
                "session_id": self.session_id,
                "interaction_count": self.interaction_count,
                "conversation_length": self.conversation.get_conversation_length(),
                "conversation_duration": self.conversation.get_conversation_duration(),
                "quality_score": self.conversation.quality_score,
                "conversation_phase": self.conversation.conversation_state.conversation_phase,
                "urgency_level": self.conversation.conversation_state.urgency_level,
                "last_quality_check": self.last_quality_check,
                "last_analytics_update": self.last_analytics_update,
            }

            print(f"📋 [SUMMARY] Generated summary with {len(summary)} elements")
            return summary

        except Exception as e:
            print(f"❌ [SUMMARY] Error generating summary: {e}")
            logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the agent."""
        print("📊 [STATS] Generating comprehensive agent statistics...")

        try:
            stats = {
                "llm_status": self.get_llm_status(),
                "planning_stats": {"plans_generated": 0, "success_rate": 0.0},
                "execution_stats": {"plans_executed": 0, "success_rate": 0.0},
                "tool_stats": self.tool_orchestrator.get_tool_execution_stats(),
                "conversation_summary": self.get_conversation_summary(),
                "configuration": {
                    "quality_check_interval": self.config.quality_check_interval,
                    "analytics_update_interval": self.config.analytics_update_interval,
                    "max_conversation_length": self.config.max_conversation_length,
                    "enable_quality_monitoring": self.config.enable_quality_monitoring,
                    "enable_analytics": self.config.enable_analytics,
                    "thinking_model": self.config.thinking_model,
                    "low_latency_model": self.config.low_latency_model,
                    "enable_dual_llm": self.config.enable_dual_llm,
                },
            }

            print(
                f"📊 [STATS] Generated comprehensive statistics with {len(stats)} categories"
            )
            return stats

        except Exception as e:
            print(f"❌ [STATS] Error generating statistics: {e}")
            logger.error(f"Error generating statistics: {e}")
            return {"error": str(e)}

    def reset_conversation(self) -> None:
        """Reset the conversation and start fresh."""
        print(f"🔄 [RESET] Resetting conversation for session: {self.session_id}")

        self.conversation.clear_conversation()
        self.session_id = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0

        print("🔄 [RESET] Conversation reset completed successfully")
        logger.info("Conversation reset")

    def end_conversation(self) -> None:
        """End the current conversation and finalize analytics."""
        print(f"🏁 [END] Ending conversation for session: {self.session_id}")

        try:
            # Final quality check
            if self.config.enable_quality_monitoring:
                print("🏁 [END] Performing final quality check...")
                self._check_conversation_quality()

            # Final analytics update
            if self.config.enable_analytics:
                print("🏁 [END] Performing final analytics update...")
                self._update_analytics()

            # Generate final summary
            print("🏁 [END] Generating final conversation summary...")
            final_summary = self.get_conversation_summary()
            print(f"🏁 [END] Final summary: {final_summary}")

            print("✅ [END] Conversation ended successfully")

        except Exception as e:
            print(f"❌ [END] Error ending conversation: {e}")
            logger.error(f"Error ending conversation: {e}")
