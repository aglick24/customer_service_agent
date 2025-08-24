"""
Tool Orchestrator

This module coordinates the execution of various business tools based on
customer intent and provides a unified interface for tool management.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass

from ..data.data_types import IntentType, ToolResult
from .business_tools import BusinessTools
from ..ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionResult:
    """Result of tool execution."""
    tool_name: str
    success: bool
    data: Any
    execution_time: float
    error_message: Optional[str] = None


class ToolOrchestrator:
    """Orchestrates the execution of business tools based on customer intent."""
    
    def __init__(self, low_latency_llm: Optional[Union[Any, 'LLMClient']] = None) -> None:
        print("🎭 [ORCHESTRATOR] Initializing ToolOrchestrator...")
        
        self.business_tools = BusinessTools()
        print("🎭 [ORCHESTRATOR] Business tools initialized")
        
        # Map intents to specific tools
        self.intent_tool_mapping = {
            IntentType.ORDER_STATUS: ["get_order_status", "get_order_details", "get_shipping_info"],
            IntentType.PRODUCT_INQUIRY: ["search_products", "get_product_details", "get_product_recommendations"],
            IntentType.CUSTOMER_SERVICE: ["get_company_info", "get_contact_info", "get_policies"],
            IntentType.COMPLAINT: ["log_complaint", "get_escalation_info"],
            IntentType.RETURN_REQUEST: ["get_return_policy", "initiate_return"],
            IntentType.SHIPPING_INFO: ["get_shipping_options", "calculate_shipping", "get_tracking_info"],
            IntentType.PROMOTION_INQUIRY: ["get_current_promotions", "check_discounts", "get_sale_items"]
        }
        print(f"🎭 [ORCHESTRATOR] Mapped {len(self.intent_tool_mapping)} intent types to tools")
        
        # Custom tools registry
        self.custom_tools: Dict[str, Callable] = {}
        print("🎭 [ORCHESTRATOR] Custom tools registry initialized")
        
        # Initialize LLM client
        self.llm_client = self._initialize_llm_client()
        print("🎭 [ORCHESTRATOR] LLM client initialized")
        
        # Tool cache for performance
        self.tool_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
        print("🎭 [ORCHESTRATOR] Tool cache initialized")
        
        print("🎭 [ORCHESTRATOR] ToolOrchestrator initialization complete!")
        logger.info("ToolOrchestrator initialized")
    
    def _register_custom_tools(self) -> None:
        """Register built-in custom tools."""
        print("🎭 [ORCHESTRATOR] Registering custom tools...")
        
        # Add any built-in custom tools here
        # For now, we'll leave this empty as tools are added dynamically
        
        print("🎭 [ORCHESTRATOR] Custom tools registration complete")
    
    def _initialize_llm_client(self):
        """Initialize the LLM client."""
        print("🎭 [ORCHESTRATOR] Creating LLM client...")
        
        try:
            from ..ai.llm_client import LLMClient
            client = LLMClient()
            print("🎭 [ORCHESTRATOR] LLM client created successfully")
            return client
        except Exception as e:
            print(f"❌ [ORCHESTRATOR] Error creating LLM client: {e}")
            logger.error(f"Error creating LLM client: {e}")
            # Return a mock client for fallback
            return self._create_mock_llm_client()
    
    def _create_mock_llm_client(self):
        """Create a mock LLM client for fallback."""
        print("🔄 [ORCHESTRATOR] Creating mock LLM client as fallback...")
        
        class MockLLMClient:
            def classify_intent(self, text):
                print("🤖 [MOCK_LLM] Classifying intent (mock)")
                return IntentType.CUSTOMER_SERVICE
            
            def analyze_sentiment(self, text):
                print("🤖 [MOCK_LLM] Analyzing sentiment (mock)")
                from ..data.data_types import SentimentType
                return SentimentType.NEUTRAL
            
            def generate_response(self, context):
                print("🤖 [MOCK_LLM] Generating response (mock)")
                return "Thank you for contacting Sierra Outfitters. How can I assist you today?"
        
        print("🔄 [ORCHESTRATOR] Mock LLM client created")
        return MockLLMClient()
    
    def execute_tools_for_intent(self, intent: IntentType, user_input: str) -> Dict[str, Any]:
        """Execute the appropriate tools for a given intent."""
        print(f"🎭 [ORCHESTRATOR] Executing tools for intent: {intent}")
        print(f"🎭 [ORCHESTRATOR] User input: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        start_time = time.time()
        results = {}
        
        try:
            # Get tools for this intent
            tools_to_execute = self.intent_tool_mapping.get(intent, [])
            print(f"🎭 [ORCHESTRATOR] Found {len(tools_to_execute)} tools to execute for intent {intent}")
            
            if not tools_to_execute:
                print(f"⚠️ [ORCHESTRATOR] No tools mapped for intent: {intent}")
                return {"message": "I understand your request but don't have specific tools for this yet."}
            
            # Execute each tool
            for tool_name in tools_to_execute:
                print(f"🎭 [ORCHESTRATOR] Executing tool: {tool_name}")
                
                try:
                    tool_result = self._execute_single_tool(tool_name, user_input)
                    results[tool_name] = tool_result
                    print(f"✅ [ORCHESTRATOR] Tool {tool_name} executed successfully")
                    
                except Exception as e:
                    print(f"❌ [ORCHESTRATOR] Error executing tool {tool_name}: {e}")
                    results[tool_name] = {
                        "error": f"Tool execution failed: {str(e)}",
                        "success": False
                    }
            
            execution_time = time.time() - start_time
            print(f"🎭 [ORCHESTRATOR] All tools executed in {execution_time:.2f} seconds")
            
            # Cache results
            cache_key = f"{intent.value}_{hash(user_input)}"
            self.tool_cache[cache_key] = {
                "results": results,
                "timestamp": time.time()
            }
            print(f"🎭 [ORCHESTRATOR] Results cached with key: {cache_key}")
            
            return results
            
        except Exception as e:
            print(f"❌ [ORCHESTRATOR] Error in tool execution: {e}")
            logger.error(f"Error executing tools for intent {intent}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _execute_single_tool(self, tool_name: str, user_input: str) -> Any:
        """Execute a single business tool."""
        print(f"🔧 [ORCHESTRATOR] Executing single tool: {tool_name}")
        
        start_time = time.time()
        
        try:
            # Check if tool exists in business tools
            if hasattr(self.business_tools, tool_name):
                print(f"🔧 [ORCHESTRATOR] Tool {tool_name} found in business tools")
                tool_method = getattr(self.business_tools, tool_name)
                
                # Execute the tool
                result = tool_method(user_input)
                execution_time = time.time() - start_time
                
                print(f"🔧 [ORCHESTRATOR] Tool {tool_name} completed in {execution_time:.3f} seconds")
                return result
            
            # Check if tool exists in custom tools
            elif tool_name in self.custom_tools:
                print(f"🔧 [ORCHESTRATOR] Tool {tool_name} found in custom tools")
                custom_tool = self.custom_tools[tool_name]
                result = custom_tool(user_input)
                execution_time = time.time() - start_time
                
                print(f"🔧 [ORCHESTRATOR] Custom tool {tool_name} completed in {execution_time:.3f} seconds")
                return result
            
            else:
                print(f"❌ [ORCHESTRATOR] Tool {tool_name} not found")
                raise ValueError(f"Tool '{tool_name}' not found")
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ [ORCHESTRATOR] Error executing tool {tool_name}: {e}")
            logger.error(f"Error executing tool {tool_name}: {e}")
            
            return {
                "error": f"Tool execution failed: {str(e)}",
                "success": False,
                "execution_time": execution_time
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        print("📋 [ORCHESTRATOR] Getting list of available tools...")
        
        business_tools = [method for method in dir(self.business_tools) 
                         if callable(getattr(self.business_tools, method)) 
                         and not method.startswith('_')]
        
        custom_tools = list(self.custom_tools.keys())
        
        all_tools = business_tools + custom_tools
        print(f"📋 [ORCHESTRATOR] Found {len(all_tools)} available tools ({len(business_tools)} business, {len(custom_tools)} custom)")
        
        return all_tools
    
    def add_custom_tool(self, tool_name: str, tool_function: Callable) -> bool:
        """Add a custom tool to the orchestrator."""
        print(f"➕ [ORCHESTRATOR] Adding custom tool: {tool_name}")
        
        try:
            if tool_name in self.custom_tools:
                print(f"⚠️ [ORCHESTRATOR] Tool {tool_name} already exists, overwriting")
            
            self.custom_tools[tool_name] = tool_function
            print(f"✅ [ORCHESTRATOR] Custom tool {tool_name} added successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ [ORCHESTRATOR] Error adding custom tool {tool_name}: {e}")
            logger.error(f"Error adding custom tool {tool_name}: {e}")
            return False
    
    def remove_custom_tool(self, tool_name: str) -> bool:
        """Remove a custom tool from the orchestrator."""
        print(f"➖ [ORCHESTRATOR] Removing custom tool: {tool_name}")
        
        try:
            if tool_name in self.custom_tools:
                del self.custom_tools[tool_name]
                print(f"✅ [ORCHESTRATOR] Custom tool {tool_name} removed successfully")
                return True
            else:
                print(f"⚠️ [ORCHESTRATOR] Tool {tool_name} not found in custom tools")
                return False
                
        except Exception as e:
            print(f"❌ [ORCHESTRATOR] Error removing custom tool {tool_name}: {e}")
            logger.error(f"Error removing custom tool {tool_name}: {e}")
            return False
    
    def get_tool_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about tool execution."""
        print("📊 [ORCHESTRATOR] Getting tool execution statistics...")
        
        stats = {
            "total_tools": len(self.get_available_tools()),
            "business_tools": len([m for m in dir(self.business_tools) 
                                 if callable(getattr(self.business_tools, m)) 
                                 and not m.startswith('_')]),
            "custom_tools": len(self.custom_tools),
            "cached_results": len(self.tool_cache),
            "cache_ttl": self.cache_ttl
        }
        
        print(f"📊 [ORCHESTRATOR] Statistics: {stats}")
        return stats
    
    def clear_cache(self) -> None:
        """Clear the tool execution cache."""
        print("🧹 [ORCHESTRATOR] Clearing tool execution cache...")
        
        cache_size = len(self.tool_cache)
        self.tool_cache.clear()
        
        print(f"🧹 [ORCHESTRATOR] Cache cleared, removed {cache_size} entries")
        logger.info("Tool execution cache cleared")
    
    def get_cached_result(self, intent: IntentType, user_input: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        print(f"🔍 [ORCHESTRATOR] Checking cache for intent: {intent}")
        
        cache_key = f"{intent.value}_{hash(user_input)}"
        
        if cache_key in self.tool_cache:
            cached_data = self.tool_cache[cache_key]
            age = time.time() - cached_data["timestamp"]
            
            if age < self.cache_ttl:
                print(f"✅ [ORCHESTRATOR] Cache hit for key: {cache_key} (age: {age:.1f}s)")
                return cached_data["results"]
            else:
                print(f"⏰ [ORCHESTRATOR] Cache expired for key: {cache_key} (age: {age:.1f}s)")
                del self.tool_cache[cache_key]
        else:
            print(f"❌ [ORCHESTRATOR] Cache miss for key: {cache_key}")
        
        return None
