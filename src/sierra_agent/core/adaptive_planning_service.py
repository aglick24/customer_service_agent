"""Adaptive Planning Service

Clean, strongly typed planning service that manages evolving conversation plans.
"""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from sierra_agent.ai.llm_service import LLMService
from sierra_agent.ai.prompt_templates import PromptTemplates
from sierra_agent.core.planning_types import EvolvingPlan, ExecutedStep, ConversationContext
from sierra_agent.data.data_types import Order, Product, ToolResult
from sierra_agent.tools.tool_orchestrator import ToolOrchestrator

logger = logging.getLogger(__name__)


class AdaptivePlanningService:
    """Manages evolving plans that adapt across conversation turns."""
    
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        """Initialize the adaptive planning service."""
        self.active_plans: Dict[str, EvolvingPlan] = {}
        self.llm_service = llm_service
        logger.info("AdaptivePlanningService initialized")
    
    def get_or_create_plan(self, session_id: str, user_input: str) -> EvolvingPlan:
        """Get existing plan for session or create new one."""
        existing_plan = self.active_plans.get(session_id)
        
        if existing_plan and not existing_plan.is_complete:
            # Check if the new user input is related to the existing plan
            if self._is_input_related_to_existing_plan(user_input, existing_plan):
                return existing_plan
            else:
                # New topic - mark existing plan complete and create new one
                existing_plan.is_complete = True
        
        # Create new plan
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        new_plan = EvolvingPlan(
            plan_id=plan_id,
            original_request=user_input
        )
        
        self.active_plans[session_id] = new_plan
        return new_plan
    
    def _is_input_related_to_existing_plan(self, user_input: str, existing_plan: EvolvingPlan) -> bool:
        """Check if new input is related to existing plan or represents a topic change using LLM."""
        if not self.llm_service:
            # Fallback: always create new plan if no LLM
            return False
        
        try:
            # Get context about the existing plan
            plan_context = f"Original request: '{existing_plan.original_request}'"
            if existing_plan.executed_steps:
                plan_context += f", Tools used: {[step.tool_name for step in existing_plan.executed_steps]}"
            
            prompt = PromptTemplates.build_plan_continuation_prompt(
                plan_context=existing_plan.context,
                user_input=user_input,
                existing_request=existing_plan.original_request
            )

            response = self.llm_service.low_latency_client.call_llm(prompt)
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response.strip())
                decision = parsed_response.get("decision", "")
                return decision == "CONTINUE"
            except json.JSONDecodeError:
                # Fallback for backwards compatibility
                response_clean = response.strip().upper()
                return response_clean == "CONTINUE"
            
        except Exception as e:
            logger.exception(f"Error checking input relatedness: {e}")
            # Fallback: create new plan to be safe
            return False
    
    def process_user_input(self, session_id: str, user_input: str, tool_orchestrator: ToolOrchestrator) -> Tuple[EvolvingPlan, Optional[str]]:
        """Process user input and return updated plan with response."""
        plan = self.get_or_create_plan(session_id, user_input)
        
        # ALWAYS update context from user input first
        plan._update_context_from_user_input(user_input)
        
        # Determine what action(s) to take using LLM-powered planning
        actions = self._determine_next_action_with_llm(plan, user_input, tool_orchestrator)
        
        if not actions:
            # No clear action determined - try LLM analysis with full context and tool registry
            fallback_actions = self._retry_planning_with_full_context(plan, user_input, tool_orchestrator)
            if fallback_actions:
                if len(fallback_actions) == 1:
                    return self._execute_single_action(plan, fallback_actions[0], user_input, tool_orchestrator)
                else:
                    return self._execute_multistep_actions(plan, fallback_actions, user_input, tool_orchestrator)
            else:
                return plan, "I'm not sure how to help with that. Could you please be more specific about what you need?"
        
        # Handle single action case (including special responses)
        if len(actions) == 1:
            action = actions[0]
            if action == "wait_for_missing_info":
                # LLM determined we need to wait for more information
                missing_info = self._get_missing_info_message("get_order_status", plan)  # Assume order context
                return plan, missing_info
            
            if action == "conversational_response":
                # LLM determined this is a conversational request - generate friendly response
                return plan, self._generate_conversational_response(user_input, plan)
            
            return self._execute_single_action(plan, action, user_input, tool_orchestrator)
        
        # Handle multistep execution
        return self._execute_multistep_actions(plan, actions, user_input, tool_orchestrator)
    
    def _get_missing_info_message(self, action: str, plan: EvolvingPlan) -> str:
        """Generate LLM-powered message for missing information."""
        if not self.llm_service:
            return "I need more information to help with that request."
        
        try:
            # Build context about what we have vs what we need
            context_info = []
            missing_items = []
            
            if action == "get_order_status":
                if plan.context.customer_email:
                    context_info.append(f"Customer email: {plan.context.customer_email}")
                else:
                    missing_items.append("email address")
                
                if plan.context.order_number:
                    context_info.append(f"Order number: {plan.context.order_number}")
                else:
                    missing_items.append("order number")
            
            elif action == "get_product_details":
                if plan.context.current_order:
                    context_info.append("Customer has an order")
                else:
                    missing_items.append("product SKUs or order information")
            
            elif action == "search_products":
                missing_items.append("search criteria")
            
            context_summary = " | ".join(context_info) if context_info else "No context available"
            missing_summary = ", ".join(missing_items) if missing_items else "additional information"
            
            # Construct a temporary user input for the prompt template
            temp_input = f"Action needed: {action}, Missing: {missing_summary}"
            prompt = PromptTemplates.build_missing_info_prompt(
                plan_context=plan.context,
                user_input=temp_input
            )
            
            response = self.llm_service.low_latency_client.call_llm(prompt)
            return response.strip().strip('"').strip("'")
            
        except Exception as e:
            logger.exception(f"Error generating missing info message with LLM: {e}")
            return "I need more information to help with that request."
    
    def _format_success_response(self, executed_step: ExecutedStep, user_input: str) -> str:
        """Generate a natural language response using LLM based on the executed step."""
        # Create a ToolResult from the executed step
        tool_result = ToolResult(
            data=executed_step.result_data,
            success=executed_step.was_successful,
            error=executed_step.result.error if not executed_step.was_successful else None
        )
        
        # Always use LLM to generate natural response
        if self.llm_service:
            try:
                response = self.llm_service.generate_customer_service_response(
                    user_input=user_input,
                    tool_results=[tool_result],
                    plan_context=None,  # Pass None or create minimal context
                    use_thinking_model=False  # Use fast model for response generation
                )
                return response
            except Exception as e:
                logger.exception(f"Error generating LLM response: {e}")
                # Generate a fallback response using LLM with simpler context
                return self._generate_fallback_llm_response(executed_step, user_input)
        
        # Only if LLM service is not available
        return "I found some information for you, but I'm having trouble formatting it right now."
    
    def _generate_conversational_response(self, user_input: str, plan: EvolvingPlan) -> str:
        """Generate conversational response with Sierra Outfitters branding for greetings, thanks, etc."""
        if not self.llm_service:
            return "Hello! I'm here to help you with your outdoor adventures. What can I assist you with today?"
        
        try:
            # Determine response type based on input
            user_lower = user_input.lower()
            
            response_type = "general"
            if any(greeting in user_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
                response_type = "greeting"
            elif any(thanks in user_lower for thanks in ["thanks", "thank you", "appreciate"]):
                response_type = "thanks"
            elif any(help_word in user_lower for help_word in ["help", "assist", "support"]):
                response_type = "help_request"
            
            prompt = PromptTemplates.build_no_data_response_prompt(
                plan_context=plan.context,
                user_input=user_input,
                response_type=response_type
            )
            
            response = self.llm_service.low_latency_client.call_llm(prompt)
            return response.strip().strip('"').strip("'")
            
        except Exception as e:
            logger.exception(f"Error generating conversational response: {e}")
            return "Hello! 🏔️ Welcome to Sierra Outfitters! I'm excited to help you with your outdoor adventures. What can I assist you with today?"

    def _generate_fallback_llm_response(self, executed_step: ExecutedStep, user_input: str) -> str:
        """Generate fallback response using LLM with simplified context."""
        if not self.llm_service:
            return "I was able to process your request, but I'm having trouble explaining the results right now."
            
        try:
            # Create simplified data summary for LLM
            tool_name = executed_step.tool_name
            result_data = executed_step.result_data
            
            # Create basic data description
            data_summary = "No data returned"
            if result_data:
                if isinstance(result_data, list) and result_data:
                    data_summary = f"Found {len(result_data)} items"
                elif hasattr(result_data, '__dict__'):
                    data_summary = f"Retrieved {type(result_data).__name__} data"
                else:
                    data_summary = "Retrieved data"
            
            # Create minimal context for template
            minimal_context = ConversationContext()
            
            prompt = PromptTemplates.build_tool_result_response_prompt(
                plan_context=minimal_context,
                user_input=user_input,
                result_data=data_summary
            )
            
            response = self.llm_service.low_latency_client.call_llm(prompt)
            return response.strip().strip('"').strip("'")
            
        except Exception as e:
            logger.exception(f"Error in fallback LLM response: {e}")
            return "I was able to process your request, but I'm having trouble explaining the results right now."
    
    def cleanup_completed_plans(self) -> None:
        """Clean up completed plans to prevent memory leaks."""
        completed_sessions = [
            session_id for session_id, plan in self.active_plans.items()
            if plan.is_complete
        ]
        
        for session_id in completed_sessions:
            del self.active_plans[session_id]
        
        if completed_sessions:
            logger.info(f"Cleaned up {len(completed_sessions)} completed plans")
    
    def _determine_next_action_with_llm(self, plan: EvolvingPlan, user_input: str, tool_orchestrator: ToolOrchestrator) -> List[str]:
        """Use LLM to determine the next action based on context and user input."""
        if not self.llm_service:
            # Fallback to simple hardcoded logic if no LLM available  
            action = plan.determine_next_action(user_input)
            return [action] if action else []
        
        try:
            # Get available tools dynamically from tool orchestrator
            available_tools = tool_orchestrator.get_available_tools()
            
            # Use specialized LLM analysis for vague requests and contextual suggestions
            suggested_actions = self.llm_service.analyze_vague_request_and_suggest(
                user_input=user_input,
                plan_context=plan.context,
                available_tools=available_tools,
                tool_orchestrator=tool_orchestrator
            )
            
            # Return all suggested actions for multistep execution
            return suggested_actions
            
        except Exception as e:
            logger.exception(f"Error in LLM planning: {e}")
            # Fallback to simple logic
            action = plan.determine_next_action(user_input)
            return [action] if action else []
    
    def _enhance_parameters_with_llm(self, plan: EvolvingPlan, action: str, user_input: str) -> Optional[Dict[str, Any]]:
        """Use LLM to enhance parameters for specific actions using available context."""
        try:
            if action == "get_recommendations" and self.llm_service:
                # Smart parameter selection for recommendations tool
                params = {"limit": 3}
                
                # If we have order information, use complementary strategy
                if plan.context.current_order:
                    order = plan.context.current_order
                    if hasattr(order, 'products_ordered') and order.products_ordered:
                        return {
                            "recommendation_type": "complement_to",
                            "reference_skus": order.products_ordered,
                            "limit": 3
                        }
                
                # Default to general recommendations
                return {"recommendation_type": "general", "limit": 3}
            
            elif action == "get_product_info":
                # If user is asking about products they ordered, use the SKUs from order
                if plan.context.current_order:
                    order = plan.context.current_order
                    if hasattr(order, 'products_ordered') and order.products_ordered:
                        # Pick the first SKU for lookup
                        return {
                            "product_identifier": order.products_ordered[0],
                            "include_recommendations": True
                        }
                
                # If we have found products, use those
                if plan.context.found_products:
                    first_product = plan.context.found_products[0]
                    if hasattr(first_product, 'sku'):
                        return {
                            "product_identifier": first_product.sku,
                            "include_recommendations": True
                        }
                
            # For other tools, return None to use default parameter extraction
            return None
                
        except Exception as e:
            logger.exception(f"Error enhancing parameters with context: {e}")
            return None
    
    def _retry_planning_with_full_context(self, plan: EvolvingPlan, user_input: str, tool_orchestrator: ToolOrchestrator) -> List[str]:
        """Let LLM analyze full conversation context and choose appropriate tools."""
        if not self.llm_service:
            return []
        
        try:
            # Get available tools from registry
            available_tools = tool_orchestrator.get_available_tools()
            tool_descriptions = tool_orchestrator.get_tools_for_llm_planning()
            
            # Build rich context description
            context_info = []
            
            if plan.context.current_order:
                order = plan.context.current_order
                context_info.append(f"Current Order: {getattr(order, 'order_number', 'N/A')} for {getattr(order, 'customer_name', 'N/A')}")
                if hasattr(order, 'products_ordered') and order.products_ordered:
                    context_info.append(f"Ordered Products (SKUs): {', '.join(order.products_ordered)}")
            
            if plan.context.found_products:
                products = plan.context.found_products[:3]
                product_names = [getattr(p, 'product_name', 'Unknown') for p in products]
                context_info.append(f"Previously Found Products: {', '.join(product_names)}")
            
            if plan.executed_steps:
                executed = [step.tool_name for step in plan.executed_steps]
                context_info.append(f"Already Executed: {', '.join(executed)}")
            
            context_summary = "\n".join(context_info) if context_info else "No previous context"
            
            # Create a focused prompt for the LLM
            prompt = f"""You are helping a customer service agent choose the right tool(s) for a customer request.

CUSTOMER REQUEST: "{user_input}"

CONVERSATION CONTEXT:
{context_summary}

AVAILABLE TOOLS:
{tool_descriptions}

Based on the customer's request and the conversation context above, which tool(s) should be used?

INSTRUCTIONS:
- Consider what the customer is asking for and what context is already available
- If asking about "products I ordered" and we have order context with SKUs, use get_product_info
- If asking for recommendations and we have order/product context, use get_recommendations
- If asking to browse/search without specific context, use browse_catalog
- Return ONLY the tool name(s), comma-separated if multiple needed
- If no tool is appropriate, return "conversational_response"

RESPONSE (tool names only):"""

            # Use thinking model for better analysis
            from sierra_agent.ai.prompt_types import Prompt
            prompt_obj = Prompt(system_prompt=prompt, user_message="", temperature=0.1)
            response = self.llm_service.thinking_client.call_llm(prompt_obj)
            
            # Parse response
            response = response.strip().lower()
            if 'conversational_response' in response:
                return []
            
            # Extract tool names
            suggested_tools = []
            if ',' in response:
                tools = [t.strip() for t in response.split(',')]
            else:
                tools = [response.strip()]
            
            # Validate tools exist
            for tool in tools:
                if tool in available_tools:
                    suggested_tools.append(tool)
            
            return suggested_tools[:2]  # Max 2 tools
            
        except Exception as e:
            logger.exception(f"Error in context-aware retry planning: {e}")
            return []
    
    def _execute_single_action(self, plan: EvolvingPlan, action: str, user_input: str, tool_orchestrator: ToolOrchestrator) -> Tuple[EvolvingPlan, str]:
        """Execute a single action and return response."""
        # Enhance parameters with LLM intelligence if needed
        enhanced_params = self._enhance_parameters_with_llm(plan, action, user_input)
        
        # Execute the action with enhanced parameters
        executed_step = plan.execute_action(action, user_input, tool_orchestrator, enhanced_params)
        
        if not executed_step:
            # Action couldn't be executed (missing parameters)
            missing_info = self._get_missing_info_message(action, plan)
            return plan, missing_info
        
        if not executed_step.was_successful:
            # Action failed
            return plan, f"I encountered an error: {executed_step.result.error}"
        
        # Use LLM to check if this tool actually addressed what the user asked for
        if self.llm_service:
            tool_result_summary = executed_step.result.serialize_for_context()[:200]  # Truncate for LLM
            validation = self.llm_service.validate_tool_addressed_request(
                user_request=user_input,
                tool_executed=executed_step.tool_name,
                tool_result_summary=tool_result_summary,
                plan_context=plan.context
            )
            
            # Be more lenient - if we have successful tool results, trust that the right tool was selected
            if not validation.get("addressed", True) and not executed_step.result_data:
                # Tool didn't address the request AND we have no useful data - use LLM-generated specific request
                missing_info = validation.get("missing_request") or "I need more information to help with your request."
                return plan, missing_info
        
        # Tool succeeded and addressed the request - return formatted response
        response = self._format_success_response(executed_step, user_input)
        return plan, response
    
    def _execute_multistep_actions(self, plan: EvolvingPlan, actions: List[str], user_input: str, tool_orchestrator: ToolOrchestrator) -> Tuple[EvolvingPlan, str]:
        """Execute multiple actions in sequence and return combined response."""
        all_results = []
        
        for i, action in enumerate(actions):
            # Enhance parameters with LLM intelligence if needed
            enhanced_params = self._enhance_parameters_with_llm(plan, action, user_input)
            
            # Execute the action with enhanced parameters
            executed_step = plan.execute_action(action, user_input, tool_orchestrator, enhanced_params)
            
            if not executed_step:
                # Action couldn't be executed (missing parameters) - stop here
                missing_info = self._get_missing_info_message(action, plan)
                return plan, missing_info
            
            if not executed_step.was_successful:
                # Action failed - stop here
                return plan, f"I encountered an error on step {i+1}: {executed_step.result.error}"
            
            all_results.append(executed_step)
        
        # Generate response using all results combined
        if self.llm_service:
            try:
                # Combine all tool results for LLM context
                combined_tool_results = [
                    ToolResult(data=step.result_data, success=step.was_successful, error=step.result.error)
                    for step in all_results
                ]
                
                response = self.llm_service.generate_customer_service_response(
                    user_input=user_input,
                    tool_results=combined_tool_results,
                    plan_context=plan.context,
                    use_thinking_model=False
                )
                return plan, response
            except Exception as e:
                logger.exception(f"Error generating multistep LLM response: {e}")
        
        # Fallback: combine individual responses
        response_parts = []
        for step in all_results:
            individual_response = self._format_template_response_for_multistep(step)
            response_parts.append(individual_response)
        
        return plan, "\n\n".join(response_parts)
    
    def _format_template_response_for_multistep(self, executed_step: ExecutedStep) -> str:
        """Generate a simple response for multistep fallback."""
        tool_name = executed_step.tool_name
        if tool_name == "get_order_status":
            return "✅ Order details retrieved"
        elif tool_name == "get_product_details":
            return "✅ Product information retrieved"
        elif tool_name == "get_product_recommendations":
            return "✅ Product recommendations found"
        else:
            return f"✅ {tool_name.replace('_', ' ').title()} completed"