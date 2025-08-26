"""
Consolidated Prompt Templates

All LLM prompt generation consolidated in one place to replace scattered inline prompts
throughout the codebase. This avoids circular imports and centralizes prompt management.
"""

from typing import List
from sierra_agent.core.planning_types import ConversationContext
from .prompt_types import Prompt


class PromptTemplates:
    """Centralized prompt template generation."""
    
    @staticmethod
    def build_plan_continuation_prompt(plan_context: ConversationContext, user_input: str, existing_request: str) -> Prompt:
        """Replace adaptive_planning_service.py:61-90 inline prompt"""
        context_info = ""
        if plan_context.current_order:
            context_info += f"\nExisting order context: {plan_context.current_order.order_number}"
        if plan_context.found_products:
            context_info += f"\nExisting product context: {len(plan_context.found_products)} products found"
        
        system_prompt = f"""Determine if the new user input is related to the existing conversation plan or represents a completely different topic.

Context Information: {context_info}

Instructions:
1. If the new input is RELATED to the existing request (follow-up, clarification, additional info), respond with: CONTINUE
2. If the new input is a COMPLETELY DIFFERENT topic/request, respond with: NEW_PLAN
3. Consider context - if user provided email/order info before and now asks about products, that's RELATED
4. Consider natural conversation flow - "what about products" after order lookup is RELATED

Examples:
- Existing: "check my order", New: "john@email.com" → CONTINUE
- Existing: "find hiking boots", New: "what's your return policy" → NEW_PLAN
- Existing: "order status for W001", New: "what products are in it" → CONTINUE

Provide your decision."""
        
        user_message = f'Existing Plan Request: "{existing_request}"\nNew User Input: "{user_input}"'
        
        json_schema = {
            "type": "object",
            "properties": {
                "decision": {
                    "type": "string",
                    "enum": ["CONTINUE", "NEW_PLAN"],
                    "description": "Whether to continue with existing plan or create new plan"
                }
            },
            "required": ["decision"],
            "additionalProperties": False
        }
        
        return Prompt(
            system_prompt=system_prompt,
            user_message=user_message,
            expected_json_schema=json_schema,
            use_structured_output=True,  # Use API structured output properly
            temperature=0.1
        )

    @staticmethod
    def build_missing_info_prompt(plan_context: ConversationContext, user_input: str) -> Prompt:
        """Replace adaptive_planning_service.py:166-195 inline prompt"""
        system_prompt = f"""Generate a direct, specific request for missing information needed to help the customer.

Context:
- Customer Email: {plan_context.customer_email or 'Not provided'}
- Order Number: {plan_context.order_number or 'Not provided'}

Instructions:
1. Be specific about what information is needed
2. Use friendly outdoor/adventure tone with Sierra Outfitters branding
3. Include mountain emoji 🏔️
4. Explain why the information is needed
5. Keep it concise but helpful

Generate a friendly request for the missing information needed to help this customer."""
        
        user_message = f'Customer Input: "{user_input}"'
        
        return Prompt(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.7
        )

    @staticmethod
    def build_no_data_response_prompt(plan_context: ConversationContext, user_input: str, response_type: str = "general") -> Prompt:
        """Replace adaptive_planning_service.py:235-270 inline prompt"""
        system_prompt = f"""Generate a friendly customer service response for Sierra Outfitters, an outdoor gear company. Use enthusiastic outdoor/adventure branding and tone.

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

Generate an enthusiastic, outdoor-branded response."""
        
        user_message = f'Customer said: "{user_input}"'
        
        return Prompt(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.7
        )


    @staticmethod
    def build_vague_request_analysis_prompt(plan_context: ConversationContext, user_input: str, available_tools: List[str], tools_description: str = None) -> Prompt:
        """Build prompt using dynamic tools from tool orchestrator"""
        context_summary = ""
        if plan_context.customer_email:
            context_summary += f"Customer email: {plan_context.customer_email}\n"
        if plan_context.customer_name:
            context_summary += f"Customer name: {plan_context.customer_name}\n"
        if plan_context.order_number:
            context_summary += f"Order number: {plan_context.order_number}\n"
        if plan_context.current_order:
            context_summary += f"Current order: {plan_context.current_order.order_number}\n"
        if plan_context.found_products:
            context_summary += f"Found products: {len(plan_context.found_products)} items\n"
        
        # Use provided tools description (from tool orchestrator) or fallback
        if not tools_description:
            tools_description = "\n".join([f"- {tool}" for tool in available_tools])
        
        system_prompt = f"""You are an intelligent customer service workflow planner for Sierra Outfitters outdoor gear company. Your job is to analyze what the customer wants and determine the best response approach.

Available Context: {context_summary or "No context available"}

Available Tools:
{tools_description}

STEP 1 - ANALYZE THE REQUEST TYPE:

A) CONVERSATIONAL REQUESTS (respond conversationally, no tools needed):
   - Greetings: "hello", "hi", "hey" (standalone, not followed by specific requests) → return "conversational_response"
   - Thanks: "thanks", "thank you" → return "conversational_response"  
   - General help: "I need help", "can you help" (without any context or specifics) → return "conversational_response"
   - General questions: "what can you do", "what services" → return "conversational_response"
   - IMPORTANT: If user provides email, order numbers, or specific product info, DO NOT treat as conversational

B) INFORMATION REQUESTS (use tools to get specific data):
   - Order questions: "my order", "order status", "track order" + email/order# → get_order_status
   - Product search: "show me", "what products", "looking for [product]" → browse_catalog
   - Product details: "tell me about [specific product]" → get_product_info
   - Product details from order: "tell me about the products i ordered", "what did i buy" (when order context available) → get_product_info (if multiple products in order, return "get_product_info" for EACH SKU as comma-separated)
   - Recommendations: "recommend", "suggest products" → get_recommendations
   - Promotions: "discount", "promotion", "deal", "early risers", "tell me about early risers" → get_early_risers_promotion
   - Company info: "about company", "contact" → get_company_info

C) MULTI-STEP REQUESTS (use multiple tools in sequence):
   - "check my order and give recommendations" → get_order_status,get_recommendations
   - "tell me about the products I ordered and recommend similar items" → get_product_info,get_recommendations
   - "tell me about my ordered products" (when multiple products in order) → get_product_info (for each SKU)
   - "show me products and tell me about deals" → browse_catalog,get_early_risers_promotion

STEP 2 - CHECK FOR MISSING INFORMATION:
   - For get_order_status: need email AND order_number
     * If we have BOTH email and order_number in available context → use get_order_status
     * If missing either email or order_number → return "wait_for_missing_info"
   - For get_product_info: need product_identifier (SKU or name)
     * If asking about ordered products and order has multiple SKUs, plan to call get_product_info for each SKU
   - For browse_catalog: can work without parameters or with search terms
   - For get_recommendations: can use order context or customer preferences
   - IMPORTANT: Check available context first before assuming missing information

STEP 3 - DETERMINE RESPONSE:
   - Conversational requests: return "conversational_response"
   - Single tool needed: return the tool name
   - Multiple tools needed: return comma-separated tool names
   - Missing info: return "wait_for_missing_info"

EXAMPLES:
- "hello" → "conversational_response"
- "thanks for your help" → "conversational_response"
- "I need help" (no context) → "conversational_response"
- "do you have promotions?" → "get_early_risers_promotion"
- "tell me about early risers" → "get_early_risers_promotion"
- "show me backpacks" → "browse_catalog"
- "my order george.hill@example.com #W009" → "get_order_status"
- "tell me about my order" (no email/order#) → "wait_for_missing_info"
- "#W006" (context has email: dana@example.com) → "get_order_status"
- "W006" (context has email: dana@example.com) → "get_order_status" 
- "dana@example.com" (context has order#: #W006) → "get_order_status"
- "what do you recommend?" → "get_recommendations"
- "I want" (incomplete) → "conversational_response"

Determine the appropriate action to take."""
        
        user_message = f'Customer Request: "{user_input}"'
        
        json_schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The response type or tool name(s) to execute"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }
        
        return Prompt(
            system_prompt=system_prompt,
            user_message=user_message,
            expected_json_schema=json_schema,
            use_structured_output=True,  # Use API structured output properly
            temperature=0.1
        )

    @staticmethod
    def build_tool_validation_prompt(user_request: str, tool_executed: str, tool_result_summary: str, plan_context: ConversationContext) -> Prompt:
        """Replace llm_service.py:234-255 inline prompt"""
        context_info = plan_context.get_tool_validation_context("context available") if plan_context else ""
        
        system_prompt = f"""Analyze if the executed tool properly addressed the user's request.

Instructions:
1. Did the executed tool directly address what the user asked for?
2. If user asked about "order" but tool got "contact info", that's WRONG
3. If user provided order number but tool got "company info", that's WRONG  
4. If user asked for recommendations but tool got random products, that's WRONG

Context Information: {context_info}

Respond with JSON containing:
- "addressed": true/false indicating if the tool addressed the request
- "reason": explanation for your decision
- "missing_request": specific question to ask user or null if none needed

Examples:
- User: "tell me about my order", Tool: "get_company_info" → {{"addressed": false, "reason": "user wanted order info but got company info", "missing_request": "I need your order number to look up your order."}}
- User: "george@email.com", Tool: "get_company_info" → {{"addressed": false, "reason": "user provided email for order lookup but got company info", "missing_request": "Great! I have your email. Now I need your order number."}}
- User: "#W006", Tool: "get_order_status" → {{"addressed": true, "reason": "order number provided and order lookup performed", "missing_request": null}}"""
        
        user_message = f'User Request: "{user_request}"\nTool Executed: {tool_executed}\nTool Result: {tool_result_summary}'
        
        json_schema = {
            "type": "object",
            "properties": {
                "addressed": {
                    "type": "boolean",
                    "description": "Whether the executed tool properly addressed the user's request"
                },
                "reason": {
                    "type": "string",
                    "description": "Explanation for the decision"
                },
                "missing_request": {
                    "type": ["string", "null"],
                    "description": "Specific question to ask user or null if none needed"
                }
            },
            "required": ["addressed", "reason", "missing_request"],
            "additionalProperties": False
        }
        
        return Prompt(
            system_prompt=system_prompt,
            user_message=user_message,
            expected_json_schema=json_schema,
            use_structured_output=True,  # Use API structured output properly
            temperature=0.1
        )