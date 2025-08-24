# 🧠 Multi-Turn Planning Architecture

## Overview

The Sierra Agent has been enhanced with **multi-step in-turn planning** capabilities that allow the agent to plan conversations across multiple turns while maintaining conversation flow and context. This represents a significant evolution from single-turn planning to strategic, multi-turn conversation management.

## 🚀 Key Features

### **Multi-Turn Planning**
- **Conversation Flow Management**: Plans span multiple conversation turns
- **Turn Dependencies**: Steps are organized by conversation turns with dependencies
- **Goal Tracking**: Each turn has specific goals and completion criteria
- **Auto-Advance**: Automatic progression between turns when possible

### **Conversation Patterns**
- **Information Gathering**: Collect information across multiple turns
- **Problem Solving**: Multi-step problem resolution workflows
- **Consultation**: Extended consultation and recommendation processes
- **Escalation**: Complex escalation workflows with multiple stakeholders

### **Intelligent Decision Making**
- **Automatic Mode Selection**: Chooses between single-turn and multi-turn planning
- **Context Preservation**: Maintains conversation context across turns
- **Dynamic Plan Adjustment**: Adapts plans based on conversation flow
- **Fallback Mechanisms**: Graceful degradation when planning fails

## 🏗️ Architecture Components

### 1. **Multi-Turn Planning Engine** (`MultiTurnPlanningEngine`)
Generates strategic execution plans for multi-turn conversations:

```python
from sierra_agent.tools.multi_turn_planning_engine import MultiTurnPlanningEngine

# Initialize the engine
engine = MultiTurnPlanningEngine(thinking_llm=llm_client)

# Generate a multi-turn plan
plan = engine.generate_multi_turn_plan(planning_request)
```

**Features:**
- **Planning Strategies**: Different approaches based on complexity
- **Plan Templates**: Pre-defined templates for common scenarios
- **Conversation Patterns**: Recognizable conversation flow patterns
- **LLM-Powered Generation**: Intelligent plan creation

### 2. **Multi-Turn Plan Executor** (`MultiTurnPlanExecutor`)
Executes plans incrementally across conversation turns:

```python
from sierra_agent.tools.multi_turn_plan_executor import MultiTurnPlanExecutor

# Initialize the executor
executor = MultiTurnPlanExecutor()

# Execute a specific turn
turn_result = executor.execute_turn(plan, turn_number, context)
```

**Features:**
- **Turn-by-Turn Execution**: Execute steps for specific conversation turns
- **Dependency Management**: Handle step dependencies within turns
- **Progress Tracking**: Monitor plan execution progress
- **Error Handling**: Comprehensive error handling and recovery

### 3. **Enhanced Planning Agent** (`PlanningSierraAgent`)
Integrates multi-turn planning with the existing agent architecture:

```python
from sierra_agent import PlanningSierraAgent

# Initialize the agent
agent = PlanningSierraAgent()

# Process user input (automatically chooses planning mode)
response = agent.process_user_input("Complex multi-step request...")

# Get multi-turn plan progress
progress = agent.get_multi_turn_plan_progress()
```

**Features:**
- **Automatic Mode Selection**: Choose between single-turn and multi-turn planning
- **Plan Continuation**: Continue plans across multiple interactions
- **Context Management**: Maintain conversation context and state
- **Progress Monitoring**: Track plan execution progress

## 📊 Data Models

### **MultiTurnPlan**
Represents a plan designed for multi-turn conversation execution:

```python
@dataclass
class MultiTurnPlan:
    plan_id: str
    name: str
    description: str
    customer_request: str
    steps: List[PlanStep]
    conversation_turns: int
    max_turns: int
    current_turn: int
    turn_dependencies: Dict[int, List[str]]  # turn -> step_ids
    turn_goals: Dict[int, str]  # turn -> goal description
    requires_user_input: List[int]  # turns that need user input
    auto_advance: bool  # whether to automatically advance
```

### **TurnExecutionResult**
Result of executing a single conversation turn:

