# Plan Execution with Multiple Tools

This guide explains how to create and execute plans that use multiple tools from the Sierra Agent system. The system provides a sophisticated planning and execution framework that allows you to orchestrate complex customer service workflows.

## Overview

The Sierra Agent system includes:

- **Planning Engine**: Generates strategic execution plans for customer requests
- **Plan Executor**: Executes planned sequences of tools with dependency management
- **Business Tools**: Collection of tools for customer service operations
- **Data Types**: Structured data classes for plans, steps, and execution context

## Key Concepts

### Plan Structure

A plan consists of multiple steps, each with:
- **Step ID**: Unique identifier for the step
- **Step Type**: Type of operation (tool execution, validation, conditional, etc.)
- **Tool Name**: The specific tool to execute (if applicable)
- **Parameters**: Input parameters for the tool
- **Dependencies**: Other steps that must complete before this step
- **Priority**: Execution priority level

### Step Types

- `TOOL_EXECUTION`: Execute a business tool
- `VALIDATION`: Validate data or conditions
- `CONDITIONAL_BRANCH`: Execute logic based on conditions
- `LOOP`: Repeat operations
- `USER_INTERACTION`: Handle user input
- `DATA_TRANSFORMATION`: Transform or compile data

### Dependencies

Steps can depend on other steps, creating a directed acyclic graph (DAG). The executor automatically handles dependency resolution and executes steps in the correct order.

## Examples

### 1. Simple Multi-Tool Plan

The `simple_plan_example.py` demonstrates a basic plan with multiple tools:

```python
def create_simple_multi_tool_plan() -> Plan:
    # Step 1: Search for products
    step_1 = PlanStep(
        step_id="search_products",
        step_type=PlanStepType.TOOL_EXECUTION,
        name="Search Products",
        tool_name="search_products",
        parameters={"query": "hiking boots camping gear"},
        dependencies=[],
        priority=PlanPriority.HIGH
    )
    
    # Step 2: Check order status (depends on step 1)
    step_2 = PlanStep(
        step_id="check_order",
        step_type=PlanStepType.TOOL_EXECUTION,
        name="Check Order Status",
        tool_name="get_order_status",
        parameters={"user_input": "I ordered hiking boots last week"},
        dependencies=["search_products"],  # Depends on step 1
        priority=PlanPriority.HIGH
    )
    
    # Create the plan
    plan = Plan(
        plan_id=f"simple_plan_{uuid.uuid4().hex[:8]}",
        name="Multi-Tool Customer Service Plan",
        description="Simple plan using multiple tools for customer service",
        customer_request="Check my hiking boots order and find camping gear",
        steps=[step_1, step_2],
        estimated_duration=60,
        priority=PlanPriority.MEDIUM,
        status=PlanStatus.PENDING
    )
    
    return plan
```

### 2. Comprehensive Customer Service Plan

The `plan_execution_example.py` shows a more complex plan with 8 steps:

1. **Analyze Request**: Understand customer needs
2. **Get Order Status**: Check existing orders
3. **Search Products**: Find relevant products
4. **Get Recommendations**: Generate personalized recommendations
5. **Check Discounts**: Look for available promotions
6. **Calculate Shipping**: Determine shipping costs
7. **Get Promotions**: Retrieve current sales
8. **Compile Response**: Combine all information

### 3. Conditional Planning

Plans can include conditional logic:

```python
# Conditional branch step
step_2 = PlanStep(
    step_id="conditional_branch",
    step_type=PlanStepType.CONDITIONAL_BRANCH,
    name="Determine Action",
    description="Determine whether to check order or search products",
    conditions={
        "equals": {"field": "intent", "value": "order_status"},
        "exists": {"field": "order_id"}
    },
    dependencies=["analyze_request"],
    priority=PlanPriority.HIGH
)
```

## Available Business Tools

The system provides many tools you can use in your plans:

### Order Management
- `get_order_status`: Check order status
- `get_order_details`: Get detailed order information
- `get_shipping_info`: Retrieve shipping details
- `get_tracking_info`: Get tracking information

### Product Management
- `search_products`: Search for products
- `get_product_details`: Get product information
- `get_product_recommendations`: Generate recommendations

