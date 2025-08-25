# Development Guide

**Quick reference for Sierra Agent development and maintenance**

## 🚀 Quick Setup

```bash
# Clone and setup
git clone <repository-url>
cd customer_service_agent
./setup.sh

# Activate environment  
source .venv/bin/activate

# Configure
cp config.template .env
# Edit .env with your OpenAI API key
```

## 🔧 Development Commands

```bash
# Type checking (required to pass)
python -m mypy src/sierra_agent --ignore-missing-imports

# Code formatting
python -m ruff format src/

# Linting  
python -m ruff check src/

# Run tests
python -m pytest tests/

# Run agent
python main.py
```

## 📁 Project Structure

```
├── src/sierra_agent/          # Main source code
│   ├── core/                  # Core agent & conversation logic
│   ├── ai/                    # LLM client integration
│   ├── data/                  # Data models & provider
│   ├── tools/                 # Business tools & orchestration
│   └── utils/                 # Utilities (branding, errors)
├── data/                      # JSON data files
│   ├── CustomerOrders.json    # Order data
│   └── ProductCatalog.json    # Product data
├── tests/                     # Test files
├── main.py                    # CLI interface
└── README.md                  # User documentation
```

## 🛠️ Adding Features

### New Business Tool
1. Add method to `BusinessTools` class
2. Register in `ToolOrchestrator.available_tools`
3. Add to plan generation logic in `SierraAgent`
4. Update tests

### New Data Type
1. Define in `data_types.py` with `@dataclass`
2. Add to `__all__` export list
3. Update serialization methods if needed
4. Add type validation

### New Planning Logic
1. Update `_analyze_request()` for new intent detection
2. Add steps in `_generate_plan_steps()`
3. Handle in `_execute_plan_step()`
4. Test with various input formats

## ✅ Code Standards

### Required Practices
- **Type hints**: All functions must have type annotations
- **MyPy compliance**: Code must pass `mypy` without errors
- **Error handling**: All external calls wrapped in try/except
- **Documentation**: Public methods need docstrings
- **Testing**: New features require tests

### Code Style
- Use `dataclass` for data structures
- Prefer `Optional[Type]` over `Type | None`
- Use descriptive variable names
- Keep functions under 50 lines when possible
- Add debug logging with consistent format

## 🐛 Debugging

### Common Issues
```bash
# API key not working
export OPENAI_API_KEY="your-key-here"

# Type errors
python -m mypy src/sierra_agent --ignore-missing-imports

# Module import errors
pip install -e .

# Data file not found
# Check data/ directory exists with JSON files
```

### Debug Logging
```python
# Enable debug logging in development
logging.basicConfig(level=logging.DEBUG)

# Agent includes extensive debug output:
# 🧠 [PLANNING] - Plan generation
# 🔧 [EXECUTION] - Step execution  
# 📊 [DATA_PROVIDER] - Data operations
# 💬 [CONVERSATION] - Conversation management
```

## 📊 Performance Monitoring

### Key Metrics to Track
- **Response time**: Target <2s for simple, <5s for complex
- **Plan success rate**: Should be >95%
- **Tool execution success**: Should be >98%
- **Conversation quality**: Target score >0.8

### Optimization Tips
- Use `low_latency_model` for simple responses
- Cache frequently accessed data
- Limit conversation context to 3 interactions
- Batch database operations when possible

## 🧪 Testing Strategy

### Test Categories
```bash
# Unit tests - individual components
pytest tests/test_data_provider.py

# Integration tests - component interaction  
pytest tests/test_agent_integration.py

# End-to-end tests - full workflows
pytest tests/test_conversation_flows.py
```

### Test Data
- Use sample data in `tests/fixtures/`
- Mock external API calls
- Test both success and failure scenarios
- Verify error message quality

## 🚢 Deployment

### Environment Setup
```bash
# Production environment variables
OPENAI_API_KEY=prod_key_here
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
ANALYTICS_ENABLED=true
```

### Health Checks
```python
# Basic health check
agent = SierraAgent()
status = agent.get_llm_status()
# Verify both LLMs are available

# Data integrity check  
data_provider = DataProvider()
assert len(data_provider.customer_orders) > 0
assert len(data_provider.product_catalog) > 0
```

### Monitoring
- Track conversation quality scores
- Monitor API usage and costs
- Watch for tool execution failures
- Log user interaction patterns

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Review conversation analytics
- **Monthly**: Update dependencies (`pip install --upgrade -r requirements.txt`)
- **Quarterly**: Review and optimize LLM prompts
- **As needed**: Update product catalog and customer data

### Data Updates
```python
# Adding new products to catalog
new_product = {
    "ProductName": "New Hiking Boots",
    "SKU": "BOOT123",
    "Inventory": 50,
    "Description": "Waterproof hiking boots",
    "Tags": ["hiking", "boots", "waterproof"]
}
# Add to data/ProductCatalog.json
```

### Performance Optimization
- Monitor token usage for cost optimization
- Review and consolidate similar business tools
- Optimize search algorithms based on usage patterns
- Cache frequently requested data

---

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).
For user documentation, see [README.md](README.md).