```python
@dataclass
class TurnExecutionResult:
    turn_number: int
    success: bool
    completed_steps: List[str]
    failed_steps: List[str]
    user_input_required: bool
    next_turn_ready: bool
    turn_output: Dict[str, Any]
    conversation_state: Dict[str, Any]
    execution_time: float
```

### **ConversationState**
Enhanced conversation state with multi-turn planning information:

```python
@dataclass
class ConversationState:
    # ... existing fields ...
    active_plan_id: Optional[str]
    plan_execution_state: str  # NO_PLAN, PLANNING, EXECUTING, COMPLETED
    completed_plan_steps: List[str]
    pending_plan_steps: List[str]
    conversation_goals: List[str]
    current_goal: Optional[str]
    goal_progress: Dict[str, float]
```

## 🔄 How It Works

### **1. Input Analysis & Mode Selection**
```python
def _should_use_multi_turn_planning(self, user_input, intent, sentiment):
    # Check if we have an active multi-turn plan
    if self.active_multi_turn_plan:
        return True
    
    # Check for complex, multi-step requests
    if len(user_input) > 150:
        return True
    
    # Check for specific intent patterns
    if intent == IntentType.COMPLAINT and sentiment == SentimentType.NEGATIVE:
        return True
    
    return False
```

### **2. Plan Generation**
```python
def _start_new_multi_turn_plan(self, user_input, intent, sentiment):
    # Create planning request
    planning_request = PlanningRequest(
        customer_input=user_input,
        conversation_context=self.conversation.get_conversation_patterns(),
        available_tools=self.tool_orchestrator.get_available_tools(),
        business_rules=self.business_rules,
        urgency_level=self._determine_urgency_level(sentiment, intent),
    )
    
    # Generate multi-turn plan
    multi_turn_plan = self.multi_turn_planning_engine.generate_multi_turn_plan(planning_request)
    
    # Store the plan and execute first turn
    self.active_multi_turn_plan = multi_turn_plan
    return self._execute_multi_turn_turn(multi_turn_plan, 1, user_input, intent, sentiment)
```

### **3. Turn Execution**
```python
def _execute_multi_turn_turn(self, plan, turn_number, user_input, intent, sentiment):
    # Create execution context
    execution_context = ExecutionContext(
        plan_id=plan.plan_id,
        session_id=self.session_id,
        user_input=user_input,
        conversation_history=self.conversation.get_message_history(limit=5),
        global_variables={
            "intent": intent.value,
            "sentiment": sentiment.value,
            "urgency": self.conversation.conversation_state.urgency_level,
            "current_turn": turn_number,
            "total_turns": plan.conversation_turns,
        },
    )
    
    # Execute the turn
    turn_result = self.multi_turn_plan_executor.execute_turn(plan, turn_number, execution_context)
    
    # Update conversation state
    self.conversation.conversation_state.plan_execution_state = "EXECUTING"
    self.conversation.conversation_state.completed_plan_steps.extend(turn_result.completed_steps)
    
    return turn_result.turn_output
```

### **4. Plan Continuation**
```python
def _continue_multi_turn_plan(self, user_input, intent, sentiment):
    # Check if we can advance to the next turn
    if self.multi_turn_plan_executor.can_advance_to_next_turn(
        self.active_multi_turn_plan, self.current_turn
    ):
        self.current_turn += 1
    
    # Execute the current turn
    return self._execute_multi_turn_turn(
        self.active_multi_turn_plan, self.current_turn, user_input, intent, sentiment
    )
```

## 🎯 Usage Examples

