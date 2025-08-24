"""
Quality Scorer

This module provides conversation quality assessment and scoring based on
various metrics including relevance, helpfulness, engagement, and resolution.
"""

import logging
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..data.data_types import QualityScore, QualityLevel
from ..core.conversation import Conversation, MessageType

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Quality metrics for conversation analysis."""
    response_time_score: float
    message_length_score: float
    sentiment_consistency_score: float
    topic_relevance_score: float
    resolution_efficiency_score: float
    overall_score: float


class QualityScorer:
    """Assesses conversation quality based on various metrics."""
    
    def __init__(self) -> None:
        print("📊 [QUALITY_SCORER] Initializing QualityScorer...")
        
        # Quality thresholds and weights
        self.response_time_threshold = 30.0  # seconds
        self.optimal_message_length = 150  # characters
        self.message_length_tolerance = 50  # characters
        
        # Scoring weights
        self.weights = {
            "response_time": 0.25,
            "message_length": 0.20,
            "sentiment_consistency": 0.20,
            "topic_relevance": 0.20,
            "resolution_efficiency": 0.15
        }
        
        print(f"📊 [QUALITY_SCORER] Response time threshold: {self.response_time_threshold}s")
        print(f"📊 [QUALITY_SCORER] Optimal message length: {self.optimal_message_length} chars")
        print(f"📊 [QUALITY_SCORER] Scoring weights: {self.weights}")
        print("📊 [QUALITY_SCORER] QualityScorer initialized successfully")
        logger.info("QualityScorer initialized")
    
    def score_conversation(self, conversation: Conversation) -> QualityScore:
        """Score the overall quality of a conversation."""
        print(f"📊 [QUALITY_SCORER] Scoring conversation quality...")
        print(f"📊 [QUALITY_SCORER] Conversation has {conversation.get_conversation_length()} messages")
        
        try:
            # Calculate individual quality metrics
            print("📊 [QUALITY_SCORER] Calculating response time score...")
            response_time_score = self._calculate_response_time_score(conversation)
            print(f"📊 [QUALITY_SCORER] Response time score: {response_time_score:.3f}")
            
            print("📊 [QUALITY_SCORER] Calculating message length score...")
            message_length_score = self._calculate_message_length_score(conversation)
            print(f"📊 [QUALITY_SCORER] Message length score: {message_length_score:.3f}")
            
            print("📊 [QUALITY_SCORER] Calculating sentiment consistency score...")
            sentiment_consistency_score = self._calculate_sentiment_consistency_score(conversation)
            print(f"📊 [QUALITY_SCORER] Sentiment consistency score: {sentiment_consistency_score:.3f}")
            
            print("📊 [QUALITY_SCORER] Calculating topic relevance score...")
            topic_relevance_score = self._calculate_topic_relevance_score(conversation)
            print(f"📊 [QUALITY_SCORER] Topic relevance score: {topic_relevance_score:.3f}")
            
            print("📊 [QUALITY_SCORER] Calculating resolution efficiency score...")
            resolution_efficiency_score = self._calculate_resolution_efficiency_score(conversation)
            print(f"📊 [QUALITY_SCORER] Resolution efficiency score: {resolution_efficiency_score:.3f}")
            
            # Calculate weighted overall score
            print("📊 [QUALITY_SCORER] Calculating weighted overall score...")
            overall_score = (
                response_time_score * self.weights["response_time"] +
                message_length_score * self.weights["message_length"] +
                sentiment_consistency_score * self.weights["sentiment_consistency"] +
                topic_relevance_score * self.weights["topic_relevance"] +
                resolution_efficiency_score * self.weights["resolution_efficiency"]
            )
            print(f"📊 [QUALITY_SCORER] Overall score: {overall_score:.3f}")
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            print(f"📊 [QUALITY_SCORER] Quality level: {quality_level.value}")
            
            # Create quality score object
            quality_score = QualityScore(
                overall_score=overall_score,
                quality_level=quality_level,
                metrics={
                    "response_time_score": response_time_score,
                    "message_length_score": message_length_score,
                    "sentiment_consistency_score": sentiment_consistency_score,
                    "topic_relevance_score": topic_relevance_score,
                    "resolution_efficiency_score": resolution_efficiency_score
                }
            )
            
            print(f"✅ [QUALITY_SCORER] Conversation quality scoring completed successfully")
            return quality_score
            
        except Exception as e:
            print(f"❌ [QUALITY_SCORER] Error scoring conversation: {e}")
            logger.error(f"Error scoring conversation: {e}")
            
            # Return default quality score on error
            return QualityScore(
                overall_score=0.5,
                quality_level=QualityLevel.AVERAGE,
                metrics={}
            )
    
    def _calculate_response_time_score(self, conversation: Conversation) -> float:
        """Calculate score based on response time consistency."""
        print(f"⏱️ [QUALITY_SCORER] Analyzing response times...")
        
        messages = conversation.get_message_history()
        if len(messages) < 2:
            print(f"⏱️ [QUALITY_SCORER] Not enough messages for response time analysis")
            return 0.5
        
        response_times = []
        user_messages = [msg for msg in messages if msg.message_type == MessageType.USER]
        ai_messages = [msg for msg in messages if msg.message_type == MessageType.AI]
        
        print(f"⏱️ [QUALITY_SCORER] Found {len(user_messages)} user messages and {len(ai_messages)} AI messages")
        
        # Calculate response times between user messages and subsequent AI responses
        for i, user_msg in enumerate(user_messages):
            if i < len(ai_messages):
                response_time = (ai_messages[i].timestamp - user_msg.timestamp).total_seconds()
                response_times.append(response_time)
                print(f"⏱️ [QUALITY_SCORER] Response {i+1}: {response_time:.1f}s")
        
        if not response_times:
            print(f"⏱️ [QUALITY_SCORER] No response times calculated")
            return 0.5
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        print(f"⏱️ [QUALITY_SCORER] Average response time: {avg_response_time:.1f}s")
        
        # Score based on threshold (lower is better)
        if avg_response_time <= self.response_time_threshold:
            score = 1.0
        else:
            # Exponential decay for longer response times
            score = math.exp(-(avg_response_time - self.response_time_threshold) / 60.0)
        
        print(f"⏱️ [QUALITY_SCORER] Response time score: {score:.3f}")
        return score
    
    def _calculate_message_length_score(self, conversation: Conversation) -> float:
        """Calculate score based on message length appropriateness."""
        print(f"📏 [QUALITY_SCORER] Analyzing message lengths...")
        
        messages = conversation.get_message_history()
        if not messages:
            print(f"📏 [QUALITY_SCORER] No messages to analyze")
            return 0.5
        
        ai_messages = [msg for msg in messages if msg.message_type == MessageType.AI]
        if not ai_messages:
            print(f"📏 [QUALITY_SCORER] No AI messages to analyze")
            return 0.5
        
        print(f"📏 [QUALITY_SCORER] Analyzing {len(ai_messages)} AI messages")
        
        # Calculate length scores for each AI message
        length_scores = []
        for i, msg in enumerate(ai_messages):
            length = len(msg.content)
            print(f"📏 [QUALITY_SCORER] Message {i+1} length: {length} chars")
            
            # Score based on distance from optimal length
            distance = abs(length - self.optimal_message_length)
            if distance <= self.message_length_tolerance:
                score = 1.0
            else:
                # Linear decay for messages outside tolerance
                score = max(0.0, 1.0 - (distance - self.message_length_tolerance) / 100.0)
            
            length_scores.append(score)
            print(f"📏 [QUALITY_SCORER] Message {i+1} length score: {score:.3f}")
        
        # Return average length score
        avg_score = sum(length_scores) / len(length_scores)
        print(f"📏 [QUALITY_SCORER] Average message length score: {avg_score:.3f}")
        return avg_score
    
    def _calculate_sentiment_consistency_score(self, conversation: Conversation) -> float:
        """Calculate score based on sentiment consistency throughout conversation."""
        print(f"😊 [QUALITY_SCORER] Analyzing sentiment consistency...")
        
        sentiment_trend = conversation.get_customer_sentiment_trend()
        if len(sentiment_trend) < 2:
            print(f"😊 [QUALITY_SCORER] Not enough sentiment data for consistency analysis")
            return 0.5
        
        print(f"😊 [QUALITY_SCORER] Analyzing {len(sentiment_trend)} sentiment entries")
        
        # Count sentiment changes
        sentiment_changes = 0
        for i in range(1, len(sentiment_trend)):
            if sentiment_trend[i] != sentiment_trend[i-1]:
                sentiment_changes += 1
                print(f"😊 [QUALITY_SCORER] Sentiment change {i}: {sentiment_trend[i-1]} -> {sentiment_trend[i]}")
        
        print(f"😊 [QUALITY_SCORER] Total sentiment changes: {sentiment_changes}")
        
        # Score based on consistency (fewer changes is better)
        max_expected_changes = len(sentiment_trend) - 1
        if max_expected_changes == 0:
            score = 1.0
        else:
            consistency_ratio = 1.0 - (sentiment_changes / max_expected_changes)
            score = max(0.0, consistency_ratio)
        
        print(f"😊 [QUALITY_SCORER] Sentiment consistency score: {score:.3f}")
        return score
    
    def _calculate_topic_relevance_score(self, conversation: Conversation) -> float:
        """Calculate score based on topic relevance and consistency."""
        print(f"🎯 [QUALITY_SCORER] Analyzing topic relevance...")
        
        messages = conversation.get_message_history()
        if len(messages) < 3:
            print(f"🎯 [QUALITY_SCORER] Not enough messages for topic analysis")
            return 0.5
        
        print(f"🎯 [QUALITY_SCORER] Analyzing {len(messages)} messages for topic relevance")
        
        # Simple topic relevance based on conversation state
        conversation_state = conversation.conversation_state
        current_topic = conversation_state.current_topic
        
        if current_topic == "general":
            print(f"🎯 [QUALITY_SCORER] General topic detected, scoring lower")
            score = 0.6
        else:
            print(f"🎯 [QUALITY_SCORER] Specific topic detected: {current_topic}")
            score = 0.9
        
        # Bonus for staying on topic (conversation phase progression)
        conversation_phase = conversation_state.conversation_phase
        if conversation_phase in ["exploration", "resolution"]:
            score += 0.1
            print(f"🎯 [QUALITY_SCORER] Bonus for conversation phase: {conversation_phase}")
        
        score = min(1.0, score)
        print(f"🎯 [QUALITY_SCORER] Topic relevance score: {score:.3f}")
        return score
    
    def _calculate_resolution_efficiency_score(self, conversation: Conversation) -> float:
        """Calculate score based on conversation resolution efficiency."""
        print(f"✅ [QUALITY_SCORER] Analyzing resolution efficiency...")
        
        conversation_state = conversation.conversation_state
        conversation_phase = conversation_state.conversation_phase
        urgency_level = conversation_state.urgency_level
        
        print(f"✅ [QUALITY_SCORER] Conversation phase: {conversation_phase}")
        print(f"✅ [QUALITY_SCORER] Urgency level: {urgency_level}")
        
        # Base score based on conversation phase
        phase_scores = {
            "greeting": 0.3,
            "exploration": 0.6,
            "resolution": 0.9,
            "closing": 1.0
        }
        
        base_score = phase_scores.get(conversation_phase, 0.5)
        print(f"✅ [QUALITY_SCORER] Base score from phase: {base_score:.3f}")
        
        # Adjust based on urgency (higher urgency should lead to faster resolution)
        urgency_adjustment = 0.0
        if urgency_level == "high" and conversation_phase in ["greeting", "exploration"]:
            urgency_adjustment = -0.2  # Penalty for not resolving urgent issues quickly
            print(f"✅ [QUALITY_SCORER] Urgency penalty applied: -0.2")
        elif urgency_level == "normal" and conversation_phase in ["resolution", "closing"]:
            urgency_adjustment = 0.1  # Bonus for resolving normal issues efficiently
            print(f"✅ [QUALITY_SCORER] Efficiency bonus applied: +0.1")
        
        final_score = max(0.0, min(1.0, base_score + urgency_adjustment))
        print(f"✅ [QUALITY_SCORER] Resolution efficiency score: {final_score:.3f}")
        return final_score
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on overall score."""
        print(f"🏆 [QUALITY_SCORER] Determining quality level for score: {score:.3f}")
        
        if score >= 0.9:
            level = QualityLevel.EXCELLENT
            print(f"🏆 [QUALITY_SCORER] Quality level: EXCELLENT")
        elif score >= 0.8:
            level = QualityLevel.GOOD
            print(f"🏆 [QUALITY_SCORER] Quality level: GOOD")
        elif score >= 0.6:
            level = QualityLevel.AVERAGE
            print(f"🏆 [QUALITY_SCORER] Quality level: AVERAGE")
        elif score >= 0.4:
            level = QualityLevel.BELOW_AVERAGE
            print(f"🏆 [QUALITY_SCORER] Quality level: BELOW_AVERAGE")
        else:
            level = QualityLevel.POOR
            print(f"🏆 [QUALITY_SCORER] Quality level: POOR")
        
        return level
    
    def get_recommendations(self, quality_score: QualityScore) -> List[str]:
        """Get improvement recommendations based on quality score."""
        print(f"💡 [QUALITY_SCORER] Generating improvement recommendations...")
        
        recommendations = []
        metrics = quality_score.metrics
        
        print(f"💡 [QUALITY_SCORER] Analyzing {len(metrics)} quality metrics")
        
        # Response time recommendations
        if metrics.get("response_time_score", 1.0) < 0.7:
            recommendations.append("Consider reducing response time to improve customer satisfaction")
            print(f"💡 [QUALITY_SCORER] Added response time recommendation")
        
        # Message length recommendations
        if metrics.get("message_length_score", 1.0) < 0.7:
            recommendations.append("Optimize message length for better readability and engagement")
            print(f"💡 [QUALITY_SCORER] Added message length recommendation")
        
        # Sentiment consistency recommendations
        if metrics.get("sentiment_consistency_score", 1.0) < 0.7:
            recommendations.append("Maintain consistent sentiment throughout the conversation")
            print(f"💡 [QUALITY_SCORER] Added sentiment consistency recommendation")
        
        # Topic relevance recommendations
        if metrics.get("topic_relevance_score", 1.0) < 0.7:
            recommendations.append("Stay focused on the main topic to improve resolution efficiency")
            print(f"💡 [QUALITY_SCORER] Added topic relevance recommendation")
        
        # Resolution efficiency recommendations
        if metrics.get("resolution_efficiency_score", 1.0) < 0.7:
            recommendations.append("Work towards faster issue resolution and conversation closure")
            print(f"💡 [QUALITY_SCORER] Added resolution efficiency recommendation")
        
        # Overall quality recommendations
        if quality_score.overall_score < 0.6:
            recommendations.append("Overall conversation quality needs improvement. Focus on customer needs and efficient resolution.")
            print(f"💡 [QUALITY_SCORER] Added overall quality recommendation")
        
        print(f"💡 [QUALITY_SCORER] Generated {len(recommendations)} recommendations")
        return recommendations
    
    def get_quality_summary(self, conversation: Conversation) -> Dict[str, Any]:
        """Get a comprehensive quality summary for a conversation."""
        print(f"📋 [QUALITY_SCORER] Generating quality summary...")
        
        try:
            quality_score = self.score_conversation(conversation)
            recommendations = self.get_recommendations(quality_score)
            
            summary = {
                "overall_score": quality_score.overall_score,
                "quality_level": quality_score.quality_level.value,
                "detailed_metrics": quality_score.metrics,
                "recommendations": recommendations,
                "conversation_stats": {
                    "total_messages": conversation.get_conversation_length(),
                    "conversation_duration": conversation.get_conversation_duration(),
                    "conversation_phase": conversation.conversation_state.conversation_phase,
                    "urgency_level": conversation.conversation_state.urgency_level
                }
            }
            
            print(f"📋 [QUALITY_SCORER] Quality summary generated with {len(summary)} sections")
            return summary
            
        except Exception as e:
            print(f"❌ [QUALITY_SCORER] Error generating quality summary: {e}")
            logger.error(f"Error generating quality summary: {e}")
            return {"error": f"Failed to generate quality summary: {str(e)}"}
