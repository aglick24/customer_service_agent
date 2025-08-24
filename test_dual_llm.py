#!/usr/bin/env python3
"""
Test script for the dual LLM setup with planning mechanism.

This script demonstrates how the agent now uses:
1. GPT-4o for complex thinking and planning
2. GPT-4o-mini for low latency operations
3. Strategic planning instead of reactive intent-based execution
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent.core.agent import SierraAgent, AgentConfig

def test_dual_llm_setup():
    """Test the dual LLM setup."""
    print("🧪 Testing Dual LLM Setup with Planning Mechanism")
    print("=" * 60)
    
    # Create agent configuration
    config = AgentConfig(
        quality_check_interval=2,
        analytics_update_interval=3,
        enable_dual_llm=True,
        thinking_model="gpt-4o",
        low_latency_model="gpt-4o-mini"
    )
    
    print(f"🔧 Configuration: {config}")
    
    # Initialize the agent
    print("\n🚀 Initializing Sierra Agent...")
    agent = SierraAgent(config)
    
    # Check LLM status
    print("\n📊 LLM Status:")
    llm_status = agent.get_llm_status()
    for llm_type, status in llm_status.items():
        if llm_type != "dual_llm_enabled":
            print(f"  {llm_type}:")
            print(f"    Model: {status['model']}")
            print(f"    Available: {status['available']}")
            print(f"    API Calls: {status['usage_stats']['total_requests']}")
    
    print(f"  Dual LLM Enabled: {llm_status['dual_llm_enabled']}")
    
    # Start a conversation
    print("\n💬 Starting conversation...")
    session_id = agent.start_conversation()
    print(f"  Session ID: {session_id}")
    
    # Test different types of requests
    test_requests = [
        "What's the status of my order ORD12345?",
        "I need hiking boots for a mountain trip next week",
        "How do I return a jacket that doesn't fit?",
        "What are your current promotions?"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📝 Test Request {i}: {request}")
        print("-" * 40)
        
        try:
            response = agent.process_user_input(request)
            print(f"🤖 Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            # Get execution statistics
            stats = agent.get_agent_statistics()
            print(f"📊 Planning Stats: {stats['planning_stats']}")
            print(f"📊 Execution Stats: {stats['execution_stats']}")
            
        except Exception as e:
            print(f"❌ Error processing request: {e}")
    
    # Get comprehensive statistics
    print("\n📊 Comprehensive Agent Statistics:")
    print("-" * 40)
    comprehensive_stats = agent.get_agent_statistics()
    
    print(f"LLM Models:")
    print(f"  Thinking: {comprehensive_stats['configuration']['thinking_model']}")
    print(f"  Low Latency: {comprehensive_stats['configuration']['low_latency_model']}")
    
    print(f"\nPlanning Engine:")
    print(f"  Strategies: {comprehensive_stats['planning_stats']['strategies']}")
    print(f"  Templates: {comprehensive_stats['planning_stats']['templates']}")
    
    print(f"\nPlan Execution:")
    print(f"  Total Executions: {comprehensive_stats['execution_stats']['total_executions']}")
    print(f"  Success Rate: {comprehensive_stats['execution_stats']['success_rate']:.2%}")
    print(f"  Average Duration: {comprehensive_stats['execution_stats']['average_duration']:.2f}s")
    
    print(f"\nTool Usage:")
    print(f"  Available Tools: {comprehensive_stats['tool_stats']['total_tools']}")
    print(f"  Business Tools: {comprehensive_stats['tool_stats']['business_tools']}")
    print(f"  Custom Tools: {comprehensive_stats['tool_stats']['custom_tools']}")
    
    # Test switching LLM modes
    print("\n🔄 Testing LLM Mode Switching:")
    print("  Switching to single LLM mode...")
    agent.switch_llm_mode(False)
    
    single_llm_status = agent.get_llm_status()
    print(f"  Dual LLM Enabled: {single_llm_status['dual_llm_enabled']}")
    print(f"  Low Latency LLM: {single_llm_status['low_latency_llm']['model']}")
    
    print("  Switching back to dual LLM mode...")
    agent.switch_llm_mode(True)
    
    dual_llm_status = agent.get_llm_status()
    print(f"  Dual LLM Enabled: {dual_llm_status['dual_llm_enabled']}")
    print(f"  Low Latency LLM: {dual_llm_status['low_latency_llm']['model']}")
    
    print("\n✅ Dual LLM setup test completed successfully!")

def test_planning_mechanism():
    """Test the planning mechanism specifically."""
    print("\n🧠 Testing Planning Mechanism")
    print("=" * 40)
    
    config = AgentConfig(enable_dual_llm=True)
    agent = SierraAgent(config)
    
    # Start conversation
    session_id = agent.start_conversation()
    
    # Test complex request that should trigger planning
    complex_request = """
    I ordered hiking boots last week but they haven't arrived yet. 
    I need them for a trip this weekend. Can you check the status, 
    and if they're delayed, suggest alternatives or expedited shipping options?
    """
    
    print(f"📝 Complex Request: {complex_request.strip()}")
    print("-" * 50)
    
    try:
        response = agent.process_user_input(complex_request)
        print(f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        # Get planning statistics
        stats = agent.get_agent_statistics()
        planning_stats = stats['planning_stats']
        execution_stats = stats['execution_stats']
        
        print(f"\n📊 Planning Results:")
        print(f"  Plan Generated: {planning_stats['strategies'] > 0}")
        print(f"  Templates Used: {planning_stats['templates'] > 0}")
        print(f"  Execution Success: {execution_stats['success_rate']:.2%}")
        
    except Exception as e:
        print(f"❌ Error testing planning mechanism: {e}")

if __name__ == "__main__":
    try:
        test_dual_llm_setup()
        test_planning_mechanism()
        
        print("\n🎉 All tests completed successfully!")
        print("\nThe agent now uses:")
        print("  🧠 GPT-4o for complex thinking and planning")
        print("  ⚡ GPT-4o-mini for low latency operations")
        print("  📋 Strategic planning instead of reactive execution")
        print("  🔄 Dual LLM mode that can be toggled on/off")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
