"""
Sentiment Agent for analyzing social media sentiment from financial creators.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from tools.sentiment_tool import analyze_profiles_sentiment

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAgent:
    """Agent responsible for social media sentiment analysis."""
    
    def __init__(self):
        """Initialize Sentiment Agent."""
        self.agent_name = "Sentiment Analyst"
        self.description = "Specialized agent for analyzing social media sentiment from financial creators"
        logger.info(f"Initialized {self.agent_name}")
    
    def run(self, profile_list: List[str], symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment from social posts for specified profile list.
        
        Args:
            profile_list: List of social media usernames/handles
            symbols: Optional list of stock symbols to filter content
        
        Returns:
            Dictionary containing sentiment analysis results and insights
        """
        logger.info(f"Sentiment Agent analyzing {len(profile_list)} profiles")
        if symbols:
            logger.info(f"Filtering for symbols: {', '.join(symbols)}")
        
        try:
            # Perform sentiment analysis
            sentiment_results = analyze_profiles_sentiment(profile_list, symbols)
            
            # Generate additional insights
            insights = self._generate_sentiment_insights(sentiment_results, symbols)
            
            # Assess market implications
            market_assessment = self._assess_market_implications(sentiment_results, insights)
            
            # Prepare agent results
            results = {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'profiles_analyzed': profile_list,
                'symbols_filter': symbols or [],
                'raw_sentiment': sentiment_results,
                'insights': insights,
                'market_assessment': market_assessment,
                'recommendations': self._generate_recommendations(sentiment_results, insights),
                'status': 'success'
            }
            
            overall_sentiment = sentiment_results.get('overall_sentiment', {})
            logger.info(f"Sentiment Agent completed: Overall sentiment is {overall_sentiment.get('sentiment', 'unknown')} "
                       f"(score: {overall_sentiment.get('score', 0):.2f})")
            
            return results
            
        except Exception as e:
            logger.error(f"Sentiment Agent error: {e}")
            return {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'profiles_analyzed': profile_list,
                'symbols_filter': symbols or [],
                'error': str(e),
                'status': 'error'
            }
    
    def _generate_sentiment_insights(self, sentiment_results: Dict[str, Any], 
                                   symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate deeper insights from sentiment analysis."""
        
        insights = {
            'sentiment_strength': 'weak',
            'consensus_level': 'low',
            'influencer_alignment': 'mixed',
            'sentiment_momentum': 'neutral',
            'key_themes': [],
            'outlier_profiles': [],
            'symbol_specific_sentiment': {}
        }
        
        try:
            overall = sentiment_results.get('overall_sentiment', {})
            profile_results = sentiment_results.get('profile_results', {})
            
            # Assess sentiment strength
            overall_score = abs(overall.get('score', 0))
            if overall_score > 0.6:
                insights['sentiment_strength'] = 'strong'
            elif overall_score > 0.3:
                insights['sentiment_strength'] = 'moderate'
            else:
                insights['sentiment_strength'] = 'weak'
            
            # Assess consensus level
            if profile_results:
                valid_profiles = [p for p in profile_results.values() if 'error' not in p and 'average_sentiment' in p]
                if valid_profiles:
                    sentiments = [p['average_sentiment']['sentiment'] for p in valid_profiles]
                    most_common_sentiment = max(set(sentiments), key=sentiments.count)
                    consensus_ratio = sentiments.count(most_common_sentiment) / len(sentiments)
                    
                    if consensus_ratio > 0.8:
                        insights['consensus_level'] = 'high'
                    elif consensus_ratio > 0.6:
                        insights['consensus_level'] = 'moderate'
                    else:
                        insights['consensus_level'] = 'low'
                    
                    insights['consensus_sentiment'] = most_common_sentiment
                    insights['consensus_ratio'] = round(consensus_ratio, 2)
            
            # Identify influencer alignment patterns
            positive_profiles = []
            negative_profiles = []
            neutral_profiles = []
            
            for profile, data in profile_results.items():
                if 'error' not in data and 'average_sentiment' in data:
                    sentiment = data['average_sentiment']['sentiment']
                    score = data['average_sentiment']['score']
                    
                    if sentiment == 'positive':
                        positive_profiles.append((profile, score))
                    elif sentiment == 'negative':
                        negative_profiles.append((profile, score))
                    else:
                        neutral_profiles.append((profile, score))
            
            # Determine alignment
            total_profiles = len(positive_profiles) + len(negative_profiles) + len(neutral_profiles)
            if total_profiles > 0:
                positive_ratio = len(positive_profiles) / total_profiles
                if positive_ratio > 0.7:
                    insights['influencer_alignment'] = 'strongly_positive'
                elif positive_ratio > 0.5:
                    insights['influencer_alignment'] = 'moderately_positive'
                elif positive_ratio < 0.3:
                    insights['influencer_alignment'] = 'negative_leaning'
                else:
                    insights['influencer_alignment'] = 'mixed'
            
            # Identify outlier profiles (significantly different from consensus)
            if valid_profiles and len(valid_profiles) > 2:
                scores = [p['average_sentiment']['score'] for p in valid_profiles]
                avg_score = sum(scores) / len(scores)
                
                for profile, data in profile_results.items():
                    if 'error' not in data and 'average_sentiment' in data:
                        profile_score = data['average_sentiment']['score']
                        if abs(profile_score - avg_score) > 0.5:  # Significant deviation
                            insights['outlier_profiles'].append({
                                'profile': profile,
                                'score': profile_score,
                                'deviation': round(profile_score - avg_score, 2),
                                'type': 'positive_outlier' if profile_score > avg_score else 'negative_outlier'
                            })
            
            # Extract key themes (simplified - in production would use NLP)
            insights['key_themes'] = self._extract_key_themes(sentiment_results)
            
            # Symbol-specific sentiment if symbols provided
            if symbols:
                insights['symbol_specific_sentiment'] = self._analyze_symbol_sentiment(
                    sentiment_results, symbols
                )
            
        except Exception as e:
            logger.warning(f"Error generating sentiment insights: {e}")
            insights['insight_error'] = str(e)
        
        return insights
    
    def _extract_key_themes(self, sentiment_results: Dict[str, Any]) -> List[str]:
        """Extract key themes from sentiment analysis (simplified version)."""
        
        themes = []
        
        try:
            overall = sentiment_results.get('overall_sentiment', {})
            
            # Theme detection based on sentiment patterns
            if overall.get('sentiment') == 'positive':
                themes.extend(['bullish_outlook', 'growth_optimism'])
            elif overall.get('sentiment') == 'negative':
                themes.extend(['bearish_concerns', 'risk_aversion'])
            
            # Theme detection based on profile distribution
            profile_results = sentiment_results.get('profile_results', {})
            positive_count = sum(1 for p in profile_results.values() 
                               if 'average_sentiment' in p and p['average_sentiment']['sentiment'] == 'positive')
            negative_count = sum(1 for p in profile_results.values() 
                               if 'average_sentiment' in p and p['average_sentiment']['sentiment'] == 'negative')
            
            if positive_count > negative_count * 2:
                themes.append('strong_consensus_bullish')
            elif negative_count > positive_count * 2:
                themes.append('strong_consensus_bearish')
            else:
                themes.append('mixed_sentiment_signals')
            
            # Activity level themes
            total_posts = overall.get('total_posts', 0)
            if total_posts > 50:
                themes.append('high_engagement')
            elif total_posts < 20:
                themes.append('low_engagement')
            
        except Exception as e:
            logger.warning(f"Error extracting themes: {e}")
        
        return list(set(themes))  # Remove duplicates
    
    def _analyze_symbol_sentiment(self, sentiment_results: Dict[str, Any], 
                                 symbols: List[str]) -> Dict[str, Any]:
        """Analyze sentiment for specific symbols (simplified version)."""
        
        symbol_sentiment = {}
        
        try:
            # In a full implementation, this would analyze post content for symbol mentions
            # For now, we'll provide a simplified analysis based on overall sentiment
            
            overall = sentiment_results.get('overall_sentiment', {})
            overall_score = overall.get('score', 0)
            overall_sentiment = overall.get('sentiment', 'neutral')
            
            for symbol in symbols:
                # Simplified symbol sentiment (would be more sophisticated in production)
                symbol_sentiment[symbol] = {
                    'sentiment': overall_sentiment,
                    'score': overall_score,
                    'confidence': 0.6,  # Medium confidence for simplified analysis
                    'mention_frequency': 'estimated',
                    'key_points': [
                        f"Overall creator sentiment is {overall_sentiment}",
                        f"Sentiment score: {overall_score:.2f}"
                    ]
                }
        
        except Exception as e:
            logger.warning(f"Error analyzing symbol sentiment: {e}")
        
        return symbol_sentiment
    
    def _assess_market_implications(self, sentiment_results: Dict[str, Any], 
                                  insights: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market implications of sentiment analysis."""
        
        market_assessment = {
            'market_mood': 'neutral',
            'potential_impact': 'low',
            'risk_level': 'medium',
            'trading_implications': [],
            'catalyst_potential': 'low',
            'crowd_wisdom_signals': []
        }
        
        try:
            overall = sentiment_results.get('overall_sentiment', {})
            overall_score = overall.get('score', 0)
            consensus_level = insights.get('consensus_level', 'low')
            sentiment_strength = insights.get('sentiment_strength', 'weak')
            
            # Assess market mood
            if overall_score > 0.3:
                market_assessment['market_mood'] = 'optimistic'
            elif overall_score < -0.3:
                market_assessment['market_mood'] = 'pessimistic'
            else:
                market_assessment['market_mood'] = 'neutral'
            
            # Assess potential impact
            if sentiment_strength == 'strong' and consensus_level == 'high':
                market_assessment['potential_impact'] = 'high'
            elif sentiment_strength in ['strong', 'moderate'] or consensus_level in ['high', 'moderate']:
                market_assessment['potential_impact'] = 'medium'
            else:
                market_assessment['potential_impact'] = 'low'
            
            # Assess risk level
            if insights.get('influencer_alignment') == 'mixed' and consensus_level == 'low':
                market_assessment['risk_level'] = 'high'
            elif sentiment_strength == 'strong' and consensus_level == 'high':
                market_assessment['risk_level'] = 'low'
            else:
                market_assessment['risk_level'] = 'medium'
            
            # Generate trading implications
            if overall_score > 0.4 and consensus_level == 'high':
                market_assessment['trading_implications'].append('Strong bullish sentiment may drive buying pressure')
            elif overall_score < -0.4 and consensus_level == 'high':
                market_assessment['trading_implications'].append('Strong bearish sentiment may increase selling pressure')
            
            if insights.get('influencer_alignment') == 'mixed':
                market_assessment['trading_implications'].append('Mixed signals suggest increased volatility potential')
            
            # Assess catalyst potential
            profiles_analyzed = overall.get('profiles_analyzed', 0)
            total_posts = overall.get('total_posts', 0)
            
            if profiles_analyzed > 8 and total_posts > 40 and sentiment_strength == 'strong':
                market_assessment['catalyst_potential'] = 'high'
            elif profiles_analyzed > 5 and total_posts > 20:
                market_assessment['catalyst_potential'] = 'medium'
            else:
                market_assessment['catalyst_potential'] = 'low'
            
            # Generate crowd wisdom signals
            if consensus_level == 'high' and sentiment_strength == 'strong':
                market_assessment['crowd_wisdom_signals'].append('Strong consensus detected')
            
            if len(insights.get('outlier_profiles', [])) > 0:
                market_assessment['crowd_wisdom_signals'].append('Contrarian voices identified')
            
            if 'high_engagement' in insights.get('key_themes', []):
                market_assessment['crowd_wisdom_signals'].append('High community engagement')
            
        except Exception as e:
            logger.warning(f"Error assessing market implications: {e}")
            market_assessment['assessment_error'] = str(e)
        
        return market_assessment
    
    def _generate_recommendations(self, sentiment_results: Dict[str, Any], 
                                insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations based on sentiment analysis."""
        
        recommendations = {
            'immediate_actions': [],
            'monitoring_priorities': [],
            'risk_management': [],
            'opportunity_areas': [],
            'confidence_level': 'medium'
        }
        
        try:
            overall = sentiment_results.get('overall_sentiment', {})
            overall_score = overall.get('score', 0)
            consensus_level = insights.get('consensus_level', 'low')
            sentiment_strength = insights.get('sentiment_strength', 'weak')
            
            # Immediate actions
            if sentiment_strength == 'strong':
                if overall_score > 0.4:
                    recommendations['immediate_actions'].append(
                        'Consider the strong positive sentiment in investment decisions'
                    )
                elif overall_score < -0.4:
                    recommendations['immediate_actions'].append(
                        'Exercise caution due to strong negative sentiment'
                    )
            
            if consensus_level == 'low':
                recommendations['immediate_actions'].append(
                    'Monitor for sentiment convergence or divergence'
                )
            
            # Monitoring priorities
            recommendations['monitoring_priorities'].append('Track sentiment momentum changes')
            
            if len(insights.get('outlier_profiles', [])) > 0:
                recommendations['monitoring_priorities'].append(
                    'Monitor outlier influencer opinions for potential trend shifts'
                )
            
            # Risk management
            if insights.get('influencer_alignment') == 'mixed':
                recommendations['risk_management'].append(
                    'Prepare for increased volatility due to mixed sentiment signals'
                )
            
            if consensus_level == 'low':
                recommendations['risk_management'].append(
                    'Reduce position sizes due to uncertain sentiment direction'
                )
            
            # Opportunity areas
            if overall_score > 0.3 and consensus_level == 'high':
                recommendations['opportunity_areas'].append(
                    'Strong positive consensus may indicate buying opportunities'
                )
            
            if 'high_engagement' in insights.get('key_themes', []):
                recommendations['opportunity_areas'].append(
                    'High engagement suggests increased market attention and potential catalysts'
                )
            
            # Set confidence level
            if sentiment_strength == 'strong' and consensus_level == 'high':
                recommendations['confidence_level'] = 'high'
            elif sentiment_strength == 'weak' or consensus_level == 'low':
                recommendations['confidence_level'] = 'low'
            else:
                recommendations['confidence_level'] = 'medium'
            
        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")
            recommendations['recommendation_error'] = str(e)
        
        return recommendations
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities."""
        return {
            'agent_name': self.agent_name,
            'status': 'ready',
            'capabilities': [
                'Social media sentiment analysis',
                'Multi-profile sentiment tracking',
                'Consensus analysis',
                'Market implication assessment',
                'Symbol-specific sentiment filtering'
            ],
            'data_sources': [
                'Twitter/X posts',
                'Financial creator content',
                'Social media APIs'
            ],
            'analysis_types': [
                'overall_sentiment',
                'consensus_analysis',
                'influencer_alignment',
                'market_implications',
                'trading_recommendations'
            ],
            'output_formats': ['sentiment_scores', 'insights', 'recommendations']
        }

if __name__ == "__main__":
    # Test the Sentiment agent
    agent = SentimentAgent()
    
    # Test with sample profiles
    test_profiles = ["@elonmusk", "@chamath", "@cathiedwood", "@jimcramer"]
    test_symbols = ["TSLA", "AAPL", "NVDA"]
    
    results = agent.run(test_profiles, test_symbols)
    
    print(f"Agent Status: {results.get('status')}")
    print(f"Overall Sentiment: {results.get('raw_sentiment', {}).get('overall_sentiment', {}).get('sentiment', 'unknown')}")
    print(f"Market Assessment: {results.get('market_assessment', {}).get('market_mood', 'unknown')}")
    print(f"Confidence Level: {results.get('recommendations', {}).get('confidence_level', 'unknown')}")
