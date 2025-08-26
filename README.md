# Sierra Agent - AI-Powered Customer Service Agent

**Production-ready customer service AI with adaptive conversation planning and intelligent tool orchestration**

## Overview

Sierra Agent is a modern customer service AI agent built for Sierra Outfitters. It features an Adaptive Planning System that maintains single evolving conversation plans, intelligent tool orchestration, and natural language response generation powered by dual LLM architecture.

### Key Features

- **Adaptive Planning**: Single evolving conversation plans that adapt to new requests dynamically
- **Modular Tool System**: Extensible tool architecture with automatic discovery and registration
- **Context Accumulation**: Intelligent business data accumulation across conversation turns
- **Dual LLM Architecture**: Fast responses via gpt-4o-mini, complex reasoning with gpt-4o
- **Natural Responses**: LLM-generated responses with Sierra Outfitters brand personality
- **Production-Ready**: Full type safety, comprehensive error handling, and monitoring

## Architecture

The system is built around an Adaptive Planning System that maintains single evolving conversation plans. These plans adapt dynamically to new user requests while accumulating business context across conversation turns.

```
┌─────────────────────────────────────────────────────────────┐
│                       main.py                              │ ← CLI Interface
├─────────────────────────────────────────────────────────────┤
│                     SierraAgent                            │ ← Main Coordinator
├─────────────────────────────────────────────────────────────┤
│              AdaptivePlanningService                        │ ← Core Planning Logic
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  EvolvingPlan   │  │ ConversationCtx │                  │
│  │ • Single plan   │  │ • Context data  │   LLMService     │
│  │ • Adapts to new │  │ • Auto-update   │   • Dual models │
│  │   requests      │  │ • Smart params  │   • Natural gen │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│                  ToolOrchestrator                          │ ← Tool Management
│  ┌───────────────┐ ┌─────────────────┐ ┌───────────────┐    │
│  │  OrderTools   │ │  CatalogTools   │ │ BusinessTools │    │
│  │ • Order lookup│ │ • Product search│ │ • Promotions  │    │
│  │ • Tracking    │ │ • Recommendations│ │ • Company info│    │
│  └───────────────┘ └─────────────────┘ └───────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    DataProvider                             │ ← Data Access Layer
│                  JSON Data Files                           │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

**SierraAgent (core/agent.py)**
- Main coordinator that delegates all processing to AdaptivePlanningService
- Manages conversation sessions and message history
- Handles periodic quality checks and analytics
- Provides clean API for external integrations

**AdaptivePlanningService (core/adaptive_planning_service.py)**
- Core planning logic with LLM integration
- Manages single evolving plan per conversation session
- Handles context accumulation and smart parameter extraction
- Executes tools with context-aware parameters
- Generates natural language responses

**EvolvingPlan & ConversationContext (core/planning_types.py)**
- Single adaptive plan that evolves across conversation turns
- Accumulates business data (orders, products, preferences) automatically
- Smart parameter extraction using accumulated context
- Reduces "missing information" prompts through context reuse

**Tool System (tools/)**
- Modular architecture with BaseTool interface
- Automatic tool discovery and registration via ToolRegistry
- OrderTools: Order lookup and tracking
- CatalogTools: Product search, details, and recommendations
- BusinessTools: Promotions and company information

**LLMService (ai/llm_service.py)**
- Unified service with dual model architecture
- gpt-4o for complex reasoning and planning
- gpt-4o-mini for fast responses
- Context-aware prompt building
- Natural language response generation

## Control Flow

### Request Processing

1. **User Input Reception**
   ```
   User Input → main.py → SierraAgent.process_user_input()
   ```

2. **Adaptive Planning & Execution**
   ```
   SierraAgent → AdaptivePlanningService.process_user_input()
   ```

3. **Plan Management**
   ```
   AdaptivePlanningService:
   - Get/create EvolvingPlan for session
   - Update ConversationContext from user input
   - Determine actions using LLM + rule-based fallback
   - Execute actions with context-aware parameters
   - Generate natural language response
   ```

4. **Context-Aware Tool Execution**
   ```
   EvolvingPlan.execute_action():
   - Update context from user input
   - Extract parameters using accumulated context
   - Execute tool if sufficient parameters available
   - Update context with tool results
   ```

### Context Accumulation Example

```
Turn 1: "Check order W001 for john@example.com"
        → Context: {customer_email, order_number, current_order}
        
