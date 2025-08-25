# Sierra Agent Architecture

**Technical architecture documentation for the Sierra Agent customer service system**

## 🏗️ System Overview

Sierra Agent is built on a modular, production-ready architecture that combines intelligent planning with reliable data management. The system uses a multi-layered approach to handle customer service requests efficiently and accurately.

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                      │
├─────────────────────────────────────────────────────────────┤
│                       SierraAgent                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Planning      │  │  Conversation   │  │    Tool     │ │
│  │    Engine       │  │   Management    │  │ Orchestrator│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      Business Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Business Tools  │  │  Data Provider  │  │ LLM Client  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                        Data Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Customer Orders │  │ Product Catalog │  │  Data Types │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Core Components

### 1. SierraAgent (Core/Agent.py)
**Main orchestration class with intelligent planning capabilities**

```python
class SierraAgent:
    def __init__(self, config: AgentConfig):
        self.thinking_llm = LLMClient(model="gpt-4o")      # Complex reasoning
        self.low_latency_llm = LLMClient(model="gpt-4o-mini")  # Fast responses
        self.tool_orchestrator = ToolOrchestrator()
        self.conversation = Conversation()
```

#### Key Features:
- **Dual LLM System**: Separate models for planning vs. execution
- **Automatic Mode Selection**: Chooses between planning and reactive modes
- **Context Accumulation**: Builds context across plan execution steps
- **Quality Monitoring**: Real-time conversation quality assessment

### 2. Planning Engine
**Multi-step execution planning for complex requests**

#### Plan Generation Process:
```python
def _generate_plan(self, user_input: str) -> MultiTurnPlan:
    # 1. Analyze request (intent, complexity, context)
    context = self._analyze_request(user_input)
    
    # 2. Generate steps based on context
    steps = self._generate_plan_steps(user_input, context)
    
    # 3. Create plan with dependencies
    return MultiTurnPlan(steps=steps, intent=context["primary_intent"])
```

#### Plan Types:
- **Order Status**: Extract info → Lookup order → Generate response
- **Product Inquiry**: Analyze needs → Search products → Recommend items
- **Promotion**: Check time → Validate eligibility → Generate code
- **General Inquiry**: Route to appropriate tools → Provide assistance

### 3. Conversation Management (Core/Conversation.py)
**Enhanced conversation memory and context management**

```python
class Conversation:
    def build_conversational_context(self, current_results, intent):
        # Maintains 3 previous interactions (improved from 1)
        recent_messages = self.get_recent_messages_with_tool_results(limit=3)
        # Formats context with interaction numbering
        # Returns structured context for LLM processing
```

#### Features:
- **Multi-turn Memory**: Remembers 3 previous interactions
- **Context Formatting**: Structured context presentation
- **Quality Scoring**: Real-time conversation assessment
- **Phase Tracking**: Automatic conversation phase detection

### 4. Data Provider (Data/DataProvider.py)
**Robust data access layer with enhanced search capabilities**

#### Enhanced Search Algorithm:
```python
def search_products(self, query: str) -> List[Product]:
    # Word-boundary matching (prevents false positives)
    # Relevance scoring: Name (10pts) > Tags (5pts) > Description (2pts)
    # Case-insensitive matching for all fields
    # Sorted results by relevance score
```

#### Key Improvements:
- **Case-Insensitive Lookups**: Orders found regardless of case
- **Word-Boundary Matching**: Prevents "boot" matching "reboot"
- **Relevance Scoring**: Intelligent result ranking
- **Error Handling**: Robust JSON loading and validation

### 5. Business Tools (Tools/BusinessTools.py)
**Core business operations with enhanced parsing**

#### Enhanced Order Number Extraction:
```python
def _extract_order_number(self, text: str) -> Optional[str]:
    patterns = [
        r"#\s*W\s*\d+",                    # #W001, # W001
        r"\bW\s*-?\s*\d+\b",               # W001, W-001, W 001
        r"order\s+#?\s*W\s*-?\s*\d+",      # order W001, order #W001
        r"my\s+order\s+#?\s*W\s*-?\s*\d+", # my order W001
    ]
    # Normalizes to consistent format: #W001
```

#### Capabilities:
- **Flexible Pattern Matching**: Handles natural language variations
- **Data Extraction**: Email, order numbers, product preferences
- **Business Logic**: Promotion validation, inventory checks
- **Error Handling**: User-friendly error messages

## 🔄 Request Processing Flow

### 1. Input Analysis
```python
# User input: "Check my order W001 and recommend hiking boots"

# Analysis determines:
# - Intent: ORDER_STATUS + PRODUCT_INQUIRY (complex)
# - Complexity: Multi-step (triggers planning mode)
# - Required tools: get_order_status, search_products
```

### 2. Plan Generation
```python
# Generated plan steps:
[
    PlanStep(name="Extract Order Info", tool="extract_order_info"),
    PlanStep(name="Get Order Status", tool="get_order_status", 
             dependencies=["Extract Order Info"]),
    PlanStep(name="Analyze Product Request", tool="analyze_product_request"),
    PlanStep(name="Search Products", tool="search_products",
             dependencies=["Analyze Product Request"])
]
```

