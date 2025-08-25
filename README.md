# Sierra Agent - AI-Powered Customer Service Agent

**AI-powered customer service agent with intelligent planning, reliable data retrieval, and robust conversation management**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Check](https://img.shields.io/badge/mypy-passing-brightgreen.svg)](https://mypy-lang.org/)
[![Code Quality](https://img.shields.io/badge/code%20quality-optimized-brightgreen.svg)](/)

## 🚀 Overview

Sierra Agent is a production-ready customer service AI agent built for **Sierra Outfitters**, featuring intelligent request planning, reliable data retrieval, and sophisticated conversation management. The system automatically handles complex multi-step customer requests while maintaining conversation context and ensuring data accuracy.

### ✨ Key Features

- **🧠 Intelligent Planning**: Automatically generates multi-step execution plans for complex requests
- **📊 Reliable Data Retrieval**: Robust search and lookup with enhanced accuracy and error handling
- **🔄 Conversation Memory**: Maintains context across multiple interactions for better continuity
- **⚡ Dual Response Modes**: Fast responses for simple queries, strategic planning for complex requests
- **🛡️ Production-Ready**: Type-safe code with comprehensive error handling and validation
- **📈 Real-time Analytics**: Built-in conversation quality monitoring and analytics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Sierra Agent                             │
├─────────────────────────────────────────────────────────────┤
│  🧠 Planning Engine    │  📊 Data Layer    │  💬 Conversation │
│  • Multi-step plans    │  • Order lookup    │  • Context mgmt  │
│  • Dependency mgmt     │  • Product search  │  • Quality score │
│  • Strategic execution │  • Promotions      │  • Analytics     │
└─────────────────────────────────────────────────────────────┘
```

### Core Business Capabilities

1. **Order Status & Tracking**: Case-insensitive order lookup with USPS tracking integration
2. **Product Search & Recommendations**: Intelligent product search with relevance ranking
3. **Early Risers Promotion**: Time-based promotional offers (8-10 AM PT, 10% discount)
4. **Customer Support**: Multi-turn conversations with comprehensive help

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd customer_service_agent

# Run setup script (creates virtual environment and installs dependencies)
./setup.sh

# Or manual setup:
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

```bash
# Copy configuration template
cp config.template .env

# Edit .env file with your settings
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
```

### Basic Usage

```bash
# Run the interactive agent
python main.py

# Example interactions:
# "Check order #W001 for john.doe@example.com"
# "I'm looking for hiking boots"
# "Any early morning promotions available?"
```

### Python API Usage

```python
from sierra_agent import SierraAgent, AgentConfig

# Initialize agent
config = AgentConfig(
    thinking_model="gpt-4o",
    low_latency_model="gpt-4o-mini",
    enable_dual_llm=True
)
agent = SierraAgent(config)

# Start conversation
session_id = agent.start_conversation()

# Process user input
response = agent.process_user_input("Check my order status for john@example.com order W001")
print(response)
```

## 📊 Recent Improvements (v2.1)

### 🔧 Critical Bug Fixes
- **Case-Insensitive Order Lookup**: Orders now found regardless of case (`#w001` = `#W001`)
- **Enhanced Product Search**: Word-boundary matching prevents false positives (`"boot"` won't match `"reboot"`)
- **Improved Context Memory**: Increased conversation memory from 1 to 3 interactions
- **Flexible Order Number Parsing**: Handles various formats (`"my order W001"`, `"Order #W-001"`, etc.)
- **Better Error Messages**: User-friendly, actionable error messages across all tools

### 🧹 Code Quality Improvements
- **126+ lines of dead code removed** (unused mock methods, deprecated functions)
- **Enhanced type safety** with full MyPy validation
- **Optimized search relevance** with scoring algorithm (Name > Tags > Description)
- **Improved result formatting** with user feedback when results are truncated
- **Streamlined imports** and eliminated unused dependencies

## 🏢 Business Features

### Order Management
```python
# Supports flexible order number formats:
"Check order W001"           # ✅ Works
"Track #W001"               # ✅ Works  
"My order number is W-001"  # ✅ Works
"Order status for w001"     # ✅ Works (case-insensitive)
```

### Product Search
```python
# Intelligent search with relevance ranking:
agent.process_user_input("hiking boots")
# Returns boots specifically, not words containing "boot"
# Results ranked: exact name matches > tag matches > description matches
```

### Early Risers Promotion
```python
# Time-based promotion (8:00-10:00 AM Pacific Time)
agent.process_user_input("any morning discounts?")
# Automatically generates unique discount code if within time window
```

## 🔧 Data Management

### Data Files
- `data/CustomerOrders.json` - Customer order data with tracking info
- `data/ProductCatalog.json` - Product inventory with descriptions and tags

### Data Provider Features
- **Robust JSON loading** with error handling
- **Type-safe data models** (Order, Product, Promotion objects)
- **Optimized search algorithms** with word-boundary matching
- **USPS tracking integration** with automatic URL generation

## 🧠 Planning System

### Automatic Plan Generation
The agent automatically creates execution plans for complex requests:

```python
# Complex request example:
"I need to check my order W001 and also want recommendations for hiking gear"

# Automatically generates plan:
# 1. Extract customer information
# 2. Look up order status  
# 3. Analyze product preferences
# 4. Search for hiking products
# 5. Generate comprehensive response
```

### Planning vs Reactive Mode
- **Simple queries**: Direct tool execution (fast)
- **Complex queries**: Multi-step planning (comprehensive)
- **Automatic detection**: Based on request complexity and content

## 💬 Conversation Management

### Enhanced Memory
- **Context preservation**: Maintains 3 previous interactions
- **Quality scoring**: Real-time conversation quality assessment
- **Analytics**: Detailed conversation insights and performance metrics
- **Phase tracking**: Automatic conversation phase detection (greeting, exploration, resolution)

### Conversation Flow
```python
# Multi-turn conversation example:
Turn 1: "Check my order" 
        → "I need your email and order number"
Turn 2: "john@example.com, order W001"
        → "Your order is shipped, tracking: TRK123456789"
Turn 3: "When will it arrive?"
        → "Based on tracking, expected delivery is tomorrow"
        # ✅ Remembers order from previous turns
```

## 🛡️ Production Features

### Error Handling
- **Graceful degradation**: Fallback responses when tools fail
- **User-friendly errors**: Clear, actionable error messages
- **Input validation**: Robust parsing with multiple format support
- **Type safety**: Full MyPy compliance for reliability

### Performance
- **Dual LLM system**: Fast model for simple tasks, advanced model for complex reasoning
- **Optimized search**: Efficient product search with relevance scoring
- **Result caching**: Intelligent caching for frequently accessed data
- **Memory management**: Proper conversation memory limits

### Monitoring
- **Quality metrics**: Real-time conversation quality scoring
- **Usage analytics**: Detailed insights into agent performance
- **Error tracking**: Comprehensive error logging and reporting

## 🔧 Development

### Code Quality
```bash
# Type checking
python -m mypy src/sierra_agent --ignore-missing-imports

# Code formatting
python -m ruff format src/

# Linting
python -m ruff check src/

# Testing
python -m pytest tests/
```

### Architecture Components

#### Core Classes
- **SierraAgent**: Main agent class with dual LLM support
- **Conversation**: Enhanced conversation management with memory
- **DataProvider**: Robust data access layer with error handling
- **ToolOrchestrator**: Tool coordination and execution management

#### Data Types
- **Order**: Customer order with tracking integration
- **Product**: Product catalog item with search optimization
- **Promotion**: Time-based promotional offers
- **ToolResult**: Standardized tool execution results

## 📈 Analytics & Monitoring

### Built-in Analytics
- **Conversation quality scoring**: Real-time quality assessment
- **Tool execution metrics**: Success rates and performance data
- **User interaction patterns**: Conversation flow analysis
- **Error tracking**: Comprehensive error monitoring

### Configuration Options
```python
config = AgentConfig(
    quality_check_interval=3,      # Quality checks every N interactions
    analytics_update_interval=5,   # Analytics updates every N interactions
    max_conversation_length=50,    # Maximum conversation length
    enable_quality_monitoring=True,
    enable_analytics=True
)
```

## 🤝 Contributing

1. **Code Standards**: All code must pass MyPy type checking
2. **Testing**: New features require comprehensive tests
3. **Documentation**: Update README for significant changes
4. **Performance**: Optimize for production use cases

## 📜 License

MIT License - see LICENSE file for details.

## 🚀 What's Next

### Planned Improvements
- **Enhanced search algorithms**: Semantic search capabilities
- **Advanced analytics**: Machine learning insights
- **Multi-language support**: International customer service
- **API endpoints**: REST API for external integrations

---

**Sierra Agent v2.1** - Production-ready AI customer service with intelligent planning and reliable data management.