### **Basic Multi-Turn Planning**
```python
from sierra_agent import PlanningSierraAgent

# Initialize the agent
agent = PlanningSierraAgent()

# Start a conversation
session_id = agent.start_conversation()

# Process a complex request (triggers multi-turn planning)
response = agent.process_user_input(
    "I have a complex complaint about my recent purchase that includes "
    "damaged items, incorrect sizing, delayed delivery, and poor customer "
    "service experience that needs to be escalated to management immediately"
)

# Check if multi-turn planning was triggered
if agent.active_multi_turn_plan:
    progress = agent.get_multi_turn_plan_progress()
    print(f"Multi-turn plan: {progress['current_turn']}/{progress['total_turns']} turns")
    print(f"Progress: {progress['progress_percentage']:.1f}%")

# Continue the conversation
follow_up_response = agent.process_user_input("Can you tell me what steps you're taking?")

# Get updated progress
progress = agent.get_multi_turn_plan_progress()
print(f"Updated progress: {progress['progress_percentage']:.1f}%")
```

### **Plan Management**
```python
# Get plan progress
progress = agent.get_multi_turn_plan_progress()
print(f"Plan: {progress['plan_id']}")
print(f"Status: {progress['status']}")
print(f"Completed turns: {progress['completed_turns']}")
print(f"Remaining turns: {progress['remaining_turns']}")

# Reset plan if needed
agent.reset_multi_turn_plan()

# Check if plan was reset
if not agent.active_multi_turn_plan:
    print("Plan reset successfully")
```

### **Advanced Configuration**
```python
from sierra_agent import PlanningAgentConfig

# Configure multi-turn planning behavior
config = PlanningAgentConfig(
    planning_threshold=50,        # Character threshold for planning
    enable_planning=True,         # Enable planning system
    thinking_model="gpt-4o",      # Model for complex reasoning
    low_latency_model="gpt-4o-mini",  # Model for fast responses
    enable_dual_llm=True,        # Use separate models
)

agent = PlanningSierraAgent(config)
```

## 📈 Monitoring & Analytics

### **Multi-Turn Planning Statistics**
```python
# Get comprehensive statistics
stats = agent.get_agent_statistics()

# Multi-turn planning status
multi_turn_stats = stats['multi_turn_planning']
print(f"Active Plan: {multi_turn_stats['active_plan']}")
print(f"Current Turn: {multi_turn_stats['current_turn']}")
print(f"Total Turns: {multi_turn_stats['total_turns']}")
print(f"Plan Status: {multi_turn_stats['plan_status']}")

# Multi-turn executor statistics
executor_stats = stats['multi_turn_executor']
print(f"Total Plans: {executor_stats['total_plans']}")
print(f"Total Turns: {executor_stats['total_turns']}")
print(f"Success Rate: {executor_stats['success_rate']:.1f}%")

# Multi-turn planning engine statistics
engine_stats = stats['multi_turn_planning_engine']
print(f"Planning Strategies: {engine_stats['strategies']}")
print(f"Plan Templates: {engine_stats['templates']}")
print(f"Conversation Patterns: {engine_stats['conversation_patterns']}")
```

### **Plan Progress Tracking**
```python
# Get detailed plan progress
progress = agent.get_multi_turn_plan_progress()

print(f"Plan Progress:")
print(f"  Current Turn: {progress['current_turn']}")
print(f"  Total Turns: {progress['total_turns']}")
print(f"  Progress: {progress['progress_percentage']:.1f}%")
print(f"  Completed Turns: {progress['completed_turns']}")
print(f"  Remaining Turns: {progress['remaining_turns']}")
print(f"  Status: {progress['status']}")

# Show turn results if available
if 'turn_results' in progress:
    for turn_result in progress['turn_results']:
        print(f"  Turn {turn_result['turn_number']}: {turn_result['success']}")
```

## 🔧 Configuration Options

### **Planning Thresholds**
- **Single-turn planning**: Input length > 50 characters
- **Multi-turn planning**: Input length > 150 characters or complex intents
- **Reactive mode**: Input length ≤ 50 characters

### **Turn Management**
- **Auto-advance**: Automatically progress between turns when possible
- **User input requirements**: Specify which turns require user input
- **Turn dependencies**: Define step dependencies within and across turns
- **Completion criteria**: Set criteria for turn completion

