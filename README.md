# Sierra Agent - AI-Powered Customer Service Platform

A comprehensive AI customer service platform for Sierra Outfitters with real-time quality monitoring, detailed analytics, and intelligent business tool orchestration.

## 🚀 Features

- **Dual LLM Architecture**: 
  - 🧠 GPT-4o for complex thinking and strategic planning
  - ⚡ GPT-4o-mini for low latency operations and simple tasks
- **Strategic Planning Engine**: Multi-step execution plans instead of reactive intent-based responses
- **AI-Powered Conversations**: Intelligent customer interactions with planning capabilities
- **Intent Classification**: Automatic understanding of customer requests
- **Sentiment Analysis**: Real-time customer mood tracking
- **Quality Monitoring**: Continuous conversation quality assessment
- **Business Tools**: Comprehensive toolset for order management, product inquiries, and more
- **Analytics Dashboard**: Detailed performance metrics and insights
- **Modular Architecture**: Clean, maintainable codebase

## 🏗️ Architecture

```
sierra_agent/
├── ai/                    # LLM integration and AI components
├── core/                  # Core agent and conversation management
├── analytics/             # Quality scoring and conversation analytics
├── tools/                 # Business tools and orchestration
│   ├── planning_engine.py # Strategic planning engine
│   ├── plan_executor.py   # Plan execution and coordination
│   └── business_tools.py  # Business logic tools
├── data/                  # Data types and models
└── utils/                 # Branding and error handling
```

### Dual LLM Architecture

The system now uses two LLM clients for optimal performance:

- **🧠 Thinking LLM (GPT-4o)**: Used for complex reasoning, strategic planning, and multi-step problem solving
- **⚡ Low Latency LLM (GPT-4o-mini)**: Used for fast responses, simple classifications, and routine tasks

### Planning Mechanism

Instead of reactive intent-based execution, the system now:

1. **Analyzes** customer requests for complexity
2. **Generates** strategic execution plans with multiple steps
3. **Executes** plans with dependency management and error handling
4. **Optimizes** execution order and handles conditional logic

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd customer_service_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)

### Package Configuration

The system uses `pyproject.toml` for package management with:
- Clean dependency specification
- Development tools configuration
- Type checking with MyPy
- Code formatting with Black
- Testing with pytest

### LLM Configuration

The agent can be configured with different LLM models:

```python
from sierra_agent.core.agent import AgentConfig, SierraAgent

# Dual LLM setup (recommended)
config = AgentConfig(
    enable_dual_llm=True,
    thinking_model="gpt-4o",        # For complex planning
    low_latency_model="gpt-4o-mini" # For fast responses
)

# Single LLM setup
config = AgentConfig(
    enable_dual_llm=False,
    thinking_model="gpt-4o"  # Used for all operations
)

agent = SierraAgent(config)
```

## 💬 Usage

### Starting a Conversation

```bash
python main.py
```

### Available Commands

- `help` - Show available commands
- `stats` - Display conversation statistics
- `summary` - Show current conversation summary
- `reset` - Reset current conversation
- `quit` - Exit the application

### Example Interactions

```
👤 You: I need help finding hiking boots
🤖 Sierra Agent: I'd be happy to help you find the perfect hiking boots! 
    Let me search our inventory for you...

👤 You: Track my order #12345
🤖 Sierra Agent: I'll look up your order #12345 for you...
    Order Status: Shipped
    Estimated Delivery: 2024-01-15
    Tracking Number: TRK789456123
```

### Testing the New Features

To test the dual LLM setup and planning mechanism:

```bash
# Test dual LLM and planning
python test_dual_llm.py

# Run the main application
python main.py
```

The test script demonstrates:
- Dual LLM initialization and status
- Planning engine functionality
- Plan execution and statistics
- LLM mode switching (single vs. dual)
- Comprehensive agent statistics

## 🧠 Planning Engine

The new planning mechanism replaces reactive intent-based execution with strategic planning:

### Plan Types

- **Simple Linear Plans**: Basic tool execution sequences
- **Conditional Plans**: Plans with branching logic based on results
- **Complex Plans**: Multi-step plans with loops and optimization

### Plan Execution

- **Dependency Management**: Ensures steps execute in correct order
- **Error Handling**: Graceful failure and retry mechanisms
- **Progress Tracking**: Real-time execution status monitoring
- **Result Aggregation**: Combines outputs from multiple steps

### Example Plan

```python
# A plan for handling order status inquiries
plan = Plan(
    name="Order Status Inquiry",
    steps=[
        PlanStep("validate_order", "VALIDATION", "Validate order ID format"),
        PlanStep("get_status", "TOOL_EXECUTION", "Retrieve order status", 
                dependencies=["validate_order"]),
        PlanStep("get_shipping", "TOOL_EXECUTION", "Get shipping info", 
                dependencies=["get_status"])
    ]
)
```

## 🏪 Business Tools

The system includes comprehensive business tools:

### Order Management
- Order status tracking
- Shipping information
- Delivery estimates

### Product Services
- Product search and recommendations
- Availability checking
- Detailed product information

### Customer Service
- Company information
- Contact details
- Policy information

### Returns & Complaints
- Return policy details
- Complaint logging
- Escalation procedures

## 📊 Analytics & Quality

### Quality Metrics
- **Relevance Score**: Topic consistency and focus
- **Helpfulness Score**: Response quality and tool usage
- **Engagement Score**: Conversation flow and interaction
- **Resolution Score**: Conversation completion
- **Sentiment Trajectory**: Customer mood changes

### Performance Tracking
- Conversation duration and length
- Intent distribution analysis
- Tool effectiveness metrics
- Quality trend analysis

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🔍 Code Quality

### Type Checking
```bash
mypy src/
```

### Code Formatting
```bash
black src/
```

### Linting
```bash
flake8 src/
```

## 📁 Project Structure

```
customer_service_agent/
├── src/
│   └── sierra_agent/      # Main package
│       ├── ai/            # AI/LLM integration
│       ├── core/          # Core system components
│       ├── analytics/     # Quality and analytics
│       ├── tools/         # Business tools
│       ├── data/          # Data models
│       └── utils/         # Utilities
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
├── main.py               # Main entry point
├── pyproject.toml        # Package configuration
└── requirements.txt      # Dependencies
```

## 🚧 Development

### Adding New Business Tools

1. Extend the `BusinessTools` class in `src/sierra_agent/tools/business_tools.py`
2. Add tool mapping in `ToolOrchestrator.intent_tool_mapping`
3. Update tests and documentation

### Customizing Quality Metrics

Modify `QualityScorer` in `src/sierra_agent/analytics/quality_scorer.py`:
- Adjust metric weights
- Add new quality dimensions
- Customize scoring algorithms

### Extending Data Models

Add new data types in `src/sierra_agent/data/data_types.py`:
- Define new enums and dataclasses
- Add validation functions
- Update serialization methods

## 📈 Monitoring & Logging

The system provides comprehensive logging:
- Application-level logging
- Error tracking and reporting
- Performance metrics
- Quality assessment logs

## 🔒 Security

- API keys stored in environment variables
- Input sanitization and validation
- Error message sanitization
- Secure API communication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: dev@sierraoutfitters.com
- Phone: 1-800-SIERRA-1
- Website: www.sierraoutfitters.com

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - AI-powered customer service
  - Quality monitoring
  - Business tool integration
  - Analytics dashboard

---

**Built with ❤️ by the Sierra Outfitters Development Team**
