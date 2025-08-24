# 🧠 Sierra Agent Planning Architecture

## Overview

The Sierra Agent has been transformed from a reactive tool execution system to an **intelligent, planning-based architecture** that strategically executes customer service requests. This document explains the new planning system and how it works.

## 🏗️ Architecture Transformation

### Before: Reactive Architecture
- **Simple tool execution**: Tools were executed immediately based on intent
- **No strategic planning**: Each request was handled independently
- **Limited complexity handling**: Complex multi-step requests were difficult to manage

### After: Planning Architecture
- **Strategic execution planning**: Complex requests are broken down into multi-step plans
- **Intelligent decision making**: The system automatically chooses between planning and reactive modes
- **Business rule integration**: Automated decisions based on urgency, sentiment, and intent
- **Dual LLM system**: Separate models for thinking (planning) and fast responses

## 🔧 Core Components

### 1. PlanningSierraAgent
The main agent class that orchestrates the planning system:

```python
from sierra_agent import PlanningSierraAgent, PlanningAgentConfig

# Configure the planning agent
config = PlanningAgentConfig(
    planning_threshold=50,  # Character threshold to trigger planning
    enable_planning=True,
    thinking_model="gpt-4o",      # For complex reasoning
    low_latency_model="gpt-4o-mini"  # For fast responses
)

agent = PlanningSierraAgent(config)
```

### 2. Planning Engine
Generates execution plans for complex requests:

```python
# The planning engine automatically creates multi-step execution plans
plan = agent.planning_engine.generate_plan(planning_request)
```

### 3. Plan Executor
Executes the generated plans step by step:

```python
# Plans are executed with proper error handling and fallbacks
execution_result = agent.plan_executor.execute_plan(plan, context)
```

### 4. Business Rules Engine
Automated decision making based on business logic:

```python
# Business rules automatically trigger planning for:
# - High urgency requests
# - Complex intents (complaints, product inquiries)
# - Negative sentiment
# - Long input (>50 characters by default)
```

## 🎯 How It Works

### Decision Flow
1. **Input Analysis**: User input is analyzed for length, intent, and sentiment
2. **Planning Decision**: System automatically decides whether to use planning or reactive mode
3. **Plan Generation**: If planning is needed, a multi-step execution plan is created
4. **Plan Execution**: Plan is executed step by step with error handling
5. **Response Generation**: Final response is generated based on execution results

### Planning Triggers
The system automatically uses planning when:

- **Input length** exceeds the threshold (default: 50 characters)
- **Business rules** are triggered (urgency, intent, sentiment)
- **Complex intents** are detected (complaints, detailed product inquiries)

### Example Decision Logic
```python
def _should_use_planning(self, user_input, intent, sentiment):
    # Check input length
    if len(user_input) > self.config.planning_threshold:
        return True
    
    # Check business rules
    for rule in self.business_rules:
        if self._evaluate_business_rule(rule, user_input, intent, sentiment):
            return True
    
    # Check intent complexity
    complex_intents = [IntentType.COMPLAINT, IntentType.PRODUCT_INQUIRY]
    if intent in complex_intents:
        return True
    
    return False
```

## 📊 Business Rules

### Default Business Rules
1. **Urgent Order Handling**
   - Conditions: `urgency: "high"`, `intent: "ORDER_STATUS"`
   - Actions: `["escalate_planning", "use_complex_strategy"]`

2. **Complex Product Inquiry**
   - Conditions: `intent: "PRODUCT_INQUIRY"`, `input_length: ">100"`
   - Actions: `["use_planning", "product_recommendation_plan"]`

3. **Complaint Escalation**
   - Conditions: `intent: "COMPLAINT"`, `sentiment: "NEGATIVE"`
   - Actions: `["use_planning", "complaint_resolution_plan"]`

### Custom Business Rules
You can add custom business rules by extending the `_initialize_business_rules` method:

```python
def _initialize_business_rules(self):
    rules = [
        # ... existing rules ...
        BusinessRule(
            rule_id="custom_rule",
            rule_name="Custom Business Logic",
            description="Handle specific business scenarios",
            conditions={"intent": "CUSTOM_INTENT", "urgency": "high"},
            actions=["use_planning", "custom_plan"],
            priority=1
        )
    ]
    return rules
```

## 🚀 Usage Examples