Turn 2: "What products are in my order?"
        → Uses context.current_order.products_ordered automatically
        
Turn 3: "Track my shipment"
        → Uses context.current_order.tracking_number automatically
```

### Conversation Flow

The system maintains one EvolvingPlan per conversation session that adapts to new requests:

```python
# Initial request
Turn 1: "Check my order W001"
       → Plan: Extract order info → Lookup order → Store context

# Follow-up leverages accumulated context  
Turn 2: "What products are in my order?"
       → Plan: Use stored order context → Get product details
       
# Further requests continue building context
Turn 3: "Recommend something similar"
       → Plan: Use order products as preferences → Get recommendations
```

## Business Capabilities

### Order Management
- Context-aware order lookup with USPS tracking integration
- Flexible order number parsing (W001, #W001, "order W001", etc.)
- Automatic context persistence across conversation turns

### Product Catalog
- Intelligent product search with relevance scoring
- Detailed product information retrieval
- Smart recommendations based on order history and preferences
- Context-aware product suggestions

### Early Risers Promotion
- Time-based promotional offers (8-10 AM Pacific Time, 10% discount)
- Automatic discount code generation
- Natural language promotion descriptions

### Conversational AI
- Natural language responses with Sierra Outfitters brand personality
- Context-aware conversations that remember previous interactions
- Smart parameter extraction to minimize user friction

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd customer_service_agent

# Run setup script
./setup.sh

# Or manual setup:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

```bash
# Copy configuration template
cp config.template .env

# Edit .env file with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### Basic Usage

```bash
# Run the interactive agent
python main.py

# Special commands:
# help     - Show available commands
# stats    - Display conversation statistics  
# planning - Show current planning system status
# reset    - Reset conversation
# quit     - Exit
```

### Python API Usage

```python
from sierra_agent import SierraAgent, AgentConfig

# Initialize agent
config = AgentConfig(
    thinking_model="gpt-4o",           # For complex reasoning
    low_latency_model="gpt-4o-mini",   # For fast responses
    enable_dual_llm=True,              # Enable dual LLM architecture
    enable_analytics=True,             # Enable conversation analytics
)
agent = SierraAgent(config)

# Start conversation session
session_id = agent.start_conversation()

# Process user input - context accumulates automatically
response = agent.process_user_input("Check order W001 for john@example.com")
follow_up = agent.process_user_input("What products are in my order?")

# Get conversation insights
stats = agent.get_conversation_summary()
```

## Project Structure

```
src/sierra_agent/
├── core/                          # Core agent & planning logic
│   ├── agent.py                   # Main SierraAgent coordinator
│   ├── adaptive_planning_service.py # Adaptive planning system
│   ├── planning_types.py          # EvolvingPlan & ConversationContext
│   └── conversation.py            # Message management
├── ai/                            # LLM integration
│   ├── llm_service.py             # Unified LLM service
│   ├── llm_client.py              # OpenAI client wrapper
│   ├── context_builder.py         # Context building for LLM calls
│   └── prompt_templates.py        # LLM prompt templates
├── tools/                         # Modular tool system
│   ├── base_tool.py               # BaseTool interface & registry
│   ├── tool_orchestrator.py       # Tool discovery & execution
│   ├── order_tools.py             # Order management tools
│   ├── catalog_tools.py           # Product catalog tools
│   └── business_tools.py          # General business tools
├── data/                          # Data access layer
│   ├── data_provider.py           # JSON data loading & search
│   └── data_types.py              # Business data models
└── utils/                         # Utilities
    └── branding.py                # Sierra Outfitters branding

data/                              # Business data
├── CustomerOrders.json            # Order data with tracking
└── ProductCatalog.json            # Product inventory
```

