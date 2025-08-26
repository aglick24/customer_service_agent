#!/usr/bin/env python3
"""
Quick test to see what tools are actually available
"""

from src.sierra_agent.tools.tool_orchestrator import ToolOrchestrator

def check_available_tools():
    orchestrator = ToolOrchestrator()
    
    print("Available tools:")
    tools = orchestrator.get_available_tools()
    for tool in tools:
        print(f"  - {tool}")
    
    print(f"\nTotal: {len(tools)} tools")
    
    print("\nTool descriptions for LLM:")
    descriptions = orchestrator.get_tools_for_llm_planning()
    print(descriptions)

if __name__ == "__main__":
    check_available_tools()