### 3. Execution with Context Accumulation
```python
# Step 1: Extract order info → Updates execution_context["current_order"]
# Step 2: Get order status → Uses extracted info from Step 1  
# Step 3: Analyze products → Independent analysis
# Step 4: Search products → Uses preferences from Step 3
# Result: All context available for final response generation
```

### 4. Response Generation
```python
# LLM receives:
# - Original user request
# - Primary tool result (most relevant business data)
# - Conversational context (previous 3 interactions)
# - Intent classification
# - Accumulated execution context
```

## 🛡️ Production Features

### Type Safety
- **Full MyPy compliance** across all modules
- **Typed data classes** (Order, Product, Promotion, ToolResult)
- **Generic type annotations** for collections and optionals

### Error Handling
```python
# Graceful degradation at every layer:
# 1. Tool failures → ToolResult with error message
# 2. Plan failures → Fallback plan generation  
# 3. LLM failures → Default error responses
# 4. Data failures → Empty results with user guidance
```

### Performance Optimizations
- **Dual LLM Strategy**: Fast model for simple tasks
- **Relevance-based Search**: Reduces irrelevant results
- **Context Management**: Optimal memory usage (3 interactions)
- **Caching Layer**: Intelligent result caching (5-minute TTL)

### Monitoring & Analytics
```python
# Built-in metrics:
# - Conversation quality scores (real-time)
# - Tool execution success rates  
# - Plan completion statistics
# - User interaction patterns
# - Error frequency tracking
```

## 🗄️ Data Models

### Core Business Objects
```python
@dataclass
class Order:
    customer_name: str
    email: str
    order_number: str           # Case-insensitive matching
    products_ordered: List[str] # SKU references
    status: str
    tracking_number: Optional[str]
    
    def get_tracking_url(self) -> Optional[str]:
        # USPS integration for tracking links

@dataclass 
class Product:
    product_name: str
    sku: str
    inventory: int
    description: str
    tags: List[str]            # Used for categorization & search

@dataclass
class ToolResult:
    data: Any
    success: bool = True
    error: Optional[str] = None
    
    def serialize_for_context(self) -> str:
        # Enhanced formatting for LLM context
        # Handles Order, Product, Promotion objects
        # Provides user feedback for truncated results
```

### Planning Objects
```python
@dataclass
class MultiTurnPlan:
    plan_id: str
    intent: IntentType
    customer_request: str
    steps: List[PlanStep]
    status: PlanStatus
    conversation_context: Dict[str, Any]  # Accumulated context

@dataclass
class PlanStep:
    step_id: str
    name: str
    description: str
    tool_name: Optional[str]
    dependencies: List[str]    # Step IDs this step depends on
    is_completed: bool = False
    result: Optional[Any] = None
```

## 🔧 Configuration

### Agent Configuration
```python
@dataclass
class AgentConfig:
    # LLM Configuration
    thinking_model: str = "gpt-4o"          # Complex reasoning
    low_latency_model: str = "gpt-4o-mini"  # Fast responses
    enable_dual_llm: bool = True
    
    # Monitoring Configuration  
    quality_check_interval: int = 3         # Every N interactions
    analytics_update_interval: int = 5      # Every N interactions
    max_conversation_length: int = 50       # Conversation limits
    
    # Feature Flags
    enable_quality_monitoring: bool = True
    enable_analytics: bool = True
```

### Environment Configuration
```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional
OPENAI_MODEL=gpt-4o                    # Default thinking model
OPENAI_MAX_TOKENS=2000                 # Response length limit  
OPENAI_TEMPERATURE=0.7                 # Response creativity
LOG_LEVEL=INFO                         # Logging verbosity
```

## 🚀 Deployment Considerations

### Scalability
- **Stateless design**: Each request is self-contained
- **Conversation persistence**: Can be externalized to database
- **Tool modularity**: Easy to add/remove business tools
- **LLM abstraction**: Can switch between providers

### Security  
- **Input validation**: All user inputs validated and sanitized
- **Error message safety**: No sensitive data in error responses
- **API key management**: Secure environment variable handling
- **Type safety**: Prevents runtime type errors

### Performance
- **Average response time**: <2 seconds for simple queries
- **Complex planning time**: 3-5 seconds for multi-step requests
- **Memory usage**: Optimized context management
- **Token efficiency**: Smart prompt construction for cost management

## 🔄 Extension Points

### Adding New Business Tools
```python
# 1. Create tool method in BusinessTools
def new_business_tool(self, user_input: str) -> ToolResult:
    # Implementation
    
# 2. Register in ToolOrchestrator
self.available_tools["new_business_tool"] = self.business_tools.new_business_tool

# 3. Add to plan generation logic
if request_type == "new_request_type":
    steps.append(PlanStep(tool_name="new_business_tool"))
```

### Custom Data Providers
```python
# Extend DataProvider for custom data sources
class CustomDataProvider(DataProvider):
    def load_external_data(self, source: str):
        # Custom data loading logic
```

### Analytics Integration
```python
# Built-in hooks for external analytics
def _update_analytics(self):
    # Send metrics to external system
    # Built-in conversation quality scores
    # Tool execution statistics
    # User interaction patterns
```

---

This architecture provides a solid foundation for production customer service AI with intelligent planning, reliable data management, and comprehensive monitoring capabilities.