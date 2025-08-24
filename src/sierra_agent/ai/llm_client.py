"""
LLM Client - OpenAI API Integration

This module provides the interface to OpenAI's language models for intent
classification, sentiment analysis, and response generation with usage tracking.
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

from ..data.data_types import IntentType, SentimentType
from ..utils.branding import Branding
from ..utils.error_messages import ErrorMessages

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Track API usage and costs."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    api_calls: int = 0
    
    def update_from_response(self, response: Dict[str, Any]) -> None:
        """Update stats from API response."""
        usage = response.get('usage', {})
        self.prompt_tokens += usage.get('prompt_tokens', 0)
        self.completion_tokens += usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        self.api_calls += 1
        
        # Estimate cost (approximate rates for GPT-4)
        cost_per_1k_tokens = 0.03  # $0.03 per 1K tokens (approximate)
        self.total_cost += (total_tokens / 1000) * cost_per_1k_tokens


class LLMClient:
    """Client for interacting with OpenAI's language models."""
    
    def __init__(self, model_name: str = "gpt-4o", max_tokens: int = 1000) -> None:
        print(f"🤖 [LLM_CLIENT] Initializing LLM client...")
        print(f"🤖 [LLM_CLIENT] Model: {model_name}, Max tokens: {max_tokens}")
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        
        # Get API key from environment
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            print(f"✅ [LLM_CLIENT] OpenAI API key found")
            try:
                self.client = OpenAI(api_key=self.api_key)
                print(f"✅ [LLM_CLIENT] OpenAI client configured")
            except ImportError:
                print(f"⚠️ [LLM_CLIENT] OpenAI package not installed, using mock mode")
                self.api_key = None
                self.client = None
        else:
            print(f"⚠️ [LLM_CLIENT] No OpenAI API key found, using mock mode")
            self.client = None
        
        # Initialize usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "requests_by_model": {},
            "last_request": None
        }
        print(f"📊 [LLM_CLIENT] Usage tracking initialized")
        
        print(f"✅ [LLM_CLIENT] LLM client initialized successfully")
        logger.info(f"LLMClient initialized with model {model_name}")
    
    def classify_intent(self, user_input: str) -> IntentType:
        """Classify the user's intent from their input."""
        print(f"🧠 [LLM_CLIENT] Classifying intent for: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")
        
        try:
            if self.api_key:
                print(f"🧠 [LLM_CLIENT] Using OpenAI API for intent classification")
                intent = self._classify_intent_with_openai(user_input)
            else:
                print(f"🧠 [LLM_CLIENT] Using mock intent classification")
                intent = self._classify_intent_mock(user_input)
            
            print(f"✅ [LLM_CLIENT] Intent classified as: {intent}")
            self._update_usage_stats("intent_classification")
            return intent
            
        except Exception as e:
            print(f"❌ [LLM_CLIENT] Error classifying intent: {e}")
            logger.error(f"Error classifying intent: {e}")
            
            # Fallback to mock classification
            print(f"🔄 [LLM_CLIENT] Falling back to mock classification")
            return self._classify_intent_mock(user_input)
    
    def analyze_sentiment(self, user_input: str) -> SentimentType:
        """Analyze the sentiment of the user's input."""
        print(f"😊 [LLM_CLIENT] Analyzing sentiment for: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")
        
        try:
            if self.api_key:
                print(f"😊 [LLM_CLIENT] Using OpenAI API for sentiment analysis")
                sentiment = self._analyze_sentiment_with_openai(user_input)
            else:
                print(f"😊 [LLM_CLIENT] Using mock sentiment analysis")
                sentiment = self._analyze_sentiment_mock(user_input)
            
            print(f"✅ [LLM_CLIENT] Sentiment analyzed as: {sentiment}")
            self._update_usage_stats("sentiment_analysis")
            return sentiment
            
        except Exception as e:
            print(f"❌ [LLM_CLIENT] Error analyzing sentiment: {e}")
            logger.error(f"Error analyzing sentiment: {e}")
            
            # Fallback to mock analysis
            print(f"🔄 [LLM_CLIENT] Falling back to mock sentiment analysis")
            return self._analyze_sentiment_mock(user_input)
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the given context."""
        print(f"💬 [LLM_CLIENT] Generating response with context: {len(context)} elements")
        print(f"💬 [LLM_CLIENT] Context keys: {list(context.keys())}")
        
        try:
            if self.api_key:
                print(f"💬 [LLM_CLIENT] Using OpenAI API for response generation")
                response = self._generate_response_with_openai(context)
            else:
                print(f"💬 [LLM_CLIENT] Using mock response generation")
                response = self._generate_response_mock(context)
            
            print(f"✅ [LLM_CLIENT] Response generated: '{response[:50]}{'...' if len(response) > 50 else ''}'")
            self._update_usage_stats("response_generation")
            return response
            
        except Exception as e:
            print(f"❌ [LLM_CLIENT] Error generating response: {e}")
            logger.error(f"Error generating response: {e}")
            
            # Fallback to mock response
            print(f"🔄 [LLM_CLIENT] Falling back to mock response generation")
            return self._generate_response_mock(context)
    
    def _classify_intent_with_openai(self, user_input: str) -> IntentType:
        """Classify intent using OpenAI API."""
        print(f"🌐 [LLM_CLIENT] Sending intent classification request to OpenAI...")
        
        try:
            prompt = f"""
            Classify the customer's intent from the following message. Choose from these categories:
            - ORDER_STATUS: Questions about order tracking, shipping, delivery
            - PRODUCT_INQUIRY: Questions about products, recommendations, availability
            - CUSTOMER_SERVICE: General customer service, policies, company info
            - COMPLAINT: Complaints, issues, problems
            - RETURN_REQUEST: Returns, refunds, exchanges
            - SHIPPING_INFO: Shipping options, costs, tracking
            - PROMOTION_INQUIRY: Sales, discounts, promotions
            
            Customer message: "{user_input}"
            
            Respond with only the intent category (e.g., ORDER_STATUS):
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            intent_text = response.choices[0].message.content.strip().upper()
            print(f"🌐 [LLM_CLIENT] OpenAI response: {intent_text}")
            
            # Map response to IntentType
            intent_mapping = {
                "ORDER_STATUS": IntentType.ORDER_STATUS,
                "PRODUCT_INQUIRY": IntentType.PRODUCT_INQUIRY,
                "CUSTOMER_SERVICE": IntentType.CUSTOMER_SERVICE,
                "COMPLAINT": IntentType.COMPLAINT,
                "RETURN_REQUEST": IntentType.RETURN_REQUEST,
                "SHIPPING_INFO": IntentType.SHIPPING_INFO,
                "PROMOTION_INQUIRY": IntentType.PROMOTION_INQUIRY
            }
            
            if intent_text in intent_mapping:
                return intent_mapping[intent_text]
            else:
                print(f"⚠️ [LLM_CLIENT] Unknown intent from OpenAI: {intent_text}, defaulting to CUSTOMER_SERVICE")
                return IntentType.CUSTOMER_SERVICE
                
        except Exception as e:
            print(f"❌ [LLM_CLIENT] OpenAI API error: {e}")
            raise
    
    def _classify_intent_mock(self, user_input: str) -> IntentType:
        """Mock intent classification for testing."""
        print(f"🎭 [LLM_CLIENT] Performing mock intent classification...")
        
        user_input_lower = user_input.lower()
        
        # Simple keyword-based classification
        if any(word in user_input_lower for word in ["order", "tracking", "shipping", "delivery"]):
            intent = IntentType.ORDER_STATUS
            print(f"🎭 [LLM_CLIENT] Mock classified as ORDER_STATUS (order-related keywords)")
        elif any(word in user_input_lower for word in ["product", "hiking", "camping", "boots", "tent", "backpack"]):
            intent = IntentType.PRODUCT_INQUIRY
            print(f"🎭 [LLM_CLIENT] Mock classified as PRODUCT_INQUIRY (product-related keywords)")
        elif any(word in user_input_lower for word in ["return", "refund", "exchange"]):
            intent = IntentType.RETURN_REQUEST
            print(f"🎭 [LLM_CLIENT] Mock classified as RETURN_REQUEST (return-related keywords)")
        elif any(word in user_input_lower for word in ["complaint", "problem", "issue", "broken", "wrong"]):
            intent = IntentType.COMPLAINT
            print(f"🎭 [LLM_CLIENT] Mock classified as COMPLAINT (complaint-related keywords)")
        elif any(word in user_input_lower for word in ["shipping", "delivery", "tracking"]):
            intent = IntentType.SHIPPING_INFO
            print(f"🎭 [LLM_CLIENT] Mock classified as SHIPPING_INFO (shipping-related keywords)")
        elif any(word in user_input_lower for word in ["sale", "discount", "promotion", "deal"]):
            intent = IntentType.PROMOTION_INQUIRY
            print(f"🎭 [LLM_CLIENT] Mock classified as PROMOTION_INQUIRY (promotion-related keywords)")
        else:
            intent = IntentType.CUSTOMER_SERVICE
            print(f"🎭 [LLM_CLIENT] Mock classified as CUSTOMER_SERVICE (default)")
        
        return intent
    
    def _analyze_sentiment_with_openai(self, user_input: str) -> SentimentType:
        """Analyze sentiment using OpenAI API."""
        print(f"🌐 [LLM_CLIENT] Sending sentiment analysis request to OpenAI...")
        
        try:
            prompt = f"""
            Analyze the sentiment of the following customer message. Choose from:
            - POSITIVE: Happy, satisfied, excited, grateful
            - NEUTRAL: Factual, informational, neither positive nor negative
            - NEGATIVE: Angry, frustrated, disappointed, upset
            
            Customer message: "{user_input}"
            
            Respond with only the sentiment (e.g., POSITIVE):
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            
            sentiment_text = response.choices[0].message.content.strip().upper()
            print(f"🌐 [LLM_CLIENT] OpenAI sentiment response: {sentiment_text}")
            
            # Map response to SentimentType
            sentiment_mapping = {
                "POSITIVE": SentimentType.POSITIVE,
                "NEUTRAL": SentimentType.NEUTRAL,
                "NEGATIVE": SentimentType.NEGATIVE
            }
            
            if sentiment_text in sentiment_mapping:
                return sentiment_mapping[sentiment_text]
            else:
                print(f"⚠️ [LLM_CLIENT] Unknown sentiment from OpenAI: {sentiment_text}, defaulting to NEUTRAL")
                return SentimentType.NEUTRAL
                
        except Exception as e:
            print(f"❌ [LLM_CLIENT] OpenAI API error: {e}")
            raise
    
    def _analyze_sentiment_mock(self, user_input: str) -> SentimentType:
        """Mock sentiment analysis for testing."""
        print(f"🎭 [LLM_CLIENT] Performing mock sentiment analysis...")
        
        user_input_lower = user_input.lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = ["thank", "thanks", "great", "awesome", "love", "perfect", "excellent", "happy", "satisfied"]
        negative_words = ["angry", "frustrated", "disappointed", "upset", "terrible", "awful", "hate", "problem", "issue", "broken"]
        
        positive_count = sum(1 for word in positive_words if word in user_input_lower)
        negative_count = sum(1 for word in negative_words if word in user_input_lower)
        
        if positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            print(f"🎭 [LLM_CLIENT] Mock analyzed as POSITIVE ({positive_count} positive keywords)")
        elif negative_count > positive_count:
            sentiment = SentimentType.NEGATIVE
            print(f"🎭 [LLM_CLIENT] Mock analyzed as NEGATIVE ({negative_count} negative keywords)")
        else:
            sentiment = SentimentType.NEUTRAL
            print(f"🎭 [LLM_CLIENT] Mock analyzed as NEUTRAL (balanced keywords)")
        
        return sentiment
    
    def _generate_response_with_openai(self, context: Dict[str, Any]) -> str:
        """Generate response using OpenAI API."""
        print(f"🌐 [LLM_CLIENT] Sending response generation request to OpenAI...")
        
        try:
            # Build prompt from context
            prompt = self._build_response_prompt(context)
            print(f"🌐 [LLM_CLIENT] Built prompt with {len(prompt)} characters")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            generated_response = response.choices[0].message.content.strip()
            print(f"🌐 [LLM_CLIENT] OpenAI generated response: {len(generated_response)} characters")
            
            return generated_response
            
        except Exception as e:
            print(f"❌ [LLM_CLIENT] OpenAI API error: {e}")
            raise
    
    def _generate_response_mock(self, context: Dict[str, Any]) -> str:
        """Mock response generation for testing."""
        print(f"🎭 [LLM_CLIENT] Performing mock response generation...")
        
        user_input = context.get("user_input", "")
        intent = context.get("intent", "customer_service")
        sentiment = context.get("sentiment", "neutral")
        
        print(f"🎭 [LLM_CLIENT] Mock context - Intent: {intent}, Sentiment: {sentiment}")
        
        # Generate appropriate mock response based on intent
        if intent == "order_status":
            response = "I'd be happy to help you with your order. Could you please provide your order number?"
        elif intent == "product_inquiry":
            response = "I'd be happy to help you find the perfect outdoor gear. What are you looking for?"
        elif intent == "return_request":
            response = "I understand you'd like to make a return. Let me help you with that process."
        elif intent == "complaint":
            response = "I'm sorry to hear you're experiencing an issue. Let me help resolve this for you."
        elif intent == "shipping_info":
            response = "I can help you with shipping information. What would you like to know?"
        elif intent == "promotion_inquiry":
            response = "Great question about our promotions! Let me check what's currently available."
        else:
            response = "Thank you for contacting Sierra Outfitters. How can I assist you today?"
        
        # Adjust response based on sentiment
        if sentiment == "positive":
            response = "I'm glad to help! " + response
        elif sentiment == "negative":
            response = "I understand your concern. " + response
        
        print(f"🎭 [LLM_CLIENT] Mock response generated: '{response[:50]}{'...' if len(response) > 50 else ''}'")
        return response
    
    def _build_response_prompt(self, context: Dict[str, Any]) -> str:
        """Build a prompt for response generation from context."""
        print(f"📝 [LLM_CLIENT] Building response prompt from context...")
        
        user_input = context.get("user_input", "")
        intent = context.get("intent", "customer_service")
        sentiment = context.get("sentiment", "neutral")
        tool_results = context.get("tool_results", {})
        conversation_history = context.get("conversation_history", [])
        
        prompt = f"""
        You are a helpful customer service agent for Sierra Outfitters, a premium outdoor gear retailer.
        
        Customer's message: "{user_input}"
        Detected intent: {intent}
        Customer sentiment: {sentiment}
        
        Available business data: {tool_results}
        
        Conversation history: {conversation_history}
        
        Please provide a helpful, professional response that:
        1. Addresses the customer's specific request
        2. Uses the available business data when relevant
        3. Maintains a tone appropriate for the customer's sentiment
        4. Is concise but informative
        5. Reflects Sierra Outfitters' brand values of quality, adventure, and customer service
        
        Response:
        """
        
        print(f"📝 [LLM_CLIENT] Prompt built with {len(prompt)} characters")
        return prompt
    
    def _update_usage_stats(self, request_type: str) -> None:
        """Update usage statistics."""
        print(f"📊 [LLM_CLIENT] Updating usage stats for: {request_type}")
        
        self.usage_stats["total_requests"] += 1
        self.usage_stats["last_request"] = datetime.now().isoformat()
        
        if request_type not in self.usage_stats["requests_by_model"]:
            self.usage_stats["requests_by_model"][request_type] = 0
        self.usage_stats["requests_by_model"][request_type] += 1
        
        print(f"📊 [LLM_CLIENT] Usage stats updated: {self.usage_stats['total_requests']} total requests")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        print(f"📊 [LLM_CLIENT] Retrieving usage statistics...")
        
        stats = self.usage_stats.copy()
        stats["model_name"] = self.model_name
        stats["max_tokens"] = self.max_tokens
        stats["has_api_key"] = bool(self.api_key)
        
        print(f"📊 [LLM_CLIENT] Usage stats retrieved: {stats['total_requests']} total requests")
        return stats
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        print(f"🔄 [LLM_CLIENT] Resetting usage statistics...")
        
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "requests_by_model": {},
            "last_request": None
        }
        
        print(f"✅ [LLM_CLIENT] Usage statistics reset")
    
    def change_model(self, new_model: str) -> None:
        """Change the model being used."""
        print(f"🔄 [LLM_CLIENT] Changing model from {self.model_name} to {new_model}")
        
        self.model_name = new_model
        print(f"✅ [LLM_CLIENT] Model changed to: {new_model}")
        logger.info(f"LLM model changed to {new_model}")
    
    def is_available(self) -> bool:
        """Check if the LLM client is available and configured."""
        available = bool(self.api_key)
        print(f"🔍 [LLM_CLIENT] Client availability check: {'Available' if available else 'Not available'}")
        return available
