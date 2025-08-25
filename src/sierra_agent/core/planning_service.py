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
from typing import Any, Dict, List, Optional, TypedDict

from ..data.data_types import (
    MultiTurnPlan,
    PlanStatus,
    PlanStep,
    ToolResult,
)

logger = logging.getLogger(__name__)


# Strong typing for planning methods
class ContextReferences(TypedDict):
    """Results from context reference extraction."""
    references_previous: bool
    extracted_info: Dict[str, str]
    needs_product_details: Optional[bool]
    needs_recommendations: Optional[bool]
    confidence: float


class RequestAnalysis(TypedDict):
    """Results from user request analysis."""
    needs: List[str]
    references_previous: bool
    user_input_lower: str


class PlanningAnalysis(TypedDict):
    """Complete planning analysis results."""
    available_data: Dict[str, Any]
    request_needs: List[str]
    references_previous: bool
    context_references: ContextReferences
    suggested_steps: List[str]
    planning_method: str
    conversation_context: Dict[str, Any]
    user_input: str


class PlanningService:
    """Service responsible for analyzing requests and generating execution plans."""

    def __init__(self, llm_client=None, tool_orchestrator=None):
        """Initialize the planning service with optional dependencies."""
        print("🎯 [PLANNING] Initializing enhanced planning service...")
        
        # Store dependencies for intelligent planning
        self.llm_client = llm_client
        self.tool_orchestrator = tool_orchestrator
        
        # Initialize LLM client if not provided
        if self.llm_client is None:
            try:
                from ..ai.llm_client import LLMClient
                self.llm_client = LLMClient(model_name="gpt-4o-mini", max_tokens=1000)
                print("🎯 [PLANNING] LLM client initialized for intelligent planning")
            except Exception as e:
                print(f"⚠️ [PLANNING] Could not initialize LLM client: {e}")
                self.llm_client = None
        
        print("🎯 [PLANNING] Enhanced planning service initialized successfully")
        logger.info("Enhanced PlanningService initialized")




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
    
    def suggest_steps_with_llm(self, user_input: str, available_data: Dict[str, Any]) -> List[str]:
        """Use LLM to intelligently suggest required steps based on context."""
        print(f"🤖 [PLANNING] Using LLM to suggest steps for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        if not self.llm_client:
            print("⚠️ [PLANNING] No LLM client available, falling back to rule-based planning")
            return self.suggest_steps_rule_based(user_input, available_data)
        
        try:
            # Build the planning prompt
            available_data_summary = self._format_available_data_for_llm(available_data)
            available_tools_description = self._get_available_tools_description()
            
            prompt = f"""You are a customer service planning assistant for Sierra Outfitters outdoor gear company. 
Analyze the customer's request and suggest the specific steps needed to fulfill it.

Customer Request: "{user_input}"

Available Context Data:
{available_data_summary}

Available Tools:
{available_tools_description}

Rules:
1. If customer mentions specific order number/email, use get_order_status tool
2. If we already have order data and customer wants related products, use get_product_recommendations tool
3. For general product requests, use search_products tool
4. Always suggest the minimum necessary steps to fulfill the request
5. Consider available context to avoid redundant data fetching
6. Only suggest tools that are available in the system

Respond with ONLY a JSON array of tool names from the available tools list, no other text:
["tool1", "tool2"]"""

            print("🤖 [PLANNING] Sending planning request to LLM...")
            # Call LLM directly for planning, not through the response generation system
            try:
                from openai import OpenAI
                openai_client = OpenAI(api_key=self.llm_client.api_key)
                
                response_obj = openai_client.chat.completions.create(
                    model=self.llm_client.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,  # Shorter limit for planning
                    temperature=0.1  # Lower temperature for more consistent JSON
                )
                
                response = response_obj.choices[0].message.content
                if response is None:
                    raise ValueError("Empty response from OpenAI")
                response = response.strip()
                print(f"🤖 [PLANNING] LLM planning response ({len(response)} chars): {response[:100]}...")
                
            except Exception as llm_error:
                print(f"❌ [PLANNING] Direct LLM call failed: {llm_error}")
                raise llm_error
            
            # Parse the JSON response
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                json_str = '[' + json_match.group(1) + ']'
                suggested_steps = json.loads(json_str)
                
                # Validate that suggested tools are available
                available_tools = self._get_available_tool_names()
                validated_steps = [step for step in suggested_steps if step in available_tools]
                
                if len(validated_steps) != len(suggested_steps):
                    print(f"⚠️ [PLANNING] Some suggested tools not available, filtered to: {validated_steps}")
                
                print(f"🤖 [PLANNING] LLM suggested {len(validated_steps)} steps: {validated_steps}")
                return validated_steps
            else:
                print("⚠️ [PLANNING] Could not parse LLM response, falling back to rule-based")
                return self.suggest_steps_rule_based(user_input, available_data)
                
        except Exception as e:
            print(f"❌ [PLANNING] Error in LLM planning: {e}")
            print("⚠️ [PLANNING] Falling back to rule-based planning")
            return self.suggest_steps_rule_based(user_input, available_data)
    
    def suggest_steps_rule_based(self, user_input: str, available_data: Dict[str, Any]) -> List[str]:
        """Rule-based step suggestion as fallback."""
        print(f"🔍 [PLANNING] Using rule-based planning for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        steps = []
        user_lower = user_input.lower()
        
        # Check for explicit order requests (order number + email patterns)
        import re
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input))
        has_order_number = bool(re.search(r'#?[wW]\d+|order\s+#?\d+|#\d+', user_input))
        has_order_keywords = any(word in user_lower for word in ["order", "check", "status", "tracking"])
        
        if (has_email and has_order_number) or (has_order_keywords and (has_email or has_order_number)):
            print(f"🔍 [PLANNING] Detected explicit order request - email: {has_email}, order#: {has_order_number}, keywords: {has_order_keywords}")
            steps.append("get_order_status")
        
        # Context-driven step determination for conversational order references
        elif any(ref in user_lower for ref in ["my order", "the order", "that order"]):
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
    
    def analyze_planning_context(self, user_input: str, conversation_data: Dict[str, Any]) -> PlanningAnalysis:
        """Analyze conversation context to determine planning requirements."""
        print(f"🧠 [PLANNING] Analyzing planning context for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        available_data = conversation_data.get("available_data", {})
        
        # NEW: Use low-latency LLM to extract implicit context references
        context_analysis = self._extract_context_references(user_input, available_data)
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
        
        return PlanningAnalysis(
            available_data=available_data,
            request_needs=request_analysis["needs"],
            references_previous=request_analysis["references_previous"] or context_analysis["references_previous"],
            context_references=context_analysis,
            suggested_steps=suggested_steps,
            planning_method="llm" if use_llm else "rule_based",
            conversation_context=conversation_data,
            user_input=user_input  # Add this for step creation
        )
    
    def create_plan_from_analysis(self, planning_analysis: PlanningAnalysis, session_id: Optional[str] = None) -> MultiTurnPlan:
        """Create a complete MultiTurnPlan from planning analysis results."""
        print(f"🔧 [PLANNING] Creating plan from analysis with {len(planning_analysis['suggested_steps'])} steps")
        
        # Convert suggested steps to PlanStep objects
        steps = self._create_plan_steps_from_suggestions(
            planning_analysis["suggested_steps"], 
            planning_analysis
        )
        
        # Create the plan
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        return MultiTurnPlan(
            plan_id=plan_id,
            customer_request=planning_analysis["user_input"],
            steps=steps,
            conversation_context={
                "planning": planning_analysis,
                "execution": {
                    "session_id": session_id,
                    "original_request": planning_analysis["user_input"]
                }
            },
            status=PlanStatus.PENDING,
            created_at=datetime.now()
        )
    
    def _create_plan_steps_from_suggestions(self, suggested_steps: List[str], planning_analysis: PlanningAnalysis) -> List[PlanStep]:
        """Convert suggested step names to actual PlanStep objects with context awareness."""
        steps = []
        available_data = planning_analysis["available_data"]
        user_input = planning_analysis["user_input"]
        context_refs = planning_analysis["context_references"]
        
        print(f"🔧 [PLANNING] Converting {len(suggested_steps)} suggested steps to PlanSteps")
        print(f"🔧 [PLANNING] Available context: {list(available_data.keys())}")
        print(f"🔧 [PLANNING] Context references: {context_refs['references_previous']}")
        
        for step_name in suggested_steps:
            step_id = f"step_{uuid.uuid4().hex[:8]}"
            
            if step_name == "get_order_status":
                # Use extracted context if available
                if context_refs["references_previous"] and context_refs["extracted_info"]:
                    # We have context references, create step that uses the extracted info
                    steps.append(PlanStep(
                        step_id=step_id,
                        name="Get Order Status from Context",
                        description="Retrieve order status using context information",
                        tool_name="get_order_status",
                        parameters={
                            "user_input": user_input,
                            "context_email": context_refs["extracted_info"].get("email"),
                            "context_order_number": context_refs["extracted_info"].get("order_number")
                        }
                    ))
                else:
                    # Standard order status lookup
                    steps.append(PlanStep(
                        step_id=step_id,
                        name="Get Order Status",
                        description="Retrieve order status and tracking information",
                        tool_name="get_order_status",
                        parameters={"user_input": user_input}
                    ))
                    
            elif step_name == "get_product_details":
                # Use existing order data if available
                if "current_order" in available_data:
                    order = available_data["current_order"]
                    steps.append(PlanStep(
                        step_id=step_id,
                        name="Get Product Details",
                        description=f"Get details for products in order {order.order_number}",
                        tool_name="get_product_details",
                        parameters={
                            "user_input": user_input,
                            "product_skus": order.products_ordered,
                            "order_context": True
                        }
                    ))
                else:
                    steps.append(PlanStep(
                        step_id=step_id,
                        name="Get Product Details",
                        description="Get product details",
                        tool_name="get_product_details",
                        parameters={"user_input": user_input}
                    ))
                    
            elif step_name == "get_product_recommendations":
                if "current_order" in available_data:
                    order = available_data["current_order"]
                    steps.append(PlanStep(
                        step_id=step_id,
                        name="Get Product Recommendations", 
                        description=f"Find products related to order {order.order_number}",
                        tool_name="get_product_recommendations",
                        parameters={
                            "user_input": user_input,
                            "related_to_skus": order.products_ordered,
                            "order_context": True
                        }
                    ))
                else:
                    steps.append(PlanStep(
                        step_id=step_id,
                        name="Get Product Recommendations",
                        description="Find recommended products",
                        tool_name="get_product_recommendations",
                        parameters={"user_input": user_input}
                    ))
                    
            elif step_name == "search_products":
                steps.append(PlanStep(
                    step_id=step_id,
                    name="Search Products",
                    description="Search and recommend relevant products",
                    tool_name="search_products",
                    parameters={"user_input": user_input}
                ))
                
            elif step_name == "get_early_risers_promotion":
                steps.append(PlanStep(
                    step_id=step_id,
                    name="Check Early Risers Promotion",
                    description="Check for available promotions",
                    tool_name="get_early_risers_promotion",
                    parameters={"user_input": user_input}
                ))
                
            else:  # handle_general_inquiry or unknown
                steps.append(PlanStep(
                    step_id=step_id,
                    name="Handle General Inquiry",
                    description="Provide general customer service assistance",
                    tool_name="handle_general_inquiry",
                    parameters={"user_input": user_input}
                ))
        
        print(f"🔧 [PLANNING] Created {len(steps)} PlanSteps from suggestions")
        return steps
    
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
    
    def _analyze_user_request(self, user_input: str, available_data: Dict[str, Any]) -> RequestAnalysis:
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
        
        # Check for explicit order requests (should use LLM for better accuracy)
        import re
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input))
        has_order_number = bool(re.search(r'#?[wW]\d+|order\s+#?\d+|#\d+', user_input))
        has_order_keywords = any(word in user_lower for word in ["order", "check", "status", "tracking"])
        
        # Complex indicators
        complexity_indicators = [
            len(user_input.split()) > 10,  # Long requests
            any(word in user_lower for word in ["and", "but", "also", "plus"]),  # Multiple requests
            any(word in user_lower for word in ["similar", "related", "like", "recommend"]),  # Relational requests
            user_input.count("?") > 1,  # Multiple questions
            (has_email and has_order_number),  # Explicit order requests with both email and order number
            (has_order_keywords and (has_email or has_order_number)),  # Order requests with one identifier
        ]
        
        return any(complexity_indicators)
    
    def _extract_context_references(self, user_input: str, available_data: Dict[str, Any]) -> ContextReferences:
        """Use low-latency LLM to extract implicit context references from user input."""
        print(f"🔍 [CONTEXT] Analyzing context references for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        # If no available data, return empty analysis
        if not available_data:
            print("🔍 [CONTEXT] No available context data")
            return ContextReferences(
                references_previous=False, 
                extracted_info={}, 
                needs_product_details=False,
                needs_recommendations=False,
                confidence=0.0
            )
        
        # Check for obvious context references first (rule-based)
        user_lower = user_input.lower()
        context_keywords = ["my order", "the order", "that order", "my", "the", "this", "it"]
        has_context_references = any(keyword in user_lower for keyword in context_keywords)
        
        if not has_context_references:
            print("🔍 [CONTEXT] No context reference keywords detected")
            return ContextReferences(
                references_previous=False, 
                extracted_info={}, 
                needs_product_details=False,
                needs_recommendations=False,
                confidence=0.0
            )
        
        # Use low-latency LLM to extract specific references and information
        if not self.llm_client:
            print("⚠️ [CONTEXT] No LLM available for context extraction")
            return ContextReferences(
                references_previous=True, 
                extracted_info={}, 
                needs_product_details=False,
                needs_recommendations=False,
                confidence=0.5
            )
        
        try:
            # Format available data for LLM context
            available_context = self._format_available_data_for_context_extraction(available_data)
            
            prompt = f"""You are analyzing a customer service conversation to extract implicit references.

CUSTOMER'S LATEST MESSAGE: "{user_input}"

AVAILABLE CONVERSATION CONTEXT:
{available_context}

TASK: Determine what the customer is referring to and extract specific information.

RULES:
1. If customer says "my order", "the order", extract: email and order_number from context
2. If customer asks about "products in my order", extract: email, order_number, and set needs_product_details=true  
3. If customer wants recommendations "like my order", extract: email, order_number, and set needs_recommendations=true
4. Only extract information that exists in the available context
5. Be conservative - only extract if you're confident

RESPOND WITH JSON ONLY:
{{
  "references_previous": true/false,
  "extracted_email": "email@domain.com" or null,
  "extracted_order_number": "W123" or null, 
  "needs_product_details": true/false,
  "needs_recommendations": true/false,
  "confidence": 0.0-1.0
}}"""

            print("🔍 [CONTEXT] Sending context extraction request to LLM...")
            
            # Use low-latency LLM for fast context extraction
            response = self._call_llm_directly(prompt, max_tokens=200, temperature=0.1)
            
            print(f"🔍 [CONTEXT] LLM response: {response[:100]}...")
            
            # Parse JSON response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                context_info = json.loads(json_match.group(0))
                
                print(f"🔍 [CONTEXT] Extracted context: {context_info}")
                
                # Build extracted info dict
                extracted_info = {}
                if context_info.get("extracted_email"):
                    extracted_info["email"] = context_info["extracted_email"]
                if context_info.get("extracted_order_number"):
                    extracted_info["order_number"] = context_info["extracted_order_number"]
                
                return ContextReferences(
                    references_previous=context_info.get("references_previous", False),
                    extracted_info=extracted_info,
                    needs_product_details=context_info.get("needs_product_details", False),
                    needs_recommendations=context_info.get("needs_recommendations", False),
                    confidence=context_info.get("confidence", 0.5)
                )
            else:
                print("⚠️ [CONTEXT] Could not parse LLM response")
                return ContextReferences(
                    references_previous=True, 
                    extracted_info={}, 
                    needs_product_details=False,
                    needs_recommendations=False,
                    confidence=0.3
                )
                
        except Exception as e:
            print(f"❌ [CONTEXT] Error in context extraction: {e}")
            return ContextReferences(
                references_previous=True, 
                extracted_info={}, 
                needs_product_details=False,
                needs_recommendations=False,
                confidence=0.0
            )
    
    def _format_available_data_for_context_extraction(self, available_data: Dict[str, Any]) -> str:
        """Format available data specifically for context extraction."""
        if not available_data:
            return "No previous context available."
        
        formatted = []
        for key, value in available_data.items():
            if key == "current_order" and hasattr(value, 'order_number'):
                formatted.append(f"Previous Order Found:")
                formatted.append(f"  - Order Number: {value.order_number}")
                formatted.append(f"  - Customer: {value.customer_name}")  
                formatted.append(f"  - Email: {value.email}")
                formatted.append(f"  - Status: {value.status}")
                formatted.append(f"  - Products: {', '.join(value.products_ordered)}")
            elif key == "recent_products" and isinstance(value, list):
                formatted.append(f"Recent Products Found: {len(value)} products")
        
        return "\n".join(formatted) if formatted else "Context data available but not formatted."
    
    def _call_llm_directly(self, prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
        """Direct LLM call for context extraction - reuse the existing direct call logic."""
        try:
            from openai import OpenAI
            openai_client = OpenAI(api_key=self.llm_client.api_key)
            
            response_obj = openai_client.chat.completions.create(
                model=self.llm_client.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response_obj.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from OpenAI")
            return content.strip()
        except Exception as e:
            print(f"❌ [CONTEXT] Direct LLM call failed: {e}")
            raise e
    
    def update_plan_with_low_latency_llm(self, plan: MultiTurnPlan, execution_results: List[ToolResult], low_latency_llm) -> List[str]:
        """Update plan using low-latency LLM based on execution results."""
        print(f"🔄 [PLANNING] Updating plan using low-latency LLM after {len(execution_results)} execution results")
        
        if not low_latency_llm:
            print("⚠️ [PLANNING] No low-latency LLM available for plan updates")
            return []
        
        try:
            # Build context from execution results
            execution_summary = self._format_execution_results(execution_results)
            remaining_steps = [step for step in plan.steps if not step.is_completed]
            
            prompt = f"""You are updating a customer service plan based on execution results.

Original Request: "{plan.customer_request}"

Execution Results So Far:
{execution_summary}

Remaining Steps:
{[step.tool_name for step in remaining_steps]}

Available Tools:
{self._get_available_tools_description()}

Based on the execution results, should we:
1. Continue with remaining steps as planned
2. Add new steps to handle unexpected results
3. Skip steps that are no longer needed

Respond with ONLY a JSON array of tool names for the next steps:
["tool1", "tool2"]"""

            response = low_latency_llm.generate_response({
                "user_input": prompt,
                "intent": "plan_update",
                "primary_tool_result": None
            })
            
            # Parse the JSON response
            import json
            import re
            
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                json_str = '[' + json_match.group(1) + ']'
                updated_steps = json.loads(json_str)
                
                # Validate tools are available
                available_tools = self._get_available_tool_names()
                validated_steps = [step for step in updated_steps if step in available_tools]
                
                print(f"🔄 [PLANNING] Low-latency LLM suggested {len(validated_steps)} updated steps: {validated_steps}")
                return validated_steps
            else:
                print("⚠️ [PLANNING] Could not parse plan update response")
                return []
                
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