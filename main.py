#!/usr/bin/env python3
"""
Sierra Agent - Main Entry Point

AI-powered customer service agent for Sierra Outfitters with real-time
quality monitoring, comprehensive analytics, and intelligent planning.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sierra_agent import SierraAgent, Branding, ErrorMessages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Display the Sierra Outfitters welcome banner."""
    print("🏔️" * 50)
    print("🏔️  SIERRA OUTFITTERS ADVENTURE AGENT  🏔️")
    print("🏔️" * 50)
    print("Your AI-powered outdoor gear companion - Adventure awaits! 🏔️")
    print("Ready to help you gear up for your next expedition!")
    print("Type 'help' for available commands, 'quit' to exit.")
    print("=" * 50)


def print_help():
    """Display available commands and their descriptions."""
    print("\n📋 Available Commands:")
    print("  help     - Show this help message")
    print("  stats    - Display conversation statistics")
    print("  summary  - Show conversation summary")
    print("  reset    - Reset current conversation")
    print("  planning - Show planning system status")
    print("  quit     - Exit the application")
    print("\n🏔️ Just type naturally to chat with your adventure agent!")
    print("   Examples:")
    print("   - 'I need help finding hiking boots'")
    print("   - 'Track my order #W001'")
    print("   - 'What Early Risers deals are available?'")
    print("   - 'Tell me about your return policy'")
    print("\n🧠 Planning Mode:")
    print("   - Complex requests automatically use smart planning")
    print("   - Simple requests use quick response mode")
    print("   - Type 'planning' to see current strategy")


def print_conversation_summary(agent: SierraAgent):
    """Display a summary of the current conversation."""
    if not agent.session_id:
        print("⚠️  No active conversation session.")
        return
    
    summary = agent.get_conversation_summary()
    print("\n📊 Conversation Summary:")
    print("=" * 30)
    print(f"Session ID: {summary['session_id']}")
    print(f"Interactions: {summary['interaction_count']}")
    print(f"Messages: {summary['conversation_length']}")
    print(f"Duration: {summary['conversation_duration']:.1f} seconds")
    print(f"Quality Score: {summary['quality_score'] or 'Not assessed'}")
    
    if summary['conversation_patterns']:
        print(f"Phase: {summary['conversation_patterns']['conversation_phase']}")
        print(f"Urgency: {summary['conversation_patterns']['urgency_level']}")


def print_planning_status(agent: SierraAgent):
    """Display the current planning system status."""
    print("\n🧠 Planning System Status:")
    print("=" * 30)
    
    stats = agent.get_agent_statistics()
    
    # Planning configuration
    config = stats.get('configuration', {})
    print(f"Planning Enabled: {'✅ Yes' if config.get('enable_planning') else '❌ No'}")
    print(f"Planning Threshold: {config.get('planning_threshold', 'N/A')} characters")
    
    # Planning statistics
    planning_stats = stats.get('planning_stats', {})
    print(f"Planning Strategies: {planning_stats.get('strategies', 'N/A')}")
    print(f"Plan Templates: {planning_stats.get('templates', 'N/A')}")
    
    # Execution statistics
    execution_stats = stats.get('execution_stats', {})
    print(f"Total Plans Executed: {execution_stats.get('total_executions', 'N/A')}")
    print(f"Success Rate: {execution_stats.get('success_rate', 'N/A'):.1%}")
    
    # Business rules
    print(f"Business Rules: {stats.get('business_rules_count', 'N/A')}")


def main():
    """Main application entry point."""
    print_banner()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required.")
        print("Please set your OpenAI API key and try again.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Initialize the AI agent
    try:
        print("\n🔧 Initializing Adventure AI Agent...")
        agent = SierraAgent()
        print("✅ Adventure AI Agent initialized successfully! 🏔️")
    except Exception as e:
        print(f"❌ Failed to initialize Adventure AI Agent: {e}")
        logger.error(f"Agent initialization failed: {e}")
        sys.exit(1)
    
    # Start conversation
    print("\n🚀 Starting your adventure conversation session...")
    session_id = agent.start_conversation()
    print(f"✅ Session started: {session_id} - Onward into the unknown! 🏔️")
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Handle special commands
            if user_input.lower() == 'quit':
                print("\n👋 Thank you for using Sierra Outfitters Planning Agent!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'stats':
                print("\n📊 Conversation Statistics:")
                stats = agent.get_agent_statistics()
                print(f"LLM Status: {stats['llm_status']}")
                print(f"Conversation: {stats['conversation_summary']}")
                continue
            elif user_input.lower() == 'summary':
                print_conversation_summary(agent)
                continue
            elif user_input.lower() == 'planning':
                print_planning_status(agent)
                continue
            elif user_input.lower() == 'reset':
                print("\n🔄 Resetting conversation...")
                agent.reset_conversation()
                session_id = agent.start_conversation()
                print(f"✅ New session started: {session_id}")
                continue
            elif not user_input:
                print("Please enter a message or command.")
                continue
            
            # Process user input through the AI agent
            print("\n🏔️ Sierra Adventure Agent: ", end="", flush=True)
            response = agent.process_user_input(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Sierra Outfitters Adventure Agent! Happy trails! 🏔️")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            logger.error(f"Error in main loop: {e}")
            print("Please try again or type 'quit' to exit.")
    
    # Finalize analytics and display insights
    try:
        print("\n📈 Finalizing analytics...")
        agent.end_conversation()
        
        # Display final conversation summary
        print_conversation_summary(agent)
        
        # Display planning status
        print_planning_status(agent)
        
        # Display final statistics
        print("\n📊 Final Statistics:")
        stats = agent.get_agent_statistics()
        print(f"Conversation completed successfully!")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not finalize analytics: {e}")
        logger.error(f"Analytics finalization failed: {e}")
    
    print(f"\n{Branding.get_closing_message()}")


if __name__ == "__main__":
    main()
