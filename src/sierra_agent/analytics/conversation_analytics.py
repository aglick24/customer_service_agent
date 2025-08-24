"""
Conversation Analytics Module

This module provides analytics and insights for customer service conversations,
including quality metrics, intent analysis, and performance tracking.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter

from ..data.data_types import ConversationMetrics, IntentType, SentimentType
from ..core.conversation import Conversation
from ..analytics.quality_scorer import QualityScorer

logger = logging.getLogger(__name__)


class ConversationAnalytics:
    """Tracks and analyzes conversation metrics for performance insights."""
    
    def __init__(self, data_file: str = "conversation_analytics.json") -> None:
        print(f"📈 [ANALYTICS] Initializing ConversationAnalytics...")
        print(f"📈 [ANALYTICS] Data file: {data_file}")
        
        self.data_file = data_file
        self.quality_scorer = QualityScorer()
        print("📈 [ANALYTICS] Quality scorer initialized")
        
        # Initialize analytics data
        self.conversations: Dict[str, ConversationMetrics] = {}
        self.session_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data if available
        self._load_analytics_data()
        print(f"📈 [ANALYTICS] Loaded {len(self.conversations)} existing conversations")
        
        print("📈 [ANALYTICS] ConversationAnalytics initialized successfully")
        logger.info("ConversationAnalytics initialized")
    
    def _load_analytics_data(self) -> None:
        """Load analytics data from file."""
        print(f"📂 [ANALYTICS] Loading analytics data from {self.data_file}...")
        
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    print(f"📂 [ANALYTICS] Found existing analytics file")
                    
                    # Load conversations
                    if 'conversations' in data:
                        for session_id, conv_data in data['conversations'].items():
                            self.conversations[session_id] = ConversationMetrics(**conv_data)
                        print(f"📂 [ANALYTICS] Loaded {len(data['conversations'])} conversations")
                    
                    # Load session metrics
                    if 'session_metrics' in data:
                        self.session_metrics = data['session_metrics']
                        print(f"📂 [ANALYTICS] Loaded {len(data['session_metrics'])} session metrics")
                    
                    print(f"✅ [ANALYTICS] Analytics data loaded successfully")
            else:
                print(f"📂 [ANALYTICS] No existing analytics file found, starting fresh")
                
        except Exception as e:
            print(f"❌ [ANALYTICS] Error loading analytics data: {e}")
            logger.error(f"Error loading analytics data: {e}")
            # Continue with empty data
            self.conversations = {}
            self.session_metrics = {}
    
    def _save_analytics_data(self) -> None:
        """Save analytics data to file."""
        print(f"💾 [ANALYTICS] Saving analytics data to {self.data_file}...")
        
        try:
            # Prepare data for saving
            data = {
                'conversations': {
                    session_id: conv.to_dict() 
                    for session_id, conv in self.conversations.items()
                },
                'session_metrics': self.session_metrics,
                'last_updated': datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"✅ [ANALYTICS] Analytics data saved successfully")
            logger.info("Analytics data saved")
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error saving analytics data: {e}")
            logger.error(f"Error saving analytics data: {e}")
    
    def add_conversation(self, session_id: str, conversation: Conversation) -> None:
        """Add a conversation to analytics tracking."""
        print(f"➕ [ANALYTICS] Adding conversation to analytics: {session_id}")
        print(f"➕ [ANALYTICS] Conversation has {conversation.get_conversation_length()} messages")
        
        try:
            # Get conversation patterns
            patterns = conversation.get_conversation_patterns()
            print(f"➕ [ANALYTICS] Extracted conversation patterns: {len(patterns)} metrics")
            
            # Get customer sentiment trend
            sentiment_trend = [sentiment.value for sentiment in conversation.get_customer_sentiment_trend()]
            print(f"➕ [ANALYTICS] Extracted sentiment trend: {len(sentiment_trend)} sentiments")
            
            # Create conversation metrics
            conv_metrics = ConversationMetrics(
                session_id=session_id,
                start_time=conversation.start_time.isoformat(),
                end_time=conversation.last_activity.isoformat(),
                duration=conversation.get_conversation_duration(),
                message_count=conversation.get_conversation_length(),
                user_message_count=len(conversation.get_user_messages()),
                ai_message_count=len(conversation.get_ai_messages()),
                quality_score=conversation.quality_score or 0.0,
                conversation_phase=conversation.conversation_state.conversation_phase,
                urgency_level=conversation.conversation_state.urgency_level,
                current_topic=conversation.conversation_state.current_topic,
                sentiment_trend=sentiment_trend,
                intent_distribution={},  # Will be populated if available
                tool_usage={},  # Will be populated if available
                resolution_status="completed" if conversation.conversation_state.conversation_phase == "closing" else "in_progress"
            )
            
            # Store the metrics
            self.conversations[session_id] = conv_metrics
            print(f"➕ [ANALYTICS] Stored conversation metrics for session: {session_id}")
            
            # Update session metrics
            self._update_session_metrics(session_id, conv_metrics)
            print(f"➕ [ANALYTICS] Updated session metrics")
            
            # Save data
            self._save_analytics_data()
            print(f"✅ [ANALYTICS] Conversation added to analytics successfully")
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error adding conversation: {e}")
            logger.error(f"Error adding conversation: {e}")
    
    def _update_session_metrics(self, session_id: str, conv_metrics: ConversationMetrics) -> None:
        """Update session-level metrics."""
        print(f"📊 [ANALYTICS] Updating session metrics for: {session_id}")
        
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = {
                'total_conversations': 0,
                'total_duration': 0.0,
                'total_messages': 0,
                'average_quality_score': 0.0,
                'conversation_phases': Counter(),
                'topics': Counter(),
                'urgency_levels': Counter()
            }
            print(f"📊 [ANALYTICS] Created new session metrics entry")
        
        session = self.session_metrics[session_id]
        session['total_conversations'] += 1
        session['total_duration'] += conv_metrics.duration
        session['total_messages'] += conv_metrics.message_count
        
        # Update average quality score
        total_quality = session['average_quality_score'] * (session['total_conversations'] - 1)
        session['average_quality_score'] = (total_quality + conv_metrics.quality_score) / session['total_conversations']
        
        # Update counters
        session['conversation_phases'][conv_metrics.conversation_phase] += 1
        session['topics'][conv_metrics.current_topic] += 1
        session['urgency_levels'][conv_metrics.urgency_level] += 1
        
        print(f"📊 [ANALYTICS] Session metrics updated: {session['total_conversations']} conversations")
    
    def get_conversation_metrics(self, session_id: str) -> Optional[ConversationMetrics]:
        """Get metrics for a specific conversation."""
        print(f"🔍 [ANALYTICS] Getting conversation metrics for: {session_id}")
        
        if session_id in self.conversations:
            metrics = self.conversations[session_id]
            print(f"✅ [ANALYTICS] Found metrics for session: {session_id}")
            return metrics
        else:
            print(f"❌ [ANALYTICS] No metrics found for session: {session_id}")
            return None
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics across all conversations."""
        print(f"📋 [ANALYTICS] Generating summary statistics...")
        
        if not self.conversations:
            print(f"⚠️ [ANALYTICS] No conversations to analyze")
            return {"message": "No conversations available for analysis"}
        
        try:
            # Calculate basic statistics
            total_conversations = len(self.conversations)
            total_duration = sum(conv.duration for conv in self.conversations.values())
            total_messages = sum(conv.message_count for conv in self.conversations.values())
            avg_quality_score = sum(conv.quality_score for conv in self.conversations.values()) / total_conversations
            
            print(f"📋 [ANALYTICS] Basic stats: {total_conversations} conversations, {total_messages} messages")
            
            # Intent distribution
            intent_counts: Counter[str] = Counter()
            for conv in self.conversations.values():
                for intent, count in conv.intent_distribution.items():
                    intent_counts[intent] += count
            
            # Tool usage
            tool_counts: Counter[str] = Counter()
            for conv in self.conversations.values():
                for tool, count in conv.tool_usage.items():
                    tool_counts[tool] += count
            
            # Conversation phases
            phase_counts = Counter(conv.conversation_phase for conv in self.conversations.values())
            
            # Topics
            topic_counts = Counter(conv.current_topic for conv in self.conversations.values())
            
            # Urgency levels
            urgency_counts = Counter(conv.urgency_level for conv in self.conversations.values())
            
            summary = {
                "total_conversations": total_conversations,
                "total_duration": total_duration,
                "total_messages": total_messages,
                "average_quality_score": round(avg_quality_score, 3),
                "average_conversation_duration": round(total_duration / total_conversations, 2),
                "average_messages_per_conversation": round(total_messages / total_conversations, 2),
                "conversation_phases": dict(phase_counts),
                "topics": dict(topic_counts),
                "urgency_levels": dict(urgency_counts),
                "intent_distribution": dict(intent_counts),
                "tool_usage": dict(tool_counts)
            }
            
            print(f"📋 [ANALYTICS] Summary statistics generated with {len(summary)} metrics")
            return summary
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error generating summary statistics: {e}")
            logger.error(f"Error generating summary statistics: {e}")
            return {"error": f"Failed to generate summary statistics: {str(e)}"}
    
    def get_intent_analysis(self) -> Dict[str, Any]:
        """Get detailed analysis of customer intents."""
        print(f"🧠 [ANALYTICS] Generating intent analysis...")
        
        if not self.conversations:
            print(f"⚠️ [ANALYTICS] No conversations to analyze for intents")
            return {"message": "No conversations available for intent analysis"}
        
        try:
            # Aggregate intent data
            intent_counts: Counter[str] = Counter()
            intent_quality_scores = {}
            intent_duration = {}
            intent_message_counts = {}
            
            for conv in self.conversations.values():
                for intent, count in conv.intent_distribution.items():
                    intent_counts[intent] += count
                    
                    # Track quality scores by intent
                    if intent not in intent_quality_scores:
                        intent_quality_scores[intent] = []
                    intent_quality_scores[intent].append(conv.quality_score)
                    
                    # Track duration by intent
                    if intent not in intent_duration:
                        intent_duration[intent] = []
                    intent_duration[intent].append(conv.duration)
                    
                    # Track message counts by intent
                    if intent not in intent_message_counts:
                        intent_message_counts[intent] = []
                    intent_message_counts[intent].append(conv.message_count)
            
            # Calculate averages
            intent_analysis = {}
            for intent in intent_counts:
                quality_scores = intent_quality_scores[intent]
                durations = intent_duration[intent]
                message_counts = intent_message_counts[intent]
                
                intent_analysis[intent] = {
                    "count": intent_counts[intent],
                    "average_quality_score": round(sum(quality_scores) / len(quality_scores), 3),
                    "average_duration": round(sum(durations) / len(durations), 2),
                    "average_message_count": round(sum(message_counts) / len(message_counts), 2)
                }
            
            print(f"🧠 [ANALYTICS] Intent analysis generated for {len(intent_analysis)} intent types")
            return intent_analysis
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error generating intent analysis: {e}")
            logger.error(f"Error generating intent analysis: {e}")
            return {"error": f"Failed to generate intent analysis: {str(e)}"}
    
    def get_tool_effectiveness(self) -> Dict[str, Any]:
        """Get analysis of tool usage and effectiveness."""
        print(f"🛠️ [ANALYTICS] Generating tool effectiveness analysis...")
        
        if not self.conversations:
            print(f"⚠️ [ANALYTICS] No conversations to analyze for tool usage")
            return {"message": "No conversations available for tool analysis"}
        
        try:
            # Aggregate tool usage data
            tool_counts: Counter[str] = Counter()
            tool_quality_scores = {}
            tool_conversation_counts = {}
            
            for conv in self.conversations.values():
                for tool, count in conv.tool_usage.items():
                    tool_counts[tool] += count
                    
                    # Track quality scores by tool usage
                    if tool not in tool_quality_scores:
                        tool_quality_scores[tool] = []
                    tool_quality_scores[tool].append(conv.quality_score)
                    
                    # Track conversation counts by tool
                    if tool not in tool_conversation_counts:
                        tool_conversation_counts[tool] = set()
                    tool_conversation_counts[tool].add(conv.session_id)
            
            # Calculate effectiveness metrics
            tool_effectiveness = {}
            for tool in tool_counts:
                quality_scores = tool_quality_scores[tool]
                conversation_count = len(tool_conversation_counts[tool])
                
                tool_effectiveness[tool] = {
                    "total_usage": tool_counts[tool],
                    "conversations_used_in": conversation_count,
                    "average_quality_score": round(sum(quality_scores) / len(quality_scores), 3),
                    "usage_frequency": round(tool_counts[tool] / conversation_count, 2) if conversation_count > 0 else 0
                }
            
            print(f"🛠️ [ANALYTICS] Tool effectiveness analysis generated for {len(tool_effectiveness)} tools")
            return tool_effectiveness
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error generating tool effectiveness analysis: {e}")
            logger.error(f"Error generating tool effectiveness analysis: {e}")
            return {"error": f"Failed to generate tool effectiveness analysis: {str(e)}"}
    
    def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get quality score trends over time."""
        print(f"📈 [ANALYTICS] Generating quality trends for last {days} days...")
        
        if not self.conversations:
            print(f"⚠️ [ANALYTICS] No conversations to analyze for quality trends")
            return {"message": "No conversations available for quality trend analysis"}
        
        try:
            # Filter conversations by date
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            recent_conversations = [
                conv for conv in self.conversations.values()
                if datetime.fromisoformat(conv.start_time).timestamp() > cutoff_date
            ]
            
            print(f"📈 [ANALYTICS] Found {len(recent_conversations)} conversations in last {days} days")
            
            if not recent_conversations:
                return {"message": f"No conversations found in last {days} days"}
            
            # Group by day
            daily_quality = {}
            for conv in recent_conversations:
                date = conv.start_time.split('T')[0]  # Extract date part
                if date not in daily_quality:
                    daily_quality[date] = []
                daily_quality[date].append(conv.quality_score)
            
            # Calculate daily averages
            trends = {}
            for date, scores in daily_quality.items():
                trends[date] = {
                    "average_quality": round(sum(scores) / len(scores), 3),
                    "conversation_count": len(scores)
                }
            
            # Sort by date
            sorted_trends = dict(sorted(trends.items()))
            
            print(f"📈 [ANALYTICS] Quality trends generated for {len(sorted_trends)} days")
            return sorted_trends
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error generating quality trends: {e}")
            logger.error(f"Error generating quality trends: {e}")
            return {"error": f"Failed to generate quality trends: {str(e)}"}
    
    def export_analytics(self, format: str = "json") -> str:
        """Export analytics data in specified format."""
        print(f"📤 [ANALYTICS] Exporting analytics data in {format} format...")
        
        try:
            if format.lower() == "json":
                export_data = {
                    "conversations": {
                        session_id: conv.to_dict() 
                        for session_id, conv in self.conversations.items()
                    },
                    "session_metrics": self.session_metrics,
                    "summary_statistics": self.get_summary_statistics(),
                    "intent_analysis": self.get_intent_analysis(),
                    "tool_effectiveness": self.get_tool_effectiveness(),
                    "export_timestamp": datetime.now().isoformat()
                }
                
                export_file = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(export_file, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                print(f"📤 [ANALYTICS] Analytics exported to {export_file}")
                return export_file
            else:
                print(f"❌ [ANALYTICS] Unsupported export format: {format}")
                return ""
                
        except Exception as e:
            print(f"❌ [ANALYTICS] Error exporting analytics: {e}")
            logger.error(f"Error exporting analytics: {e}")
            return ""
    
    def clear_analytics(self) -> None:
        """Clear all analytics data."""
        print(f"🧹 [ANALYTICS] Clearing all analytics data...")
        
        try:
            self.conversations.clear()
            self.session_metrics.clear()
            
            # Remove data file if it exists
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
                print(f"🧹 [ANALYTICS] Removed data file: {self.data_file}")
            
            print(f"✅ [ANALYTICS] All analytics data cleared successfully")
            logger.info("Analytics data cleared")
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error clearing analytics data: {e}")
            logger.error(f"Error clearing analytics data: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a comprehensive analytics summary."""
        print(f"📊 [ANALYTICS] Generating comprehensive analytics summary...")
        
        try:
            summary = {
                "data_overview": {
                    "total_conversations": len(self.conversations),
                    "total_sessions": len(self.session_metrics),
                    "data_file": self.data_file,
                    "last_updated": datetime.now().isoformat()
                },
                "summary_statistics": self.get_summary_statistics(),
                "intent_analysis": self.get_intent_analysis(),
                "tool_effectiveness": self.get_tool_effectiveness(),
                "quality_trends": self.get_quality_trends(days=7)  # Last 7 days
            }
            
            print(f"📊 [ANALYTICS] Comprehensive summary generated with {len(summary)} sections")
            return summary
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Error generating analytics summary: {e}")
            logger.error(f"Error generating analytics summary: {e}")
            return {"error": f"Failed to generate analytics summary: {str(e)}"}