### **Business Rules**
```python
# Example business rule for multi-turn planning
BusinessRule(
    rule_id="complex_complaint_rule",
    rule_name="Complex Complaint Handling",
    description="Use multi-turn planning for complex complaints",
    conditions={
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "input_length": ">100"
    },
    actions=["use_multi_turn_planning", "escalate_planning"],
    priority=1
)
```

## 🚨 Error Handling & Recovery

### **Graceful Degradation**
- **Planning failures**: Automatically fall back to reactive mode
- **Turn execution errors**: Continue with remaining turns
- **LLM errors**: Use fallback planning strategies
- **Tool execution errors**: Handle gracefully with retry mechanisms

### **Plan Recovery**
```python
# Check if plan can continue after errors
if agent.active_multi_turn_plan:
    progress = agent.get_multi_turn_plan_progress()
    
    if progress['status'] == 'FAILED':
        # Plan failed, can reset and start over
        agent.reset_multi_turn_plan()
        print("Plan failed, reset for new attempt")
    
    elif progress['status'] == 'IN_PROGRESS':
        # Plan can continue
        print(f"Plan can continue from turn {progress['current_turn']}")
```

## 🔮 Future Enhancements

### **Planned Features**
- **Dynamic plan adjustment**: Modify plans based on conversation flow
- **Learning from patterns**: Improve planning based on successful conversations
- **Multi-agent coordination**: Coordinate plans across multiple agents
- **Real-time optimization**: Optimize plans during execution

### **Extensibility**
- **Custom conversation patterns**: Add new conversation flow patterns
- **Custom planning strategies**: Implement domain-specific planning strategies
- **Custom turn types**: Add new types of conversation turns
- **Integration hooks**: Connect with external conversation management systems

## 🧪 Testing

### **Running the Demo**
```bash
# Run the multi-turn planning demo
python multi_turn_planning_demo.py

# Run specific demo functions
python -c "
from multi_turn_planning_demo import demo_multi_turn_planning
demo_multi_turn_planning()
"
```

### **Test Coverage**
The multi-turn planning system includes comprehensive testing:
- **Unit tests**: Individual component testing
- **Integration tests**: End-to-end workflow testing
- **Pattern testing**: Conversation pattern validation
- **Error handling**: Error recovery and fallback testing

## 📚 API Reference

### **MultiTurnPlanningEngine Methods**
- `generate_multi_turn_plan(request)` - Generate multi-turn execution plan
- `get_planning_statistics()` - Get planning engine statistics

### **MultiTurnPlanExecutor Methods**
- `execute_turn(plan, turn_number, context)` - Execute a single turn
- `can_advance_to_next_turn(plan, current_turn)` - Check if next turn is ready
- `get_plan_progress(plan)` - Get detailed plan progress
- `get_execution_statistics()` - Get execution statistics

### **PlanningSierraAgent Methods**
- `get_multi_turn_plan_progress()` - Get current plan progress
- `reset_multi_turn_plan()` - Reset current multi-turn plan
- `_should_use_multi_turn_planning()` - Determine if multi-turn planning should be used

## 🤝 Contributing

### **Adding New Features**
1. **Extend conversation patterns** for new scenarios
2. **Add planning strategies** for different complexity levels
3. **Implement new turn types** for specific use cases
4. **Enhance monitoring** and analytics capabilities

### **Testing Guidelines**
1. **Unit tests** for all new functionality
2. **Integration tests** for multi-turn workflows
3. **Pattern validation** for conversation flows
4. **Documentation** for new features

---

## 🎉 Summary

The multi-turn planning architecture represents a significant evolution in AI conversation management. By enabling the Sierra Agent to plan conversations across multiple turns, the system provides:

- **Strategic conversation management** with long-term planning
- **Context preservation** across multiple interactions
- **Intelligent flow control** based on conversation patterns
- **Comprehensive progress tracking** and monitoring
- **Graceful error handling** and recovery mechanisms

This architecture makes the Sierra Agent more intelligent, capable of handling complex customer service scenarios that require multiple conversation turns, while maintaining the fast response times and reliability of the existing system.

**Experience the future of AI conversation management with strategic multi-turn planning! 🚀**
