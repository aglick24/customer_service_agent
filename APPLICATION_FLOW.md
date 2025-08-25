# Sierra Outfitters Agent - Complete Application Flow Documentation

## Table of Contents
1. [Overview](#overview)
2. [Application Entry Point](#application-entry-point)
3. [Core Architecture](#core-architecture)
4. [Data Flow Through the System](#data-flow-through-the-system)
5. [Context Construction & Management](#context-construction--management)
6. [Planning & Execution Engine](#planning--execution-engine)
7. [Key Architectural Decisions](#key-architectural-decisions)
8. [Component Deep Dive](#component-deep-dive)
9. [Request Processing Examples](#request-processing-examples)

## Overview

The Sierra Outfitters Agent is a sophisticated AI-powered customer service system designed with a layered architecture that processes user requests through intelligent planning, tool orchestration, and context-aware response generation. The system uses a dual-LLM approach with unified context management for optimal performance.

### Core Features
- **Order Status & Tracking**: Email + order number validation and status retrieval
- **Product Search & Recommendations**: Intelligent product discovery with scoring
- **Early Risers Promotion**: Time-based promotional code generation
- **Multi-turn Conversation Management**: Contextual conversation with data persistence
- **Intelligent Planning**: Dynamic request analysis and execution strategy

## Application Entry Point

### main.py:1-204
The application starts in `main.py`, which serves as the user interface and orchestration layer.

**Key Functions:**
- **Environment validation** (lines 109-114): Ensures OpenAI API key is present
- **Agent initialization** (lines 117-124): Creates SierraAgent instance
- **Conversation management** (lines 126-177): Handles user interaction loop
- **Command processing** (lines 138-164): Processes special commands (help, stats, reset, etc.)
- **Response routing** (lines 167-169): Routes user input to agent processing

**Architectural Decision**: The main loop is kept minimal, delegating all business logic to the SierraAgent class. This separation allows for clean testing and modularity.

```python
# Core interaction pattern (main.py:167-169)
response = agent.process_user_input(user_input)
```

## Core Architecture

### System Components Overview

The system follows a clean layered architecture:

```
┌─────────────────┐
│    main.py      │ ← Entry point & UI
├─────────────────┤
│  SierraAgent    │ ← Core orchestration
├─────────────────┤
│ Planning Service│ ← Request analysis & step generation
│ LLM Service     │ ← Unified AI interface
│ Conversation    │ ← State & history management
├─────────────────┤
│ToolOrchestrator │ ← Tool execution coordination
│ BusinessTools   │ ← Business logic implementation
├─────────────────┤
│  DataProvider   │ ← Data access layer
│   Data Types    │ ← Business objects
└─────────────────┘
```

## Data Flow Through the System

### 1. Request Reception (main.py → SierraAgent)
```
User Input → main.py:168 → SierraAgent.process_user_input()
```

### 2. Plan Generation (SierraAgent → PlanningService)
**Location**: `src/sierra_agent/core/agent.py:107-110`

```python
def _generate_plan(self, user_input: str) -> MultiTurnPlan:
    conversation_data = {
        "available_data": self.conversation.get_available_data(),
        "conversation_phase": self.conversation.conversation_state.conversation_phase,
        "current_topic": self.conversation.conversation_state.current_topic,
        "session_id": self.session_id
    }
    return self.planning_service.generate_plan(user_input, session_id=self.session_id, available_data=available_data)
```

### 3. Plan Execution (SierraAgent → ToolOrchestrator)
**Location**: `src/sierra_agent/core/agent.py:202-282`

The execution follows dependency resolution:
1. **Dependency Resolution** (lines 212-213): Steps ordered by dependencies
2. **Context Accumulation** (lines 208-209): Progressive context building
3. **Tool Execution** (lines 216-247): Individual step execution
4. **Result Integration** (lines 226-238): Context updates with results

### 4. Response Generation (SierraAgent → LLMService)
**Location**: `src/sierra_agent/core/agent.py:450-481`

```python
def _generate_response_from_plan(self, plan: MultiTurnPlan, execution_results: Dict[str, Any]) -> str:
    # Collect successful ToolResult objects
    all_tool_results = [step_result["result"] for step_result in execution_results["steps"] 
                       if step_result["success"] and isinstance(step_result["result"], ToolResult)]
    
    # Use unified LLM service for response generation
    return self.llm_service.generate_customer_service_response(
        user_input=plan.customer_request,
        tool_results=all_tool_results,
        conversation_context=self.conversation,
        use_thinking_model=False  # Use fast model for responses
    )
```

## Context Construction & Management

### Context Architecture
The system employs a sophisticated context management system with three layers:

#### 1. Conversation-Level Context (Conversation class)
**Location**: `src/sierra_agent/core/conversation.py:99-400`

- **Message History**: Chronological conversation record
- **Available Data Tracking**: Business objects from tool results
- **Conversation State**: Phase, topic, urgency tracking
- **Context Storage**: Explicit context preservation

```python
def get_available_data(self) -> Dict[str, Any]:
    """Get all data available from previous tool results and context storage."""
    available = {}
    
    # Check context storage
    if hasattr(self, "context_storage") and self.context_storage:
        available.update(self.context_storage)
    
    # Extract from recent tool results
    for message in reversed(self.messages):
        if message.tool_results:
            for tool_result in message.tool_results:
                if tool_result.success and tool_result.data:
                    data_type = type(tool_result.data).__name__
                    if data_type == "Order" and "current_order" not in available:
                        available["current_order"] = tool_result.data
```

#### 2. Planning Context (ContextBuilder)
**Location**: `src/sierra_agent/ai/context_builder.py:86-273`

The ContextBuilder creates strongly-typed contexts for different LLM operations:

- **CustomerServiceContext**: Response generation context
- **PlanningContext**: Tool selection and step generation  
- **PlanUpdateContext**: Dynamic plan modification

**Key Innovation**: Minimal history preservation with identifier extraction:

```python
def _summarize_tool_result_with_identifiers(self, tool_result: ToolResult) -> tuple[str, Dict[str, str], str]:
    """Summarize tool result preserving all identifiers."""
    if isinstance(tool_result.data, Order):
        order = tool_result.data
        identifiers = {
            "order_number": order.order_number,
            "customer_email": order.email,
            "customer_name": order.customer_name,
            "tracking_number": order.tracking_number or "none",
            "product_skus": ", ".join(order.products_ordered)
        }
        summary = f"Found Order {order.order_number} for {order.customer_name} - Status: {order.status}"
        interaction_type = "order_lookup"
```

#### 3. Execution Context (Plan Execution)
**Location**: `src/sierra_agent/core/agent.py:208-238`

Progressive context accumulation during execution:

```python
# Accumulate context with step results for future steps
if isinstance(result, ToolResult):
    step_context_key = f"step_{step.step_id}_result"
    execution_context[step_context_key] = result
    
    # Add semantic keys based on result type
    if result.success and hasattr(result.data, "__class__"):
        data_type = result.data.__class__.__name__
        if data_type == "Order":
            execution_context["current_order"] = result.data
        elif data_type == "list" and len(result.data) > 0:
            if hasattr(result.data[0], "__class__") and result.data[0].__class__.__name__ == "Product":
                execution_context["found_products"] = result.data
```

## Planning & Execution Engine

### Planning Service Architecture
**Location**: `src/sierra_agent/core/planning_service.py:17-336`

#### Request Analysis (lines 74-99)
The system analyzes user input to determine request type and complexity:

```python
def _analyze_request(self, user_input: str) -> Dict[str, Any]:
    user_lower = user_input.lower()
    context: Dict[str, Any] = {"request_type": "general", "complexity": "simple"}
    
    # Detect order-related requests
    if any(keyword in user_lower for keyword in ["order", "track", "delivery", "shipping", "#w", "order number"]):
        context["request_type"] = "order_status"
    
    # Detect product-related requests  
    elif any(keyword in user_lower for keyword in ["product", "recommend", "looking for", "need", "buy", "search"]):
        context["request_type"] = "product_inquiry"
    
    # Detect complex multi-part requests
    if len(user_input.split()) > 20 or "and" in user_lower or "also" in user_lower:
        context["complexity"] = "complex"
```

#### Step Generation (lines 101-192)
Context-aware step generation with dependency management:

```python
def _generate_plan_steps(self, user_input: str, context: Dict[str, Any], available_data: Optional[Dict[str, Any]] = None) -> List[PlanStep]:
    steps = []
    request_type = context.get("request_type", "general")
    available_data = available_data or {}

    if request_type == "order_status":
        # Check if we already have order data
        if "current_order" in available_data:
            # User wants product details for existing order
            if any(word in user_input.lower() for word in ["products", "items", "details", "specific"]):
                product_step = PlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    name="Get Product Details",
                    description="Get detailed information for products in the order",
                    tool_name="get_product_details",
                    parameters={"user_input": user_input}
                )
                steps.append(product_step)
        else:
            # Need to get order data first
            extract_step = PlanStep(...)
            order_step = PlanStep(..., dependencies=[extract_step.step_id])
            steps.extend([extract_step, order_step])
```

### Tool Orchestration
**Location**: `src/sierra_agent/tools/tool_orchestrator.py:18-104`

The ToolOrchestrator provides a clean interface between planning and business logic:

```python
def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
    """Execute a specific tool by name with typed parameters."""
    if tool_name not in self.available_tools:
        available_tools = list(self.available_tools.keys())
        return ToolResult(
            success=False,
            error=f"Tool '{tool_name}' not available. Available tools: {available_tools}",
            data=None
        )
    
    tool_method = self.available_tools[tool_name]
    return tool_method(**kwargs)
```

## Key Architectural Decisions

### 1. Unified LLM Service
**Location**: `src/sierra_agent/ai/llm_service.py:21-257`

**Decision**: Single service class managing dual LLM clients
**Rationale**: 
- Centralized LLM management reduces complexity
- Dual model approach (thinking vs low-latency) optimizes cost and performance
- Unified context handling ensures consistency

```python
class LLMService:
    def __init__(self, thinking_model: str = "gpt-4o", low_latency_model: str = "gpt-4o-mini"):
        self.thinking_client = LLMClient(model_name=thinking_model, max_tokens=2000)
        self.low_latency_client = LLMClient(model_name=low_latency_model, max_tokens=1000)
```

### 2. Plan-Based Execution
**Decision**: All user requests processed through MultiTurnPlan execution
**Rationale**:
- Consistent execution model for simple and complex requests
- Dependency resolution enables multi-step workflows
- Plan modification allows dynamic adaptation

### 3. Progressive Context Accumulation
**Decision**: Context built incrementally during plan execution
**Rationale**:
- Later steps can use results from earlier steps
- Enables complex workflows like "get order → get product details"
- Maintains conversation continuity

### 4. Strongly-Typed Business Objects
**Location**: `src/sierra_agent/data/data_types.py:24-354`

**Decision**: Rich data classes (Order, Product, Promotion) with serialization methods
**Rationale**:
- Type safety and IDE support
- Consistent serialization for LLM context
- Business logic encapsulation (e.g., tracking URL generation)

### 5. ToolResult Standardization
**Decision**: All tool operations return ToolResult objects
**Rationale**:
- Uniform error handling
- Rich context serialization for LLMs
- Clear success/failure indication

### 6. Parameter Extraction Strategy
**Location**: `src/sierra_agent/core/agent.py:325-417`

**Decision**: Context-aware parameter extraction using conversation history
**Rationale**:
- Reduces user friction (don't re-ask for known information)
- Supports natural conversation flow
- Handles references like "that order" or "those products"

```python
def _extract_tool_parameters(self, tool_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if tool_name == "get_order_status":
        # First check if we already have order data available
        available_data = self.conversation.get_available_data()
        if "current_order" in available_data:
            order = available_data["current_order"]
            if hasattr(order, "email") and hasattr(order, "order_number"):
                return {"email": order.email, "order_number": order.order_number}
        
        # Extract from original request
        email = self.tool_orchestrator.business_tools._extract_email(original_request)
        order_number = self.tool_orchestrator.business_tools._extract_order_number(original_request)
        
        # Search recent conversation history if missing
        if not email or not order_number:
            all_recent_messages = self.conversation.messages[-10:]
            conversation_text = " ".join([msg.content for msg in all_recent_messages if msg.content])
            # Extract from conversation context...
```

## Component Deep Dive

### DataProvider
**Location**: `src/sierra_agent/data/data_provider.py:23-243`

The DataProvider serves as the data access layer with business logic:

- **JSON Data Loading**: CustomerOrders.json and ProductCatalog.json
- **Product Search with Scoring**: Weighted matching (name > tags > description)
- **Time-Based Promotions**: Early Risers availability (8-10 AM PT)
- **Order Matching**: Case-insensitive email + order number validation

### BusinessTools
**Location**: `src/sierra_agent/tools/business_tools.py:19-313`

Individual business operations with parameter validation:

- **Order Status**: Email/order number validation and lookup
- **Product Search**: Query processing with empty result handling
- **Product Details**: SKU-based detailed product information
- **Recommendations**: Category and preference-based matching
- **Early Risers**: Time validation and dynamic code generation

### Conversation Management
**Location**: `src/sierra_agent/core/conversation.py:99-401`

Sophisticated conversation state tracking:

- **Message Threading**: User/AI/System message chronology
- **Tool Result Association**: Business data linked to AI responses
- **Phase Detection**: Greeting → Exploration → Resolution → Closing
- **Context Extraction**: Available data aggregation from tool results

## Request Processing Examples

### Example 1: Order Status Request
**User Input**: "I need to check on my order #W002 for alex@example.com"

**Flow**:
1. **Plan Generation**: 
   - Request type: "order_status"
   - Steps: [extract_order_info, get_order_status]

2. **Execution**:
   - Extract: email="alex@example.com", order_number="#W002"
   - Get Order: Returns Order object with customer details

3. **Response**: LLM generates friendly response with order details

### Example 2: Multi-Step Product Inquiry
**User Input**: "What products are in my order?" (following order lookup)

**Flow**:
1. **Context Analysis**: Available data contains "current_order"
2. **Plan Generation**: Steps: [get_product_details] using order SKUs
3. **Parameter Extraction**: SKUs from current_order.products_ordered
4. **Execution**: BusinessTools.get_product_details() with order SKUs
5. **Response**: Rich product information with descriptions and categories

### Example 3: Context-Aware Search Enhancement
**User Input**: "Show me hiking boots" followed by "Something similar but cheaper"

**Flow**:
1. **First Request**: Standard product search for "hiking boots"
2. **Context Storage**: Product results stored in conversation
3. **Second Request**: 
   - Plan recognizes "similar" reference
   - Uses get_product_recommendations with hiking boot category
   - Filters for lower-priced alternatives

This documentation provides a comprehensive understanding of the Sierra Outfitters Agent architecture, data flow, and decision-making processes. The system's design enables sophisticated customer service interactions while maintaining clean separation of concerns and extensibility.