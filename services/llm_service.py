"""
LLM service for sentiment analysis using OpenRouter API.
Provides advanced sentiment analysis with reasoning and confidence scoring.
"""
import os
import requests
import json
import logging
from typing import Dict, Any, Optional
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('configs/.env')

logger = logging.getLogger(__name__)

class LLMSentimentService:
    """Service for LLM-powered sentiment analysis."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model = os.getenv('SENTIMENT_LLM_MODEL', 'meta-llama/llama-3.1-8b-instruct:free')
        self.temperature = float(os.getenv('SENTIMENT_LLM_TEMPERATURE', '0.3'))
        self.max_tokens = int(os.getenv('SENTIMENT_MAX_TOKENS', '500'))
        
        if not self.api_key:
            logger.warning("No OpenRouter API key found. LLM sentiment analysis disabled.")
            
        self.last_request_time = 0
        self.min_request_interval = 1  # seconds between requests
        
    def _rate_limit(self):
        """Simple rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def analyze_sentiment(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze sentiment using LLM with financial context awareness.
        
        Args:
            text: Text to analyze
            context: Additional context (profile, symbols, etc.)
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.api_key:
            return self._fallback_sentiment(text)
        
        try:
            self._rate_limit()
            
            # Build context-aware prompt
            prompt = self._build_sentiment_prompt(text, context)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/wildcraft958/CrowdWisdomTrading_AI_Agent',
                'X-Title': 'CrowdWisdom Trading AI'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '''You are an expert financial sentiment analyst. Analyze text for trading and investment sentiment with high accuracy. 

Response format (JSON only):
{
    "sentiment": "positive|negative|neutral",
    "score": float between -1.0 and 1.0,
    "confidence": float between 0.0 and 1.0,
    "reasoning": "brief explanation",
    "financial_relevance": float between 0.0 and 1.0,
    "key_indicators": ["list", "of", "key", "sentiment", "words"]
}'''
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
                'top_p': 0.9
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    sentiment_data = json.loads(content)
                    return self._validate_sentiment_response(sentiment_data, text)
                except json.JSONDecodeError:
                    logger.warning("LLM returned invalid JSON, parsing manually")
                    return self._parse_llm_response(content, text)
            else:
                logger.warning(f"LLM API error: {response.status_code}")
                return self._fallback_sentiment(text)
                
        except Exception as e:
            logger.warning(f"LLM sentiment analysis error: {e}")
            return self._fallback_sentiment(text)
    
    def _build_sentiment_prompt(self, text: str, context: Dict[str, Any] = None) -> str:
        """Build context-aware sentiment analysis prompt."""
        base_prompt = f"""Analyze the financial sentiment of this text:

TEXT: "{text}"
"""
        
        if context:
            if context.get('profile'):
                base_prompt += f"\nPROFILE CONTEXT: This content relates to {context['profile']}, a financial influencer."
            
            if context.get('symbols'):
                symbols_str = ', '.join(context['symbols'])
                base_prompt += f"\nSTOCK SYMBOLS: Focus on sentiment related to {symbols_str}."
            
            if context.get('source'):
                base_prompt += f"\nSOURCE: {context['source']}"
        
        base_prompt += """

Consider:
1. Financial keywords and trading terminology
2. Market sentiment indicators (bullish, bearish, neutral)
3. Confidence level based on text clarity and financial relevance
4. Overall tone towards investments/stocks/trading
5. Emotional indicators that might affect trading decisions

Provide detailed analysis in the specified JSON format."""
        
        return base_prompt
    
    def _validate_sentiment_response(self, data: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Validate and normalize LLM sentiment response."""
        try:
            # Ensure required fields exist
            sentiment = data.get('sentiment', 'neutral').lower()
            score = float(data.get('score', 0.0))
            confidence = float(data.get('confidence', 0.5))
            
            # Validate ranges
            score = max(-1.0, min(1.0, score))
            confidence = max(0.0, min(1.0, confidence))
            
            # Ensure sentiment consistency
            if sentiment not in ['positive', 'negative', 'neutral']:
                if score > 0.1:
                    sentiment = 'positive'
                elif score < -0.1:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': round(score, 3),
                'confidence': round(confidence, 3),
                'reasoning': data.get('reasoning', 'LLM sentiment analysis'),
                'financial_relevance': round(float(data.get('financial_relevance', 0.5)), 3),
                'key_indicators': data.get('key_indicators', []),
                'source': 'llm_analysis',
                'model': self.model,
                'text_length': len(original_text)
            }
            
        except Exception as e:
            logger.warning(f"Error validating LLM response: {e}")
            return self._fallback_sentiment(original_text)
    
    def _parse_llm_response(self, content: str, original_text: str) -> Dict[str, Any]:
        """Parse LLM response when JSON parsing fails."""
        try:
            content_lower = content.lower()
            
            # Extract sentiment
            if 'positive' in content_lower:
                sentiment = 'positive'
                score = 0.5
            elif 'negative' in content_lower:
                sentiment = 'negative'
                score = -0.5
            else:
                sentiment = 'neutral'
                score = 0.0
            
            # Extract confidence if mentioned
            confidence = 0.6  # default
            if 'high confidence' in content_lower:
                confidence = 0.8
            elif 'low confidence' in content_lower:
                confidence = 0.4
            
            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': confidence,
                'reasoning': content[:200] + '...' if len(content) > 200 else content,
                'financial_relevance': 0.5,
                'key_indicators': [],
                'source': 'llm_analysis_parsed',
                'model': self.model,
                'text_length': len(original_text)
            }
            
        except Exception as e:
            logger.warning(f"Error parsing LLM response: {e}")
            return self._fallback_sentiment(original_text)
    
    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword matching."""
        text_lower = text.lower()
        
        positive_keywords = [
            'bullish', 'buy', 'long', 'calls', 'moon', 'rocket', 'pump', 'rally',
            'breakout', 'surge', 'strong', 'bull', 'green', 'gains', 'profit',
            'outperform', 'upgrade', 'target', 'momentum', 'squeeze'
        ]
        
        negative_keywords = [
            'bearish', 'sell', 'short', 'puts', 'crash', 'dump', 'drop', 'fall',
            'breakdown', 'bear', 'red', 'losses', 'weak', 'correction', 'decline',
            'underperform', 'downgrade', 'resistance', 'overbought'
        ]
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(0.8, positive_count * 0.2)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = -min(0.8, negative_count * 0.2)
        else:
            sentiment = 'neutral'
            score = 0.0
        
        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'confidence': 0.4,  # Lower confidence for keyword-based analysis
            'reasoning': 'Keyword-based fallback analysis',
            'financial_relevance': 0.6 if (positive_count + negative_count) > 0 else 0.3,
            'key_indicators': [],
            'source': 'keyword_fallback',
            'model': 'keyword_matching',
            'text_length': len(text)
        }
    
    def batch_analyze_sentiment(self, texts: list, context: Dict[str, Any] = None) -> list:
        """Analyze sentiment for multiple texts efficiently."""
        results = []
        
        for text in texts:
            if isinstance(text, dict) and 'text' in text:
                # If text is a dict with additional context
                text_content = text['text']
                text_context = {**(context or {}), **{k: v for k, v in text.items() if k != 'text'}}
            else:
                text_content = str(text)
                text_context = context
            
            result = self.analyze_sentiment(text_content, text_context)
            results.append(result)
        
        return results
