# Sierra Agent - AI-Powered Customer Service Agent

**AI-powered customer service agent with intelligent planning and strategic execution**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)](https://github.com/sierraoutfitters/sierra-agent)
[![Type Check](https://img.shields.io/badge/mypy-passing-brightgreen.svg)](https://mypy-lang.org/)

## 🚀 What's New: Planning Architecture!

The Sierra Agent has been **completely transformed** from a reactive tool execution system to an **intelligent, planning-based architecture** that automatically chooses between strategic planning and fast reactive responses.

### ✨ Key Features
- **🧠 Intelligent Planning**: Complex requests automatically use multi-step execution plans
- **⚡ Smart Reactive Mode**: Simple requests get fast responses without planning overhead
- **📊 Business Rules Engine**: Automated decisions based on urgency, sentiment, and intent
- **🔄 Dual LLM System**: Separate models for thinking (planning) and fast responses
- **📈 Quality Monitoring**: Real-time conversation quality assessment
- **🔍 Comprehensive Analytics**: Detailed insights into agent performance

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Sierra Agent v2.0                        │
├─────────────────────────────────────────────────────────────┤
│  🧠 Planning Mode    │  ⚡ Reactive Mode                   │
│  • Multi-step plans  │  • Fast responses                   │
│  • Business rules    │  • Simple tool execution            │
│  • Strategic logic   │  • Low latency                      │
└─────────────────────────────────────────────────────────────┘
```

### 🎯 How It Works
1. **Input Analysis**: Analyzes length, intent, and sentiment
2. **Smart Decision**: Automatically chooses planning vs reactive mode
3. **Execution**: Either creates/executes plans or runs tools directly
4. **Response**: Generates appropriate response based on execution results

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation
```bash
# Clone the repository
git clone https://github.com/sierraoutfitters/sierra-agent.git
cd sierra-agent

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage
```python
from sierra_agent import PlanningSierraAgent

# Initialize the planning agent
agent = PlanningSierraAgent()

# Start a conversation
session_id = agent.start_conversation()

# Process user input (automatically chooses planning or reactive mode)
response = agent.process_user_input("I need help with a complex order issue...")

# Get comprehensive statistics
stats = agent.get_agent_statistics()
```

### Command Line Interface
```bash
# Run the interactive agent
python main.py

# Available commands:
#   help     - Show available commands
#   stats    - Display conversation statistics
#   planning - Show planning system status
#   summary  - Show conversation summary
#   reset    - Reset current conversation
#   quit     - Exit the application
```

## 🧪 Testing & Demo

### Run Tests
```bash
# All tests
python3 -m pytest tests/ -v

# Planning system tests
python3 -m pytest tests/test_planning_agent.py -v

# With coverage
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Type Checking
```bash
# Check types with mypy
python3 -m mypy src/sierra_agent/ --show-error-codes
```

### Demo Script
```bash
# See the planning system in action
python3 test_planning_demo.py
```

## 📊 Planning vs Reactive Examples

### 🧠 Planning Mode (Complex Requests)
**Input**: *"I have a complaint about my recent purchase that includes damaged items, incorrect sizing, delayed delivery, and poor customer service experience that needs to be escalated to management"*

**System Response**: 
- ✅ **Planning triggered** (length: 156 chars > 50 threshold)
- 🧠 **Multi-step plan created** (complaint resolution workflow)
- 📋 **Business rules applied** (negative sentiment + complaint intent)
- 🚀 **Strategic execution** with proper escalation

### ⚡ Reactive Mode (Simple Requests)
**Input**: *"Hi there!"*

**System Response**:
- ⚡ **Reactive mode** (length: 8 chars < 50 threshold)
- 🚀 **Fast response** generated immediately
- 🛠️ **Simple tool execution** if needed
- 💨 **Low latency** response

## 🔧 Configuration

### Planning Agent Configuration
```python
from sierra_agent import PlanningAgentConfig

config = PlanningAgentConfig(
    planning_threshold=50,        # Character threshold for planning
    enable_planning=True,         # Enable planning system
    thinking_model="gpt-4o",      # Model for complex reasoning
    low_latency_model="gpt-4o-mini",  # Model for fast responses
    enable_dual_llm=True,        # Use separate models
    quality_check_interval=3,     # Check quality every 3 interactions
    analytics_update_interval=5   # Update analytics every 5 interactions
)
```

### Business Rules
The system automatically applies business rules:
- **High urgency** requests → Planning mode
- **Complex intents** (complaints, detailed inquiries) → Planning mode
- **Negative sentiment** → Planning mode with escalation
- **Long inputs** (>50 chars) → Planning mode

## 📈 Monitoring & Analytics

### Real-time Statistics
```python
# Get comprehensive agent statistics
stats = agent.get_agent_statistics()

# Planning system status
planning_stats = stats['planning_stats']
execution_stats = stats['execution_stats']

# Conversation quality
quality_score = agent.conversation.quality_score
```

### Quality Metrics
- **Conversation quality scores** (0.0 - 1.0)
- **Planning vs reactive usage** statistics
- **Business rule trigger rates**
- **Plan execution success rates**
- **Response generation times**

## 🏗️ Project Structure

```
sierra-agent/
├── src/sierra_agent/
│   ├── core/
│   │   ├── planning_agent.py    # 🆕 Main planning agent
│   │   ├── agent.py            # Legacy reactive agent
│   │   └── conversation.py     # Conversation management
│   ├── tools/
│   │   ├── planning_engine.py  # 🆕 Plan generation
│   │   ├── plan_executor.py    # 🆕 Plan execution
│   │   └── tool_orchestrator.py # Tool management
│   ├── ai/
│   │   └── llm_client.py      # LLM integration
│   ├── analytics/
│   │   ├── quality_scorer.py   # Quality assessment
│   │   └── conversation_analytics.py # Analytics
│   └── data/
│       └── data_types.py      # Data models
├── tests/
│   └── test_planning_agent.py # 🆕 Planning system tests
├── main.py                    # 🆕 Updated CLI with planning
├── test_planning_demo.py     # 🆕 Planning system demo
└── PLANNING_ARCHITECTURE.md  # 🆕 Detailed architecture docs
```

## 🔮 What's Next

### Planned Enhancements
- **Dynamic plan adjustment** based on execution results
- **Learning from past plans** to improve future planning
- **Multi-agent coordination** for complex scenarios
- **Real-time plan optimization** based on conversation context

### Extensibility
The architecture is designed to be easily extensible:
- **Custom business rules** can be added dynamically
- **New planning strategies** can be implemented
- **Additional LLM models** can be integrated
- **Custom tool orchestration** can be added

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Development

### Code Quality with Ruff

This project uses [Ruff](https://github.com/astral-sh/ruff) for fast Python linting and formatting. Ruff is a modern, extremely fast Python linter and formatter written in Rust.

#### Quick Commands

```bash
# Check code quality (linting)
make lint

# Check formatting
make format

# Auto-fix linting issues
make fix

# Auto-format code
make format-fix

# Run both linting and formatting checks
make check

# Show all available commands
make help
```

#### Using Ruff Directly

```bash
# Lint the codebase
python3 -m ruff check src/ tests/

# Auto-fix issues
python3 -m ruff check --fix src/ tests/

# Check formatting
python3 -m ruff format --check src/ tests/

# Format code
python3 -m ruff format src/ tests/
```

#### Configuration

Ruff is configured in `pyproject.toml` with:
- Line length: 88 characters (same as Black)
- Target Python version: 3.8+
- Comprehensive rule set including style, import sorting, and best practices
- Auto-fix enabled for most rules

#### What Ruff Checks

- **Style**: PEP 8 compliance, line length, spacing
- **Import sorting**: Automatic import organization
- **Code quality**: Unused imports, variables, and functions
- **Best practices**: Error handling, logging, security
- **Performance**: Inefficient patterns and optimizations

### Running Tests

```bash
# Run tests with coverage
make test

# Generate HTML coverage report
make test-html
```

### Installation

```bash
# Install development dependencies
make install-dev
```

## 📚 Documentation

- **[Planning Architecture](PLANNING_ARCHITECTURE.md)** - Detailed planning system documentation
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Examples](examples/)** - Usage examples and tutorials
- **[Testing Guide](docs/TESTING.md)** - Testing and development guide

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the LLM capabilities
- **Pydantic** for robust data validation
- **Pytest** for comprehensive testing framework
- **Mypy** for static type checking

---

## 🎉 Get Started Today!

Transform your customer service with intelligent AI planning:

```bash
git clone https://github.com/sierraoutfitters/sierra-agent.git
cd sierra-agent
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
python main.py
```

**Experience the future of AI customer service with strategic planning and intelligent execution! 🚀**
