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

from ..ai.llm_service import LLMService
from ..core.conversation import Conversation
from ..core.planning_service import PlanningService
from ..data.data_types import (
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

        # Initialize unified LLM service
        self.llm_service = LLMService(
            thinking_model=self.config.thinking_model,
            low_latency_model=self.config.low_latency_model
        )

        self.tool_orchestrator = ToolOrchestrator()

        # Initialize planning service with unified LLM service
        self.planning_service = PlanningService(
            llm_service=self.llm_service,  # Use unified service
            tool_orchestrator=self.tool_orchestrator
        )

        self.session_id: Optional[str] = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0
        
        # Clean agent - no continuation cruft

        logger.info("SierraAgent initialized successfully")

    def get_llm_status(self) -> Dict[str, Any]:
        """Get the status of unified LLM service."""
        return self.llm_service.get_service_status()

    # LLM mode switching handled by unified service - no longer needed

    def start_conversation(self) -> str:
        """Start a new conversation session."""

        # Generate session ID
        self.session_id = f"session_{int(time.time())}"

        # Reset interaction counter
        self.interaction_count = 0

        # Reset conversation
        self.conversation.clear_conversation()

        # Add system message
        self.conversation.add_system_message(f"Session {self.session_id} started")

        logger.info(f"Started conversation session {self.session_id}")

        return self.session_id

    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response."""
        
        try:
            # Add user message to conversation
            self.conversation.add_user_message(user_input)

            # Increment interaction counter
            self.interaction_count += 1

            # Simplified approach - no continuation handling

            # Generate plan for user request
            plan = self._generate_plan(user_input)

            # Print the plan in readable format
            plan.print_plan()

            # Execute plan steps
            execution_results = self._execute_plan(plan)

            # Simplified - no complex continuation or context extraction logic

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
                intent=None,  # No longer using intent
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
            logger.error(f"Error processing user input: {e}")

            # Generate fallback response
            fallback_response = "I'm experiencing some technical difficulties right now. Please try again in a moment."

            # Add fallback response to conversation
            self.conversation.add_ai_message(fallback_response)

            return fallback_response

    def _generate_plan(self, user_input: str) -> MultiTurnPlan:
        """Generate a comprehensive plan for handling the user request."""

        try:
            # Get conversation data for planning context
            conversation_data = {
                "available_data": self.conversation.get_available_data(),
                "conversation_phase": self.conversation.conversation_state.conversation_phase,
                "current_topic": self.conversation.conversation_state.current_topic,
                "session_id": self.session_id
            }

            # Use PlanningService to generate the complete plan with available data
            available_data = conversation_data["available_data"]
            # Type assertion to ensure mypy compatibility
            assert isinstance(available_data, dict), "available_data should be a dict"
            plan = self.planning_service.generate_plan(user_input, session_id=self.session_id, available_data=available_data)

            return plan

        except Exception as e:
            # Use PlanningService fallback plan generation
            fallback_step = PlanStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                name="General Assistance",
                description="Provide general customer service help",
                tool_name="handle_general_inquiry",
                parameters={"user_input": user_input}
            )
            
            return MultiTurnPlan(
                plan_id=f"fallback_{uuid.uuid4().hex[:8]}",
                customer_request=user_input,
                steps=[fallback_step],
                conversation_context={
                    "planning": {"fallback": True, "reason": "plan_generation_failed"},
                    "execution": {"session_id": self.session_id, "original_request": user_input}
                },
                status=PlanStatus.PENDING,
                created_at=datetime.now()
            )

    def _execute_plan(self, plan: MultiTurnPlan) -> Dict[str, Any]:
        """Execute all steps in the plan."""

        plan.status = PlanStatus.IN_PROGRESS
        execution_results: Dict[str, Any] = {"steps": [], "overall_success": True}

        # NEW: Progressive context accumulation during execution
        execution_context = plan.conversation_context.copy()

        # NEW: Execute steps in dependency order
        execution_order = self._resolve_step_dependencies(plan.steps)

        for step in execution_order:

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

                execution_results["steps"].append({
                    "step_id": step.step_id,
                    "name": step.name,
                    "tool_name": step.tool_name,
                    "success": True,
                    "result": result
                })

                # Update plan using unified LLM service after each step
                completed_results = [step_result["result"] for step_result in execution_results["steps"] 
                                   if isinstance(step_result.get("result"), ToolResult)]
                if len(completed_results) > 0 and len(completed_results) % 2 == 0:  # Update every 2 steps to avoid too frequent calls
                    updated_steps = self.planning_service.update_plan_with_llm_service(
                        plan, completed_results
                    )
                    if updated_steps:
                        plan.steps = updated_steps
                        print(f"🔄 [EXECUTION] Plan updated with {len(updated_steps)} new suggested steps: {updated_steps}")

            except Exception as e:
                print(f"❌ [EXECUTION] Step '{step.name}' failed: {e}")
                step.result = {"error": str(e)}
                execution_results["overall_success"] = False

                # Store failed step result in context for debugging
                if isinstance(step.result, dict) and "error" in step.result:
                    step_context_key = f"step_{step.step_id}_result"
                    execution_context[step_context_key] = step.result
                else:
                    step_context_key = f"step_{step.step_id}_result"
                    execution_context[step_context_key] = step.result

                execution_results["steps"].append({
                    "step_id": step.step_id,
                    "name": step.name,
                    "tool_name": step.tool_name,
                    "success": False,
                    "error": str(e)
                })

        # Update plan status and store final context
        plan.status = PlanStatus.COMPLETED if execution_results["overall_success"] else PlanStatus.FAILED
        plan.conversation_context = execution_context  # Store accumulated context back to plan

        return execution_results

    def _execute_plan_step(self, step: PlanStep, context: Dict[str, Any], dependency_data: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute a single plan step."""

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
        if step.tool_name == "get_product_details":
            result_data = self._get_product_details_from_context()
            return ToolResult(success=True, data=result_data, error=None)
        if step.tool_name == "format_order_status":
            result_data = self._format_existing_order_status()
            return ToolResult(success=True, data=result_data, error=None)

        # Execute business tool via orchestrator (now returns ToolResult)
        tool_mapping = {
            "get_order_status": True,
            "search_products": True,
            "get_product_recommendations": True,
            "get_early_risers_promotion": True,
        }

        if step.tool_name in tool_mapping:
            # Extract typed parameters for the tool
            tool_params = self._extract_tool_parameters(step.tool_name, context)
            
            if tool_params is None:
                return ToolResult(success=False, error="Missing required parameters", data=None)
            return self.tool_orchestrator.execute_tool(step.tool_name, **tool_params)
        return ToolResult(
            success=False,
            error=f"Unknown tool: {step.tool_name}",
            data=None
        )

    def _extract_tool_parameters(self, tool_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract typed parameters for a specific tool from context."""
        
        # Get original user request
        original_request = (
            context.get("execution", {}).get("original_request", "") or
            context.get("original_request", "")
        )
        
        if tool_name == "get_order_status":
            # Extract email and order number from original request
            email = self._extract_email(original_request)
            order_number = self._extract_order_number(original_request)
            if email and order_number:
                return {"email": email, "order_number": order_number}
            return None
            
        elif tool_name == "search_products":
            # Use original request as search query
            if original_request:
                return {"query": original_request}
            return None
            
        elif tool_name == "get_product_details":
            # First try to get SKUs from conversation context
            available_data = self.conversation.get_available_data()
            if "current_order" in available_data:
                current_order = available_data["current_order"]
                if hasattr(current_order, 'products_ordered') and current_order.products_ordered:
                    return {"skus": current_order.products_ordered}
            
            # Fallback: try to extract SKU from original request
            product_sku = self._extract_product_id(original_request)
            if product_sku:
                return {"skus": [product_sku]}
            return None
            
        elif tool_name == "get_product_recommendations":
            # Extract category and preferences from original request
            category = self._extract_product_category(original_request)
            preferences = self._extract_preferences(original_request)
            return {"category": category, "preferences": preferences if preferences else None}
            
        elif tool_name in ["get_company_info", "get_contact_info", "get_policies", "get_early_risers_promotion"]:
            # These tools don't need parameters
            return {}
            
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        import re
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def _extract_order_number(self, text: str) -> Optional[str]:
        """Extract order number from text."""
        import re
        patterns = [
            r"#\s*W\s*\d+",           # #W001, # W001, #W 001
            r"\bW\s*-?\s*\d+\b",      # W001, W-001, W 001 (with word boundaries)
            r"order\s+#?\s*W\s*-?\s*\d+",  # Order W001, order #W001, order W-001
            r"order\s+number\s+#?\s*W\s*-?\s*\d+",  # order number W001
            r"my\s+order\s+#?\s*W\s*-?\s*\d+",      # my order W001
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_text = match.group(0)
                w_match = re.search(r"W\s*-?\s*(\d+)", order_text, re.IGNORECASE)
                if w_match:
                    number_part = w_match.group(1)
                    return f"#W{number_part.zfill(3)}"
        return None

    def _extract_product_id(self, text: str) -> Optional[str]:
        """Extract product ID from text."""
        import re
        patterns = [r"PROD\d+", r"Product\s+(\d+)"]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        return None

    def _extract_product_category(self, text: str) -> Optional[str]:
        """Extract product category from text."""
        text_lower = text.lower()
        categories = [
            "backpack", "hiking", "adventure", "outdoor gear",
            "skis", "snow", "winter", "high-tech", "trail", "comfort",
            "food & beverage", "weatherproof", "versatile", "explorer",
            "rugged design", "trailblazing", "personal flight", "safety-enhanced",
            "stealth", "discretion", "advanced cloaking", "fashion", "lifestyle",
            "teleportation", "transport", "home decor", "lighting", "modern design",
            "luxury", "interior style"
        ]
        
        for category in categories:
            if category in text_lower:
                return category
        return None

    def _extract_preferences(self, text: str) -> List[str]:
        """Extract customer preferences from text."""
        text_lower = text.lower()
        preferences = []
        preference_keywords = [
            "hiking", "camping", "adventure", "outdoor", "winter", "summer",
            "comfort", "luxury", "budget", "premium", "lightweight", "durable",
            "waterproof", "high-tech", "traditional", "modern", "classic"
        ]
        
        for keyword in preference_keywords:
            if keyword in text_lower:
                preferences.append(keyword)
        return preferences

    def _resolve_step_dependencies(self, steps: List[PlanStep]) -> List[PlanStep]:
        """Resolve step dependencies and return steps in execution order."""

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
                        break

                if dependencies_satisfied:
                    execution_order.append(step)
                    completed_steps.add(step.name)
                    remaining_steps.remove(step)
                    made_progress = True

            if not made_progress:
                # Handle circular dependencies or missing dependencies

                # Add remaining steps to execution order (fallback)
                execution_order.extend(remaining_steps)
                break

        return execution_order

    def _gather_dependency_data(self, step: PlanStep, completed_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gather data from completed dependency steps."""

        dependency_data = {}

        for dep_step_id in step.dependencies:
            # Find the completed step with this step_id
            for completed_step in completed_steps:
                if completed_step["step_id"] == dep_step_id and completed_step["success"]:
                    step_result = completed_step["result"]
                    if isinstance(step_result, ToolResult) and step_result.success:
                        dependency_data[dep_step_id] = step_result.data
                    break

        return dependency_data

    def _generate_response_from_plan(self, plan: MultiTurnPlan, execution_results: Dict[str, Any]) -> str:
        """Generate a response based on plan execution results using unified LLM service."""

        # Collect all ToolResult objects (both successful and failed)
        all_tool_results = []
        for step_result in execution_results["steps"]:
            if step_result["success"] and isinstance(step_result["result"], ToolResult):
                all_tool_results.append(step_result["result"])

        if not all_tool_results:
            return "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team."

        # Get request context
        request_type = plan.conversation_context.get("request_type", "general")
        conversation_phase = self.conversation.conversation_state.conversation_phase
        
        # Limited context auditing for response generation
        tool_data_types = []
        for result in all_tool_results:
            if result.success and result.data:
                data_type = type(result.data).__name__
                tool_data_types.append(data_type)
            elif not result.success:
                tool_data_types.append("ERROR")
        
        print(f"💭 [RESPONSE] Generating response | Request: {request_type} | Data types: {tool_data_types}")
        
        # Use unified LLM service for response generation
        response = self.llm_service.generate_customer_service_response(
            user_input=plan.customer_request,
            tool_results=all_tool_results,
            conversation_context=self.conversation,
            use_thinking_model=False  # Use fast model for responses
        )
        
        return response

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
        
        try:
            # Simplified quality check - just use a mock score
            quality_score = 0.8

            # Update conversation with quality score
            self.conversation.update_quality_score(quality_score)

            self.last_quality_check = self.interaction_count

        except Exception as e:
            logger.error(f"Error during quality check: {e}")

    def _update_analytics(self) -> None:
        """Update conversation analytics."""
        
        try:
            # Simplified analytics - just log
            if self.session_id:
                self.last_analytics_update = self.interaction_count
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        
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

            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the agent."""

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

            return stats

        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {"error": str(e)}

    def reset_conversation(self) -> None:
        """Reset the conversation and start fresh."""

        self.conversation.clear_conversation()
        self.session_id = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0

        logger.info("Conversation reset")

    def end_conversation(self) -> None:
        """End the current conversation and finalize analytics."""

        try:
            # Final quality check
            if self.config.enable_quality_monitoring:
                self._check_conversation_quality()

            # Final analytics update
            if self.config.enable_analytics:
                self._update_analytics()

            # Generate final summary
            final_summary = self.get_conversation_summary()

        except Exception as e:
            logger.error(f"Error ending conversation: {e}")

    def _add_context_to_conversation(self, context_data: Dict[str, Any]) -> None:
        """Add context data from tool results to conversation context."""
        
        try:
            # Store context in conversation state for future tool access
            if not hasattr(self.conversation, 'context_storage'):
                self.conversation.context_storage = {}
            
            # Merge new context with existing context
            self.conversation.context_storage.update(context_data)
            
        except Exception as e:
            logger.error(f"Error adding context to conversation: {e}")

    def _build_continuation_completion_prompt(self, user_input: str, tool_name: str, result: "ToolResult") -> str:
        """Build prompt for continuation completion responses."""
        result_summary = result.serialize_for_context() if result.success else f"Error: {result.error}"
        conversational_context = self.conversation.build_conversational_context([result], "tool_completion")
        
        prompt = f"""You are a helpful customer service representative for Sierra Outfitters.

The customer provided additional information to complete a {tool_name} request. Here are the results:

{result_summary}

{conversational_context}

Please present this information to the customer in a clear, friendly, and natural way. Be specific and include all relevant details from the order information."""
        
        return prompt

    def _get_product_details_from_context(self) -> Dict[str, Any]:
        """Get product details from existing order context."""
        
        available_data = self.conversation.get_available_data()
        if "current_order" in available_data:
            order = available_data["current_order"]
            
            # Use the business tools to get product details for all products in the order
            # Call with a user input that indicates we want details for the order's products
            result = self.tool_orchestrator.execute_tool(
                "get_product_details", 
                skus=order.products_ordered
            )
            
            if result.success and result.data:
                return result.data
            else:
                # Fallback: return basic order information
                return {
                    "order_number": order.order_number,
                    "customer_name": order.customer_name,
                    "products_ordered": order.products_ordered,
                    "status": order.status,
                    "tracking_number": order.tracking_number,
                    "message": "Here are the product IDs in your order. For detailed product information, please visit our website or contact customer service."
                }
        else:
            return {"error": "No order context available"}

    def _format_existing_order_status(self) -> Dict[str, Any]:
        """Format existing order status for display."""
        
        available_data = self.conversation.get_available_data()
        if "current_order" in available_data:
            order = available_data["current_order"]
            
            return {
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "email": order.email,
                "products_ordered": order.products_ordered,
                "status": order.status,
                "tracking_number": order.tracking_number,
                "formatted": True
            }
        else:
            return {"error": "No order context available"}