### Basic Usage
```python
from sierra_agent import PlanningSierraAgent

# Initialize the agent
agent = PlanningSierraAgent()

# Start a conversation
session_id = agent.start_conversation()

# Process user input (automatically chooses planning or reactive mode)
response = agent.process_user_input("I need help with a complex order issue...")

# Get conversation summary
summary = agent.get_conversation_summary()

# End conversation
agent.end_conversation()
```

### Advanced Configuration
```python
from sierra_agent import PlanningAgentConfig

# Custom configuration
config = PlanningAgentConfig(
    planning_threshold=100,        # Higher threshold
    quality_check_interval=5,      # Check quality every 5 interactions
    analytics_update_interval=10,  # Update analytics every 10 interactions
    enable_dual_llm=True,         # Use separate models for thinking and fast responses
    thinking_model="gpt-4o",      # Complex reasoning model
    low_latency_model="gpt-4o-mini"  # Fast response model
)

agent = PlanningSierraAgent(config)
```

### Monitoring and Analytics
```python
# Get comprehensive statistics
stats = agent.get_agent_statistics()

# Check planning system status
planning_stats = stats['planning_stats']
execution_stats = stats['execution_stats']

# Monitor conversation quality
quality_score = agent.conversation.quality_score
```

## 🧪 Testing

### Running Tests
```bash
# Run all planning agent tests
python3 -m pytest tests/test_planning_agent.py -v

# Run specific test categories
python3 -m pytest tests/test_planning_agent.py::TestPlanningAgentConfig -v
python3 -m pytest tests/test_planning_agent.py::TestPlanningSierraAgent -v
```

### Test Coverage
The test suite covers:
- ✅ Configuration management
- ✅ Business rule evaluation
- ✅ Planning decision logic
- ✅ Urgency level determination
- ✅ Conversation management
- ✅ Integration testing

### Demo Script
Run the planning system demo:
```bash
python3 test_planning_demo.py
```

## 🔍 Monitoring and Debugging

### Logging
The system provides detailed logging for each component:
- `🧠 [PLANNING_AGENT]` - Main planning logic
- `🔍 [PLANNING_AGENT]` - Business rule evaluation
- `🚀 [PLANNING_AGENT]` - Plan execution
- `⚡ [PLANNING_AGENT]` - Reactive mode execution

### Debug Information
Enable debug output to see:
- Business rule evaluation details
- Planning decision logic
- Plan execution steps
- Fallback mechanisms

## 🚨 Error Handling

### Graceful Degradation
- **Planning failures** automatically fall back to reactive mode
- **LLM errors** are caught and handled gracefully
- **Tool execution errors** don't crash the system

### Fallback Strategies
1. **Primary**: Planning-based execution
2. **Fallback**: Reactive tool execution
3. **Emergency**: Default response generation

## 🔮 Future Enhancements

### Planned Features
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

## 📚 API Reference

### PlanningSierraAgent Methods
- `start_conversation()` - Start new conversation session
- `process_user_input(input)` - Process user input with planning
- `get_conversation_summary()` - Get conversation statistics
- `get_agent_statistics()` - Get comprehensive agent stats
- `reset_conversation()` - Reset current conversation
- `end_conversation()` - End conversation and finalize analytics

### PlanningAgentConfig Options
- `planning_threshold` - Character threshold for planning (default: 50)
- `enable_planning` - Enable/disable planning system (default: True)
- `thinking_model` - LLM model for complex reasoning (default: "gpt-4o")
- `low_latency_model` - LLM model for fast responses (default: "gpt-4o-mini")
- `enable_dual_llm` - Use separate models (default: True)

## 🤝 Contributing

### Adding New Features
1. **Extend business rules** for new scenarios
2. **Add planning strategies** for complex workflows
3. **Implement new tools** for specific business needs
4. **Enhance monitoring** and analytics capabilities

### Testing Guidelines
1. **Unit tests** for all new functionality
2. **Integration tests** for planning workflows
3. **Type checking** with mypy
4. **Documentation** for new features

---

## 🎉 Summary

The Sierra Agent planning architecture represents a significant evolution from reactive to strategic execution. By automatically choosing between planning and reactive modes, the system provides:

- **Intelligent handling** of complex customer requests
- **Automatic escalation** based on business rules
- **Strategic execution** of multi-step workflows
- **Graceful fallbacks** when planning fails
- **Comprehensive monitoring** and analytics

This architecture makes the Sierra Agent more intelligent, reliable, and capable of handling complex customer service scenarios while maintaining fast response times for simple requests.
