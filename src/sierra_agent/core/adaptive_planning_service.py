"""Adaptive Planning Service

Clean, strongly typed planning service that manages evolving conversation plans.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from sierra_agent.ai.llm_service import LLMService
from sierra_agent.core.planning_types import EvolvingPlan, ExecutedStep
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
            
            prompt = f"""Determine if the new user input is related to the existing conversation plan or represents a completely different topic.

Current Plan Context: {plan_context}
New User Input: "{user_input}"

Instructions:
1. Consider if the new input is:
   - A follow-up question about the same topic
   - Providing missing information (email, order number, clarification)
   - A refinement or continuation of the current request
   
2. OR if it's a completely different topic that should start fresh:
   - Asking about orders when current plan is about promotions
   - Asking about products when current plan is about orders
   - Any major topic shift that's unrelated

Examples:
- Plan: "tell me about early risers", New: "the discount" → RELATED (clarification)
- Plan: "tell me about early risers", New: "am i eligible" → RELATED (follow-up)
- Plan: "tell me about early risers", New: "george.hill@example.com" → RELATED (providing info)
- Plan: "tell me about early risers", New: "tell me about my order" → NOT_RELATED (topic change)
- Plan: "my order status", New: "#W009" → RELATED (providing missing order number)

Return only: "RELATED" or "NOT_RELATED" """

            response = self.llm_service.low_latency_client.call_llm(prompt, temperature=0.1)
            response_clean = response.strip().upper()
            return response_clean == "RELATED"
            
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
            # No clear action determined
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
            
            prompt = f"""Generate a direct, specific request for missing information needed to help the customer.

Action Needed: {action}
Available Context: {context_summary}
Missing Information: {missing_summary}

Instructions:
1. Be direct and specific about exactly what you need
2. Don't ask for "related items" - ask for the specific missing parameters
3. Keep it concise and friendly
4. Make it clear what the customer should provide next

Examples:
- "I need your order number to look up your order."
- "I need your email address to find your order."
- "What products are you looking for?"

Response: Just the direct request (e.g., "I need your order number.")"""
            
            response = self.llm_service.low_latency_client.call_llm(prompt, temperature=0.1)
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
            
            prompt = f"""Generate a friendly customer service response for Sierra Outfitters, an outdoor gear company. Use enthusiastic outdoor/adventure branding and tone.

Customer said: "{user_input}"
Response Type: {response_type}

Instructions:
1. Match the response to what the customer said ({response_type})
2. Use outdoor/adventure themes and enthusiasm  
3. Include Sierra Outfitters branding elements like:
   - Mountain emoji 🏔️
   - Adventure/outdoor language ("adventure", "trail", "summit", etc.)
   - Enthusiastic tone with exclamation points
   - References to the unknown, exploration, outdoor spirit
4. For greetings: Welcome them warmly and ask how you can help with their adventure
5. For thanks: Acknowledge appreciatively and offer continued support  
6. For help requests: Express excitement to help and ask what they need specifically
7. Keep it concise but branded (2-3 sentences)

Examples:
- Greeting: "Hello there, fellow adventurer! 🏔️ Welcome to Sierra Outfitters! I'm excited to help you gear up for your next outdoor expedition. What adventure can I help you prepare for today?"
- Thanks: "You're absolutely welcome! 🏔️ It's my pleasure to help fellow outdoor enthusiasts. May your trails be scenic and your adventures unforgettable!"
- Help: "I'm thrilled to help you with your outdoor adventures! 🏔️ Whether you're looking for gear recommendations, checking on orders, or exploring our latest promotions, I'm here to guide you. What can I assist you with today?"

Response:"""
            
            response = self.llm_service.low_latency_client.call_llm(prompt, temperature=0.3)
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
            
            prompt = f"""Generate a friendly customer service response based on the tool execution.

User Request: "{user_input}"
Tool Executed: {tool_name}
Result: {data_summary}

Instructions:
1. Acknowledge what was found/done
2. Be helpful and customer-focused
3. Keep it concise but informative
4. Don't make up specific details not provided

Response: Just the customer service message"""
            
            response = self.llm_service.low_latency_client.call_llm(prompt, temperature=0.3)
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
            # Prepare available data from plan context
            available_data: Dict[str, Any] = {}
            if plan.context.current_order:
                available_data["current_order"] = plan.context.current_order
            if plan.context.found_products:
                available_data["found_products"] = plan.context.found_products
            if plan.context.customer_email:
                available_data["customer_email"] = plan.context.customer_email
            if plan.context.order_number:
                available_data["order_number"] = plan.context.order_number
            
            # Determine conversation phase based on executed steps
            conversation_phase = "greeting" if not plan.executed_steps else "exploration"
            if len(plan.executed_steps) > 3:
                conversation_phase = "resolution"
            
            # Determine current topic from context
            current_topic = "general"
            if plan.context.current_order:
                current_topic = "order_management"
            elif plan.context.found_products:
                current_topic = "product_inquiry"
            
            # Get available tools dynamically from tool orchestrator
            available_tools = tool_orchestrator.get_available_tools()
            
            # Use specialized LLM analysis for vague requests and contextual suggestions
            suggested_actions = self.llm_service.analyze_vague_request_and_suggest(
                user_input=user_input,
                available_data=available_data,
                conversation_context=f"Phase: {conversation_phase}, Topic: {current_topic}, Executed: {[step.tool_name for step in plan.executed_steps]}",
                available_tools=available_tools
            )
            
            # Return all suggested actions for multistep execution
            return suggested_actions
            
        except Exception as e:
            logger.exception(f"Error in LLM planning: {e}")
            # Fallback to simple logic
            action = plan.determine_next_action(user_input)
            return [action] if action else []
    
    def _enhance_parameters_with_llm(self, plan: EvolvingPlan, action: str, user_input: str) -> Optional[Dict[str, Any]]:
        """Use LLM to enhance parameters for specific actions like recommendations."""
        if action == "get_product_recommendations" and self.llm_service:
            try:
                # Use LLM to generate smart search terms based on order/product context
                order_context = {}
                if plan.context.current_order:
                    order_context["current_order"] = plan.context.current_order
                
                product_context = plan.context.found_products if plan.context.found_products else []
                
                # Generate intelligent search terms
                search_terms = self.llm_service.generate_recommendation_search_terms(
                    order_context=order_context,
                    product_context=product_context
                )
                
                # Convert search terms to preferences list
                preferences = search_terms.split()
                
                # Return enhanced parameters
                return {"category": None, "preferences": preferences}
                
            except Exception as e:
                logger.exception(f"Error enhancing parameters with LLM: {e}")
                return None
        
        # Return None for other actions - plan will use default parameter extraction
        return None
    
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
                conversation_context=f"Original request: {plan.original_request}"
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