### Customer Service
- `log_complaint`: Log customer complaints
- `get_return_policy`: Check return policies
- `initiate_return`: Start return process

### Pricing & Promotions
- `check_discounts`: Check for available discounts
- `get_current_promotions`: Get current promotions
- `get_sale_items`: Find items on sale

### Shipping
- `calculate_shipping`: Calculate shipping costs
- `get_shipping_options`: Get available shipping methods

## Execution Workflow

### 1. Create the Plan

```python
# Define your steps
steps = [
    PlanStep(...),
    PlanStep(...),
    # ... more steps
]

# Create the plan
plan = Plan(
    plan_id=f"plan_{uuid.uuid4().hex[:8]}",
    name="Your Plan Name",
    description="Description of what this plan does",
    customer_request="Customer's request",
    steps=steps,
    estimated_duration=60,
    priority=PlanPriority.MEDIUM
)
```

### 2. Create Execution Context

```python
context = ExecutionContext(
    plan_id=plan.plan_id,
    session_id=f"session_{uuid.uuid4().hex[:8]}",
    user_input="Customer's input",
    conversation_history=[],
    global_variables={
        "customer_input": "Customer's input",
        "customer_id": "CUST001"
    }
)
```

### 3. Execute the Plan

```python
executor = PlanExecutor()
result = executor.execute_plan(plan, context)
```

### 4. Handle Results

```python
if result.success:
    print(f"Plan completed in {result.total_duration:.2f} seconds")
    print(f"Completed steps: {result.completed_steps}")
    print(f"Final output: {result.final_output}")
else:
    print(f"Plan failed: {result.error_message}")
    print(f"Failed steps: {result.failed_steps}")
```

## Best Practices

### 1. Plan Structure
- Keep steps focused and single-purpose
- Use clear, descriptive names for steps
- Set appropriate priorities for each step

### 2. Dependencies
- Design dependencies to minimize execution time
- Avoid circular dependencies
- Use dependencies to ensure data is available when needed

### 3. Error Handling
- Set appropriate timeouts for each step
- Configure retry logic for critical steps
- Handle failures gracefully

### 4. Performance
- Estimate realistic durations for each step
- Consider parallel execution where possible
- Monitor execution times and optimize

## Advanced Features

### Plan Templates

The system includes pre-built templates for common scenarios:

```python
planning_engine = PlanningEngine()
templates = planning_engine.plan_templates

# Use existing templates
order_status_template = templates["order_status"]
product_inquiry_template = templates["product_inquiry"]
```

### Planning Strategies

Different complexity levels are supported:

- **Simple**: Linear execution (up to 5 steps)
- **Moderate**: Conditional branches (up to 10 steps)
- **Complex**: Loops and advanced logic (up to 20 steps)

### Variable Resolution

Steps can reference variables from context:

```python
# In step parameters
parameters={"input": "$customer_input"}

# In execution context
global_variables={"customer_input": "actual value"}
```

## Running the Examples

### Prerequisites

Ensure you have the Sierra Agent system installed and configured.

### Simple Example

```bash
python simple_plan_example.py
```

### Comprehensive Example

```bash
python plan_execution_example.py
```

## Troubleshooting

### Common Issues

1. **Tool Not Found**: Ensure the tool name matches exactly with available tools
2. **Dependency Errors**: Check that all dependencies are valid step IDs
3. **Parameter Errors**: Verify parameter names and types match tool requirements
4. **Timeout Issues**: Adjust timeout values for slow operations

### Debugging

- Check the execution log for detailed step information
- Verify step dependencies are correctly configured
- Ensure all required tools are available
- Check parameter values and variable resolution

## Next Steps

- Explore the available business tools in `src/sierra_agent/tools/business_tools.py`
- Study the planning engine in `src/sierra_agent/tools/planning_engine.py`
- Review the plan executor in `src/sierra_agent/tools/plan_executor.py`
- Examine data types in `src/sierra_agent/data/data_types.py`

The Sierra Agent system provides a powerful framework for creating sophisticated customer service workflows. By understanding how to create and execute plans with multiple tools, you can build complex, intelligent customer service experiences.
