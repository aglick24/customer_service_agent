"""
Plan Executor

This module executes planned sequences of tools instead of reactive execution.
It handles step dependencies, conditional logic, error handling, and coordinates
the execution of complex multi-step plans.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from ..data.data_types import (
    Plan, PlanStep, PlanStepType, PlanStatus, ExecutionContext,
    PlanExecutionResult, ToolResult
)
from .business_tools import BusinessTools

logger = logging.getLogger(__name__)


@dataclass
class ExecutionStepResult:
    """Result of executing a single plan step."""
    step_id: str
    success: bool
    data: Any
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # metadata is initialized with field(default_factory=dict), so it's never None
        pass


class PlanExecutor:
    """Executes planned sequences of tools with dependency management."""
    
    def __init__(self) -> None:
        print("🚀 [EXECUTOR] Initializing Plan Executor...")
        
        # Initialize business tools
        self.business_tools = BusinessTools()
        print("🚀 [EXECUTOR] Business tools initialized")
        
        # Execution state
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.execution_history: List[PlanExecutionResult] = []
        
        # Step execution handlers
        self.step_handlers = self._initialize_step_handlers()
        print(f"🚀 [EXECUTOR] Initialized {len(self.step_handlers)} step handlers")
        
        # Execution configuration
        self.max_concurrent_executions = 5
        self.default_timeout = 30
        self.max_retries = 3
        
        print("🚀 [EXECUTOR] Plan Executor initialization complete!")
        logger.info("Plan Executor initialized successfully")
    
    def _initialize_step_handlers(self) -> Dict[PlanStepType, Callable]:
        """Initialize handlers for different step types."""
        handlers = {
            PlanStepType.TOOL_EXECUTION: self._execute_tool_step,
            PlanStepType.VALIDATION: self._execute_validation_step,
            PlanStepType.CONDITIONAL_BRANCH: self._execute_conditional_step,
            PlanStepType.LOOP: self._execute_loop_step,
            PlanStepType.USER_INTERACTION: self._execute_user_interaction_step,
            PlanStepType.DATA_TRANSFORMATION: self._execute_data_transformation_step
        }
        return handlers
    
    def execute_plan(self, plan: Plan, context: ExecutionContext) -> PlanExecutionResult:
        """Execute a complete plan."""
        print(f"🚀 [EXECUTOR] Executing plan: {plan.name} (ID: {plan.plan_id})")
        print(f"🚀 [EXECUTOR] Plan contains {len(plan.steps)} steps")
        
        start_time = time.time()
        
        # Update plan status
        plan.status = PlanStatus.IN_PROGRESS
        
        # Store execution context
        self.active_executions[plan.plan_id] = context
        
        try:
            # Execute steps according to plan
            execution_result = self._execute_plan_steps(plan, context)
            
            # Update plan status
            if execution_result.success:
                plan.status = PlanStatus.COMPLETED
                print(f"✅ [EXECUTOR] Plan execution completed successfully")
            else:
                plan.status = PlanStatus.FAILED
                print(f"❌ [EXECUTOR] Plan execution failed")
            
            # Store execution result
            self.execution_history.append(execution_result)
            
            return execution_result
            
        except Exception as e:
            print(f"❌ [EXECUTOR] Critical error during plan execution: {e}")
            logger.error(f"Critical error during plan execution: {e}")
            
            # Update plan status
            plan.status = PlanStatus.FAILED
            
            # Create error result
            error_result = PlanExecutionResult(
                plan_id=plan.plan_id,
                success=False,
                completed_steps=[],
                failed_steps=[step.step_id for step in plan.steps],
                total_duration=time.time() - start_time,
                final_output=None,
                error_message=str(e),
                execution_log=[]
            )
            
            self.execution_history.append(error_result)
            return error_result
            
        finally:
            # Clean up execution context
            if plan.plan_id in self.active_executions:
                del self.active_executions[plan.plan_id]
    
    def _execute_plan_steps(self, plan: Plan, context: ExecutionContext) -> PlanExecutionResult:
        """Execute all steps in the plan according to dependencies."""
        print(f"🚀 [EXECUTOR] Starting step execution for plan: {plan.plan_id}")
        
        completed_steps = []
        failed_steps = []
        execution_log = []
        step_results: Dict[str, Any] = {}
        
        # Execute steps in dependency order
        for step in plan.steps:
            print(f"🚀 [EXECUTOR] Executing step: {step.name} (ID: {step.step_id})")
            
            try:
                # Check dependencies
                if not self._check_dependencies(step, step_results):
                    print(f"⚠️ [EXECUTOR] Dependencies not met for step: {step.step_id}")
                    failed_steps.append(step.step_id)
                    continue
                
                # Execute step
                step_result = self._execute_single_step(step, context, step_results)
                
                if step_result.success:
                    completed_steps.append(step.step_id)
                    step_results[step.step_id] = step_result.data
                    print(f"✅ [EXECUTOR] Step {step.step_id} completed successfully")
                else:
                    failed_steps.append(step.step_id)
                    print(f"❌ [EXECUTOR] Step {step.step_id} failed: {step_result.error_message}")
                
                # Log execution
                execution_log.append({
                    "step_id": step.step_id,
                    "step_name": step.name,
                    "success": step_result.success,
                    "execution_time": step_result.execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "error_message": step_result.error_message
                })
                
                # Update context
                context.current_step = step.step_id
                context.step_results[step.step_id] = step_result.data
                context.last_activity = datetime.now()
                
            except Exception as e:
                print(f"❌ [EXECUTOR] Error executing step {step.step_id}: {e}")
                failed_steps.append(step.step_id)
                execution_log.append({
                    "step_id": step.step_id,
                    "step_name": step.name,
                    "success": False,
                    "execution_time": 0,
                    "timestamp": datetime.now().isoformat(),
                    "error_message": str(e)
                })
        
        # Determine overall success
        success = len(failed_steps) == 0
        
        # Generate final output
        final_output = self._generate_final_output(plan, step_results, context)
        
        execution_result = PlanExecutionResult(
            plan_id=plan.plan_id,
            success=success,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            total_duration=time.time() - context.execution_start.timestamp(),
            final_output=final_output,
            error_message=None if success else f"Failed steps: {', '.join(failed_steps)}",
            execution_log=execution_log
        )
        
        print(f"🚀 [EXECUTOR] Plan execution completed. Success: {success}, Completed: {len(completed_steps)}, Failed: {len(failed_steps)}")
        return execution_result
    
    def _check_dependencies(self, step: PlanStep, step_results: Dict[str, Any]) -> bool:
        """Check if all dependencies for a step are satisfied."""
        if not step.dependencies:
            return True
        
        for dep_id in step.dependencies:
            if dep_id not in step_results:
                print(f"⚠️ [EXECUTOR] Dependency {dep_id} not satisfied for step {step.step_id}")
                return False
        
        return True
    
    def _execute_single_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> ExecutionStepResult:
        """Execute a single plan step."""
        start_time = time.time()
        
        try:
            # Get the appropriate handler for this step type
            handler = self.step_handlers.get(step.step_type)
            if not handler:
                raise ValueError(f"No handler found for step type: {step.step_type}")
            
            # Execute the step
            result_data = handler(step, context, step_results)
            
            execution_time = time.time() - start_time
            
            return ExecutionStepResult(
                step_id=step.step_id,
                success=True,
                data=result_data,
                execution_time=execution_time,
                metadata={"step_type": step.step_type.value}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ [EXECUTOR] Error executing step {step.step_id}: {e}")
            
            return ExecutionStepResult(
                step_id=step.step_id,
                success=False,
                data=None,
                execution_time=execution_time,
                error_message=str(e),
                metadata={"step_type": step.step_type.value}
            )
    
    def _execute_tool_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> Any:
        """Execute a tool execution step."""
        print(f"🔧 [EXECUTOR] Executing tool: {step.tool_name}")
        
        if not step.tool_name:
            raise ValueError("Tool name not specified for tool execution step")
        
        # Check if tool exists in business tools
        if hasattr(self.business_tools, step.tool_name):
            tool_method = getattr(self.business_tools, step.tool_name)
            
            # Prepare parameters
            params = self._prepare_tool_parameters(step.parameters, context, step_results)
            
            # Execute tool
            result = tool_method(**params)
            print(f"✅ [EXECUTOR] Tool {step.tool_name} executed successfully")
            
            return result
        
        else:
            raise ValueError(f"Tool '{step.tool_name}' not found in business tools")
    
    def _execute_validation_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> bool:
        """Execute a validation step."""
        print(f"✅ [EXECUTOR] Executing validation: {step.name}")
        
        # For now, use simple validation logic
        # In a real implementation, this could call validation services
        validation_result = True
        
        if step.parameters.get("required_fields"):
            required_fields = step.parameters["required_fields"]
            for field in required_fields:
                if field not in context.global_variables:
                    validation_result = False
                    break
        
        print(f"✅ [EXECUTOR] Validation {'passed' if validation_result else 'failed'}")
        return validation_result
    
    def _execute_conditional_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> Any:
        """Execute a conditional branch step."""
        print(f"🔀 [EXECUTOR] Executing conditional: {step.name}")
        
        if not step.conditions:
            raise ValueError("No conditions specified for conditional step")
        
        # Evaluate conditions
        condition_result = self._evaluate_conditions(step.conditions, context, step_results)
        
        print(f"🔀 [EXECUTOR] Conditional result: {condition_result}")
        return condition_result
    
    def _execute_loop_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> List[Any]:
        """Execute a loop step."""
        print(f"🔄 [EXECUTOR] Executing loop: {step.name}")
        
        # For now, implement simple loop logic
        # In a real implementation, this could handle complex loop scenarios
        loop_count = step.parameters.get("loop_count", 1)
        loop_results = []
        
        for i in range(loop_count):
            # Execute the loop body (simplified)
            loop_result = f"Loop iteration {i + 1}"
            loop_results.append(loop_result)
        
        print(f"🔄 [EXECUTOR] Loop completed with {len(loop_results)} iterations")
        return loop_results
    
    def _execute_user_interaction_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> str:
        """Execute a user interaction step."""
        print(f"👤 [EXECUTOR] Executing user interaction: {step.name}")
        
        # For now, return a placeholder response
        # In a real implementation, this could handle actual user interactions
        interaction_response = f"User interaction: {step.name}"
        
        print(f"👤 [EXECUTOR] User interaction completed")
        return interaction_response
    
    def _execute_data_transformation_step(self, step: PlanStep, context: ExecutionContext, step_results: Dict[str, Any]) -> Any:
        """Execute a data transformation step."""
        print(f"🔄 [EXECUTOR] Executing data transformation: {step.name}")
        
        # For now, implement simple transformations
        # In a real implementation, this could handle complex data processing
        transformation_type = step.parameters.get("transformation_type", "identity")
        
        if transformation_type == "format_currency":
            # Format numbers as currency
            input_data = step.parameters.get("input_data", 0)
            formatted = f"${input_data:.2f}"
            return formatted
        elif transformation_type == "extract_keywords":
            # Extract keywords from text
            text = step.parameters.get("input_text", "")
            keywords = text.lower().split()[:5]  # Simple keyword extraction
            return keywords
        else:
            # Identity transformation
            return step.parameters.get("input_data", None)
    
    def _prepare_tool_parameters(self, parameters: Dict[str, Any], context: ExecutionContext, step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tool parameters by resolving variables and context."""
        prepared_params = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("$"):
                # Variable reference
                var_name = value[1:]
                if var_name in context.global_variables:
                    prepared_params[key] = context.global_variables[var_name]
                elif var_name in step_results:
                    prepared_params[key] = step_results[var_name]
                else:
                    prepared_params[key] = value  # Keep original if variable not found
            else:
                prepared_params[key] = value
        
        return prepared_params
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: ExecutionContext, step_results: Dict[str, Any]) -> bool:
        """Evaluate conditional logic."""
        # Simple condition evaluation
        # In a real implementation, this could handle complex boolean logic
        
        for condition_type, condition_value in conditions.items():
            if condition_type == "equals":
                field = condition_value.get("field")
                value = condition_value.get("value")
                
                if field in context.global_variables:
                    if context.global_variables[field] != value:
                        return False
                else:
                    return False
            
            elif condition_type == "exists":
                field = condition_value.get("field")
                if field not in context.global_variables:
                    return False
            
            elif condition_type == "greater_than":
                field = condition_value.get("field")
                threshold = condition_value.get("threshold", 0)
                
                if field in context.global_variables:
                    if not isinstance(context.global_variables[field], (int, float)):
                        return False
                    if context.global_variables[field] <= threshold:
                        return False
                else:
                    return False
        
        return True
    
    def _generate_final_output(self, plan: Plan, step_results: Dict[str, Any], context: ExecutionContext) -> Any:
        """Generate the final output from plan execution."""
        print(f"📤 [EXECUTOR] Generating final output for plan: {plan.plan_id}")
        
        # For now, return a summary of results
        # In a real implementation, this could generate structured responses
        
        output = {
            "plan_name": plan.name,
            "plan_description": plan.description,
            "execution_summary": {
                "total_steps": len(plan.steps),
                "completed_steps": len(step_results),
                "customer_request": context.user_input
            },
            "step_results": step_results,
            "execution_context": {
                "session_id": context.session_id,
                "execution_duration": (datetime.now() - context.execution_start).total_seconds()
            }
        }
        
        print(f"📤 [EXECUTOR] Final output generated successfully")
        return output
    
    def get_execution_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get the current execution status of a plan."""
        if plan_id in self.active_executions:
            context = self.active_executions[plan_id]
            return {
                "plan_id": plan_id,
                "status": "IN_PROGRESS",
                "current_step": context.current_step,
                "execution_time": (datetime.now() - context.execution_start).total_seconds(),
                "completed_steps": len(context.step_results)
            }
        
        # Check execution history
        for result in reversed(self.execution_history):
            if result.plan_id == plan_id:
                return {
                    "plan_id": plan_id,
                    "status": "COMPLETED" if result.success else "FAILED",
                    "total_duration": result.total_duration,
                    "completed_steps": len(result.completed_steps),
                    "failed_steps": len(result.failed_steps)
                }
        
        return None
    
    def cancel_execution(self, plan_id: str) -> bool:
        """Cancel an active plan execution."""
        if plan_id in self.active_executions:
            print(f"🚫 [EXECUTOR] Cancelling execution of plan: {plan_id}")
            del self.active_executions[plan_id]
            return True
        
        return False
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get statistics about plan execution."""
        total_executions = len(self.execution_history)
        successful_executions = len([r for r in self.execution_history if r.success])
        failed_executions = total_executions - successful_executions
        
        avg_duration = 0.0
        if total_executions > 0:
            total_duration = sum(r.total_duration for r in self.execution_history)
            avg_duration = total_duration / total_executions
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_duration": avg_duration,
            "active_executions": len(self.active_executions)
        }
