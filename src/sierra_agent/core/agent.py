"""
Sierra Outfitters AI Agent - Main Orchestrator

This module contains the central AI agent that coordinates all system components
including conversation management, LLM integration, quality monitoring, and analytics.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..ai.llm_client import LLMClient
from ..core.conversation import Conversation
from ..tools.tool_orchestrator import ToolOrchestrator
from ..analytics.quality_scorer import QualityScorer
from ..analytics.conversation_analytics import ConversationAnalytics
from ..data.data_types import IntentType, SentimentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the Sierra Agent."""
    quality_check_interval: int = 3
    analytics_update_interval: int = 5
    max_conversation_length: int = 50
    enable_quality_monitoring: bool = True
    enable_analytics: bool = True


class SierraAgent:
    """Base AI Agent for Sierra Outfitters customer service."""
    
    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        print("🔧 [AGENT] Initializing Sierra Agent...")
        self.config = config or AgentConfig()
        print(f"🔧 [AGENT] Configuration: quality_check_interval={self.config.quality_check_interval}, analytics_update_interval={self.config.analytics_update_interval}")
        
        print("🔧 [AGENT] Initializing conversation manager...")
        self.conversation = Conversation()
        
        print("🔧 [AGENT] Initializing tool orchestrator...")
        self.tool_orchestrator = ToolOrchestrator()
        
        print("🔧 [AGENT] Initializing quality scorer...")
        self.quality_scorer = QualityScorer()
        
        print("🔧 [AGENT] Initializing analytics...")
        self.analytics = ConversationAnalytics()
        
        self.session_id: Optional[str] = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0
        
        print("🔧 [AGENT] SierraAgent initialization complete!")
        logger.info("SierraAgent initialized successfully")
    
    def start_conversation(self) -> str:
        """Start a new conversation session."""
        print("🚀 [AGENT] Starting new conversation session...")
        
        # Generate session ID
        self.session_id = f"session_{int(time.time())}"
        print(f"🚀 [AGENT] Generated session ID: {self.session_id}")
        
        # Reset interaction counter
        self.interaction_count = 0
        print(f"🚀 [AGENT] Reset interaction counter to 0")
        
        # Reset conversation
        self.conversation.clear_conversation()
        print(f"🚀 [AGENT] Cleared previous conversation")
        
        # Add system message
        self.conversation.add_system_message(f"Session {self.session_id} started")
        print(f"🚀 [AGENT] Added system message for session start")
        
        logger.info(f"Started conversation session {self.session_id}")
        print(f"✅ [AGENT] Conversation session {self.session_id} started successfully")
        
        return self.session_id
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response."""
        print(f"\n👤 [AGENT] Processing user input: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")
        print(f"👤 [AGENT] Session: {self.session_id}, Interaction: {self.interaction_count + 1}")
        
        try:
            # Add user message to conversation
            print("👤 [AGENT] Adding user message to conversation...")
            self.conversation.add_user_message(user_input)
            
            # Increment interaction counter
            self.interaction_count += 1
            print(f"👤 [AGENT] Interaction counter incremented to {self.interaction_count}")
            
            # Classify intent
            print("🧠 [AGENT] Classifying user intent...")
            intent = self._classify_intent(user_input)
            print(f"🧠 [AGENT] Classified intent: {intent}")
            
            # Analyze sentiment
            print("😊 [AGENT] Analyzing user sentiment...")
            sentiment = self._analyze_sentiment(user_input)
            print(f"😊 [AGENT] Analyzed sentiment: {sentiment}")
            
            # Update conversation state
            print("📝 [AGENT] Updating conversation state...")
            self.conversation.update_customer_sentiment(sentiment)
            print(f"📝 [AGENT] Updated conversation state with sentiment: {sentiment}")
            
            # Execute business tools
            print("🛠️ [AGENT] Executing business tools for intent...")
            tool_results = self._execute_business_tools(intent, user_input)
            print(f"🛠️ [AGENT] Tool execution completed. Results: {len(tool_results)} tools executed")
            
            # Generate response
            print("💬 [AGENT] Generating AI response...")
            response = self._generate_response(user_input, intent, sentiment, tool_results)
            print(f"💬 [AGENT] Generated response: '{response[:50]}{'...' if len(response) > 50 else ''}'")
            
            # Add AI response to conversation
            print("💬 [AGENT] Adding AI response to conversation...")
            self.conversation.add_ai_message(response)
            
            # Check if quality monitoring is needed
            if self.config.enable_quality_monitoring and self.interaction_count % self.config.quality_check_interval == 0:
                print("📊 [AGENT] Triggering quality check...")
                self._check_conversation_quality()
            
            # Check if analytics update is needed
            if self.config.enable_analytics and self.interaction_count % self.config.analytics_update_interval == 0:
                print("📈 [AGENT] Triggering analytics update...")
                self._update_analytics()
            
            print(f"✅ [AGENT] User input processing completed successfully")
            return response
            
        except Exception as e:
            print(f"❌ [AGENT] Error processing user input: {e}")
            logger.error(f"Error processing user input: {e}")
            
            # Generate fallback response
            fallback_response = "I'm experiencing some technical difficulties right now. Please try again in a moment."
            print(f"🔄 [AGENT] Generated fallback response: {fallback_response}")
            
            # Add fallback response to conversation
            self.conversation.add_ai_message(fallback_response)
            print(f"🔄 [AGENT] Added fallback response to conversation")
            
            return fallback_response
    
    def _classify_intent(self, user_input: str) -> IntentType:
        """Classify the user's intent."""
        print(f"🧠 [INTENT] Classifying intent for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        try:
            intent = self.tool_orchestrator.llm_client.classify_intent(user_input)
            print(f"🧠 [INTENT] Successfully classified as: {intent}")
            return intent
        except Exception as e:
            print(f"❌ [INTENT] Error classifying intent: {e}")
            print(f"🔄 [INTENT] Falling back to CUSTOMER_SERVICE intent")
            return IntentType.CUSTOMER_SERVICE
    
    def _analyze_sentiment(self, user_input: str) -> SentimentType:
        """Analyze the user's sentiment."""
        print(f"😊 [SENTIMENT] Analyzing sentiment for: '{user_input[:30]}{'...' if len(user_input) > 30 else ''}'")
        
        try:
            sentiment = self.tool_orchestrator.llm_client.analyze_sentiment(user_input)
            print(f"😊 [SENTIMENT] Successfully analyzed as: {sentiment}")
            return sentiment
        except Exception as e:
            print(f"❌ [SENTIMENT] Error analyzing sentiment: {e}")
            print(f"🔄 [SENTIMENT] Falling back to NEUTRAL sentiment")
            return SentimentType.NEUTRAL
    
    def _execute_business_tools(self, intent: IntentType, user_input: str) -> Dict[str, Any]:
        """Execute business tools based on intent."""
        print(f"🛠️ [TOOLS] Executing tools for intent: {intent}")
        
        try:
            results = self.tool_orchestrator.execute_tools_for_intent(intent, user_input)
            print(f"🛠️ [TOOLS] Successfully executed tools. Results: {results}")
            return results
        except Exception as e:
            print(f"❌ [TOOLS] Error executing tools: {e}")
            print(f"🔄 [TOOLS] Returning empty results")
            return {}
    
    def _generate_response(self, user_input: str, intent: IntentType, sentiment: SentimentType, tool_results: Dict[str, Any]) -> str:
        """Generate AI response based on input and tool results."""
        print(f"💬 [RESPONSE] Generating response for intent: {intent}, sentiment: {sentiment}")
        
        try:
            # Prepare context for response generation
            context = {
                "user_input": user_input,
                "intent": intent.value,
                "sentiment": sentiment.value,
                "tool_results": tool_results,
                "conversation_history": self.conversation.get_message_history(limit=5),
                "session_id": self.session_id,
                "interaction_count": self.interaction_count
            }
            print(f"💬 [RESPONSE] Prepared context with {len(context)} elements")
            
            # Generate response using LLM
            response = self.tool_orchestrator.llm_client.generate_response(context)
            print(f"💬 [RESPONSE] Successfully generated response from LLM")
            
            return response
            
        except Exception as e:
            print(f"❌ [RESPONSE] Error generating response: {e}")
            print(f"🔄 [RESPONSE] Falling back to default response")
            
            # Fallback response based on intent
            if intent == IntentType.ORDER_STATUS:
                return "I'd be happy to help you with your order. Could you please provide your order number?"
            elif intent == IntentType.PRODUCT_INQUIRY:
                return "I'd be happy to help you find the perfect outdoor gear. What are you looking for?"
            else:
                return "Thank you for contacting Sierra Outfitters. How can I assist you today?"
    
    def _check_conversation_quality(self) -> None:
        """Check and update conversation quality."""
        print(f"📊 [QUALITY] Starting quality check for interaction {self.interaction_count}")
        
        try:
            quality_score = self.quality_scorer.score_conversation(self.conversation)
            print(f"📊 [QUALITY] Quality score calculated: {quality_score.overall_score:.2f} ({quality_score.quality_level.value})")
            
            # Update conversation with quality score
            self.conversation.update_quality_score(quality_score.overall_score)
            print(f"📊 [QUALITY] Updated conversation with quality score: {quality_score.overall_score:.2f}")
            
            self.last_quality_check = self.interaction_count
            print(f"📊 [QUALITY] Quality check completed successfully")
            
        except Exception as e:
            print(f"❌ [QUALITY] Error during quality check: {e}")
            logger.error(f"Error during quality check: {e}")
    
    def _update_analytics(self) -> None:
        """Update conversation analytics."""
        print(f"📈 [ANALYTICS] Starting analytics update for interaction {self.interaction_count}")
        
        try:
            if self.session_id:  # Only update if we have a valid session ID
                print(f"📈 [ANALYTICS] Adding conversation to analytics for session: {self.session_id}")
                self.analytics.add_conversation(
                    session_id=self.session_id,
                    conversation=self.conversation
                )
                print(f"📈 [ANALYTICS] Successfully added conversation to analytics")
                
                self.last_analytics_update = self.interaction_count
                print(f"📈 [ANALYTICS] Analytics update completed successfully")
            else:
                print(f"⚠️ [ANALYTICS] No valid session ID, skipping analytics update")
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error updating analytics: {e}")
            logger.error(f"Error updating analytics: {e}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        print(f"📋 [SUMMARY] Generating conversation summary for session: {self.session_id}")
        
        try:
            summary = {
                "session_id": self.session_id,
                "interaction_count": self.interaction_count,
                "conversation_length": self.conversation.get_conversation_length(),
                "conversation_duration": self.conversation.get_conversation_duration(),
                "quality_score": self.conversation.quality_score,
                "conversation_phase": self.conversation.conversation_state.conversation_phase,
                "urgency_level": self.conversation.conversation_state.urgency_level,
                "last_quality_check": self.last_quality_check,
                "last_analytics_update": self.last_analytics_update
            }
            
            print(f"📋 [SUMMARY] Generated summary with {len(summary)} elements")
            return summary
            
        except Exception as e:
            print(f"❌ [SUMMARY] Error generating summary: {e}")
            logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}
    
    def reset_conversation(self) -> None:
        """Reset the conversation and start fresh."""
        print(f"🔄 [RESET] Resetting conversation for session: {self.session_id}")
        
        self.conversation.clear_conversation()
        self.session_id = None
        self.interaction_count = 0
        self.last_quality_check = 0
        self.last_analytics_update = 0
        
        print(f"🔄 [RESET] Conversation reset completed successfully")
        logger.info("Conversation reset")
    
    def end_conversation(self) -> None:
        """End the current conversation and finalize analytics."""
        print(f"🏁 [END] Ending conversation for session: {self.session_id}")
        
        try:
            # Final quality check
            if self.config.enable_quality_monitoring:
                print(f"🏁 [END] Performing final quality check...")
                self._check_conversation_quality()
            
            # Final analytics update
            if self.config.enable_analytics:
                print(f"🏁 [END] Performing final analytics update...")
                self._update_analytics()
            
            # Generate final summary
            print(f"🏁 [END] Generating final conversation summary...")
            final_summary = self.get_conversation_summary()
            print(f"🏁 [END] Final summary: {final_summary}")
            
            print(f"✅ [END] Conversation ended successfully")
            
        except Exception as e:
            print(f"❌ [END] Error ending conversation: {e}")
            logger.error(f"Error ending conversation: {e}")