## Development

### Code Quality Tools

```bash
# Type checking (required to pass)
python -m mypy src/sierra_agent --ignore-missing-imports

# Code formatting
python -m ruff format src/

# Linting
python -m ruff check src/

# Testing
python -m pytest tests/ --cov=src
```

### Architecture Components

**Core Classes**
- **SierraAgent**: Simplified coordinator delegating to AdaptivePlanningService
- **AdaptivePlanningService**: Core planning logic with LLM integration
- **EvolvingPlan**: Single adaptive plan that evolves across conversation turns
- **ConversationContext**: Unified context system for business data accumulation
- **ToolOrchestrator**: Extensible tool system with automatic discovery

**Data Models**
- **Order**: Customer order with tracking integration
- **Product**: Product catalog item with search optimization  
- **ToolResult**: Standardized tool execution results
- **ExecutedStep**: Records of completed plan steps
- **BusinessData**: Union type for all business data objects

### Adding New Tools

```python
# 1. Create new tool class extending BaseTool
from sierra_agent.tools.base_tool import BaseTool

class MyNewTool(BaseTool):
    def get_name(self) -> str:
        return "my_new_tool"
    
    def get_description(self) -> str:
        return "Description for LLM planning"
    
    def execute(self, **params) -> ToolResult:
        # Implementation
        pass

# 2. Tools are automatically discovered via ToolRegistry
```

### Extending ConversationContext

```python
# Add new context fields in planning_types.py
@dataclass
class ConversationContext:
    # Existing fields...
    my_new_data: Optional[MyDataType] = None
    
    def update_from_result(self, result: ToolResult) -> None:
        # Add handling for new data types
        if isinstance(result.data, MyDataType):
            self.my_new_data = result.data
```

## Production Features

### Error Handling
- Graceful degradation with LLM fallbacks to template responses
- Context-aware error messages using accumulated conversation data
- Comprehensive parameter validation with user-friendly feedback
- Full MyPy compliance across all modules

### Performance Optimization
- Dual LLM architecture: gpt-4o-mini for fast responses, gpt-4o for complex reasoning
- Context-aware tool selection reduces unnecessary executions
- Smart parameter extraction minimizes "missing information" prompts
- Proper session management with plan cleanup

### Monitoring & Analytics
- Real-time conversation quality scoring
- Planning system metrics: active plans, success rates, tool usage
- LLM usage tracking: model selection, token usage, response quality
- Session analytics: conversation flow patterns, context effectiveness

### Configuration Options

```python
config = AgentConfig(
    # LLM Configuration
    thinking_model="gpt-4o",           # Complex reasoning model
    low_latency_model="gpt-4o-mini",   # Fast response model
    enable_dual_llm=True,              # Enable intelligent model selection
    
    # Monitoring Configuration
    quality_check_interval=3,          # Quality checks every N interactions
    analytics_update_interval=5,       # Analytics updates every N interactions
    max_conversation_length=50,        # Conversation length limits
    
    # Feature Flags
    enable_quality_monitoring=True,    # Enable quality scoring
    enable_analytics=True              # Enable detailed analytics
)
```

## Technical Benefits

### Architectural Simplification
- Single evolving plan instead of complex multi-step plan generation
- Context accumulation replaces complex context builders
- Direct tool execution with smart parameter inheritance
- Unified LLM service for consistent response generation

### Enhanced User Experience
- Faster responses with no upfront planning overhead
- Natural conversations without need to repeat information
- Context-aware interactions that reduce user friction
- Consistent brand personality across all responses

### Developer Benefits
- Easy extension through BaseTool interface implementation
- Clear separation between planning and business logic
- Full type safety with comprehensive MyPy validation
- Simple debugging with single execution paths

### Production Readiness
- Error resilience with graceful degradation at every layer
- Performance optimization through dual LLM strategy
- Built-in monitoring with quality scoring and analytics
- Memory efficiency with proper plan cleanup and context limits

---

**Sierra Agent** - Modern AI customer service with adaptive conversation planning and intelligent context management.