"""
LLM tool for report summarization and analysis using OpenRouter API.
"""
import os
import logging
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """LLM-powered analysis using OpenRouter API."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model = os.getenv('DEFAULT_LLM_MODEL', 'anthropic/claude-3-haiku')
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        if not self.api_key:
            logger.warning("OpenRouter API key not found. LLM features will be limited.")
    
    def summarize_report(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                        sentiment_results: Dict[str, Any]) -> str:
        """
        Generate comprehensive report summary using LLM.
        
        Args:
            sec_data: Recent SEC filing data
            history_data: Historical SEC filing data  
            sentiment_results: Social sentiment analysis results
        
        Returns:
            Comprehensive report summary
        """
        logger.info("Generating LLM-powered report summary")
        
        try:
            # Prepare data summary for LLM
            data_summary = self._prepare_data_summary(sec_data, history_data, sentiment_results)
            
            # Generate summary using LLM
            if self.api_key:
                summary = self._generate_llm_summary(data_summary)
            else:
                summary = self._generate_template_summary(data_summary)
            
            # Save summary to file
            self._save_summary(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating report summary: {e}")
            return self._generate_error_summary(str(e))
    
    def _prepare_data_summary(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                             sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured data summary for LLM processing."""
        
        # Aggregate SEC data
        recent_stats = self._aggregate_sec_stats(sec_data)
        historical_stats = self._aggregate_sec_stats(history_data)
        
        # Extract sentiment insights
        sentiment_summary = self._extract_sentiment_insights(sentiment_results)
        
        # Calculate key metrics
        metrics = self._calculate_key_metrics(recent_stats, historical_stats, sentiment_summary)
        
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'recent_activity': recent_stats,
            'historical_activity': historical_stats,
            'sentiment_analysis': sentiment_summary,
            'key_metrics': metrics,
            'symbols_analyzed': list(set(list(sec_data.keys()) + list(history_data.keys())))
        }
    
    def _aggregate_sec_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate SEC filing statistics."""
        stats = {
            'total_filings': 0,
            'buy_transactions': 0,
            'sell_transactions': 0,
            'unique_insiders': set(),
            'active_symbols': [],
            'symbol_breakdown': {}
        }
        
        for symbol, symbol_data in data.items():
            if 'error' in symbol_data:
                continue
            
            filings_count = symbol_data.get('filings_count', 0)
            stats['total_filings'] += filings_count
            
            if filings_count > 0:
                stats['active_symbols'].append(symbol)
            
            symbol_stats = {'buys': 0, 'sells': 0, 'filings': filings_count}
            
            for filing in symbol_data.get('filings', []):
                # Count unique insiders
                if 'reporting_owner' in filing and filing['reporting_owner'].get('name'):
                    stats['unique_insiders'].add(filing['reporting_owner']['name'])
                
                # Count transactions by type
                for transaction in filing.get('transactions', []):
                    acquired_disposed = transaction.get('acquired_disposed', '').upper()
                    if acquired_disposed == 'A':
                        stats['buy_transactions'] += 1
                        symbol_stats['buys'] += 1
                    elif acquired_disposed == 'D':
                        stats['sell_transactions'] += 1
                        symbol_stats['sells'] += 1
            
            stats['symbol_breakdown'][symbol] = symbol_stats
        
        # Convert set to list for JSON serialization
        stats['unique_insiders'] = list(stats['unique_insiders'])
        stats['unique_insider_count'] = len(stats['unique_insiders'])
        
        return stats
    
    def _extract_sentiment_insights(self, sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from sentiment analysis."""
        
        overall = sentiment_results.get('overall_sentiment', {})
        profile_results = sentiment_results.get('profile_results', {})
        
        insights = {
            'overall_score': overall.get('score', 0),
            'overall_sentiment': overall.get('sentiment', 'neutral'),
            'profiles_analyzed': overall.get('profiles_analyzed', 0),
            'total_posts': overall.get('total_posts', 0),
            'positive_profiles': 0,
            'negative_profiles': 0,
            'neutral_profiles': 0,
            'most_positive_profile': None,
            'most_negative_profile': None,
            'sentiment_consensus': 'mixed'
        }
        
        profile_scores = []
        
        for profile, data in profile_results.items():
            if 'error' not in data and 'average_sentiment' in data:
                score = data['average_sentiment'].get('score', 0)
                sentiment = data['average_sentiment'].get('sentiment', 'neutral')
                
                profile_scores.append((profile, score))
                
                if sentiment == 'positive':
                    insights['positive_profiles'] += 1
                elif sentiment == 'negative':
                    insights['negative_profiles'] += 1
                else:
                    insights['neutral_profiles'] += 1
        
        # Find most positive/negative profiles
        if profile_scores:
            profile_scores.sort(key=lambda x: x[1], reverse=True)
            insights['most_positive_profile'] = profile_scores[0]
            insights['most_negative_profile'] = profile_scores[-1]
            
            # Determine consensus
            positive_ratio = insights['positive_profiles'] / len(profile_scores)
            if positive_ratio > 0.6:
                insights['sentiment_consensus'] = 'bullish'
            elif positive_ratio < 0.4:
                insights['sentiment_consensus'] = 'bearish'
            else:
                insights['sentiment_consensus'] = 'mixed'
        
        return insights
    
    def _calculate_key_metrics(self, recent_stats: Dict[str, Any], historical_stats: Dict[str, Any], 
                              sentiment_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance metrics."""
        
        metrics = {}
        
        # Activity change metrics
        if historical_stats['total_filings'] > 0:
            filing_change = (recent_stats['total_filings'] - historical_stats['total_filings']) / historical_stats['total_filings']
            metrics['filing_activity_change'] = round(filing_change * 100, 1)
        else:
            metrics['filing_activity_change'] = 100 if recent_stats['total_filings'] > 0 else 0
        
        # Buy/sell ratio
        total_recent_transactions = recent_stats['buy_transactions'] + recent_stats['sell_transactions']
        if total_recent_transactions > 0:
            metrics['recent_buy_sell_ratio'] = round(recent_stats['buy_transactions'] / total_recent_transactions, 2)
        else:
            metrics['recent_buy_sell_ratio'] = 0.5
        
        total_historical_transactions = historical_stats['buy_transactions'] + historical_stats['sell_transactions']
        if total_historical_transactions > 0:
            metrics['historical_buy_sell_ratio'] = round(historical_stats['buy_transactions'] / total_historical_transactions, 2)
        else:
            metrics['historical_buy_sell_ratio'] = 0.5
        
        # Sentiment-insider alignment
        sentiment_score = sentiment_summary.get('overall_score', 0)
        buy_sell_ratio = metrics['recent_buy_sell_ratio']
        
        if sentiment_score > 0.1 and buy_sell_ratio > 0.5:
            metrics['sentiment_insider_alignment'] = 'positive_aligned'
        elif sentiment_score < -0.1 and buy_sell_ratio < 0.5:
            metrics['sentiment_insider_alignment'] = 'negative_aligned'
        else:
            metrics['sentiment_insider_alignment'] = 'mixed_signals'
        
        # Activity intensity
        symbols_count = len(set(recent_stats['active_symbols'] + historical_stats['active_symbols']))
        if symbols_count > 0:
            metrics['average_filings_per_symbol'] = round(recent_stats['total_filings'] / symbols_count, 1)
        else:
            metrics['average_filings_per_symbol'] = 0
        
        return metrics
    
    def _generate_llm_summary(self, data_summary: Dict[str, Any]) -> str:
        """Generate summary using OpenRouter LLM."""
        
        prompt = self._build_analysis_prompt(data_summary)
        
        try:
            response = self._call_openrouter_api(prompt)
            return response
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return self._generate_template_summary(data_summary)
    
    def _build_analysis_prompt(self, data_summary: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt for LLM."""
        
        recent = data_summary['recent_activity']
        historical = data_summary['historical_activity']
        sentiment = data_summary['sentiment_analysis']
        metrics = data_summary['key_metrics']
        
        prompt = f"""
        You are a senior financial analyst specializing in insider trading and market sentiment analysis. 
        Analyze the following data and provide a comprehensive investment intelligence report.

        RECENT INSIDER ACTIVITY (Last 24 hours):
        - Total Filings: {recent['total_filings']}
        - Buy Transactions: {recent['buy_transactions']}
        - Sell Transactions: {recent['sell_transactions']}
        - Unique Insiders: {recent['unique_insider_count']}
        - Active Symbols: {', '.join(recent['active_symbols'])}

        HISTORICAL COMPARISON (Previous Period):
        - Total Filings: {historical['total_filings']}
        - Buy Transactions: {historical['buy_transactions']}
        - Sell Transactions: {historical['sell_transactions']}
        - Unique Insiders: {historical['unique_insider_count']}

        SOCIAL SENTIMENT ANALYSIS:
        - Overall Sentiment: {sentiment['overall_sentiment']} (Score: {sentiment['overall_score']})
        - Profiles Analyzed: {sentiment['profiles_analyzed']}
        - Total Posts: {sentiment['total_posts']}
        - Sentiment Consensus: {sentiment['sentiment_consensus']}
        - Positive/Negative/Neutral Profiles: {sentiment['positive_profiles']}/{sentiment['negative_profiles']}/{sentiment['neutral_profiles']}

        KEY METRICS:
        - Filing Activity Change: {metrics['filing_activity_change']}%
        - Recent Buy/Sell Ratio: {metrics['recent_buy_sell_ratio']}
        - Historical Buy/Sell Ratio: {metrics['historical_buy_sell_ratio']}
        - Sentiment-Insider Alignment: {metrics['sentiment_insider_alignment']}

        SYMBOLS ANALYZED: {', '.join(data_summary['symbols_analyzed'])}

        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (bullet points)
        3. Insider Activity Analysis
        4. Social Sentiment Impact
        5. Risk Assessment
        6. Investment Implications
        7. Recommended Actions

        Format the response in clear sections with actionable insights.
        """
        
        return prompt
    
    def _call_openrouter_api(self, prompt: str) -> str:
        """Make API call to OpenRouter."""
        
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/wildcraft958/CrowdWisdomTrading_AI_Agent',
            'X-Title': 'CrowdWisdom Trading AI Agent'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    logger.warning(f"OpenRouter API error (attempt {attempt + 1}): {response.status_code}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"API error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"API timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise Exception("API timeout")
            
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise
    
    def _generate_template_summary(self, data_summary: Dict[str, Any]) -> str:
        """Generate template-based summary when LLM is unavailable."""
        
        recent = data_summary['recent_activity']
        historical = data_summary['historical_activity']
        sentiment = data_summary['sentiment_analysis']
        metrics = data_summary['key_metrics']
        
        summary = f"""
# Trading Intelligence Report
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary
Recent insider trading activity shows {recent['total_filings']} filings with {recent['buy_transactions']} buy and {recent['sell_transactions']} sell transactions. Activity changed by {metrics['filing_activity_change']}% compared to the historical period. Social sentiment is {sentiment['overall_sentiment']} with a consensus that is {sentiment['sentiment_consensus']}.

## Key Findings
• **Filing Activity**: {metrics['filing_activity_change']:+.1f}% change from historical period
• **Buy/Sell Ratio**: {metrics['recent_buy_sell_ratio']:.2f} (vs {metrics['historical_buy_sell_ratio']:.2f} historically)
• **Active Symbols**: {len(recent['active_symbols'])} symbols with insider activity
• **Social Sentiment**: {sentiment['overall_sentiment'].title()} ({sentiment['overall_score']:+.2f})
• **Alignment**: {metrics['sentiment_insider_alignment'].replace('_', ' ').title()}

## Insider Activity Analysis
### Recent Activity (24h)
- Total filings: {recent['total_filings']}
- Insider purchases: {recent['buy_transactions']}
- Insider sales: {recent['sell_transactions']}
- Unique insiders: {recent['unique_insider_count']}

### Historical Comparison
- Change in total filings: {metrics['filing_activity_change']:+.1f}%
- Buy ratio shift: {metrics['recent_buy_sell_ratio'] - metrics['historical_buy_sell_ratio']:+.2f}

## Social Sentiment Impact
- Overall sentiment: {sentiment['overall_sentiment'].title()} ({sentiment['overall_score']:+.2f})
- Profiles analyzed: {sentiment['profiles_analyzed']}
- Posts analyzed: {sentiment['total_posts']}
- Consensus: {sentiment['sentiment_consensus'].title()}

## Risk Assessment
"""
        
        # Add risk assessment based on data
        if metrics['sentiment_insider_alignment'] == 'positive_aligned':
            summary += "🟢 **LOW RISK**: Positive sentiment aligns with insider buying activity.\n"
        elif metrics['sentiment_insider_alignment'] == 'negative_aligned':
            summary += "🔴 **HIGH RISK**: Negative sentiment aligns with insider selling activity.\n"
        else:
            summary += "🟡 **MEDIUM RISK**: Mixed signals between sentiment and insider activity.\n"
        
        summary += f"""
## Investment Implications
Based on the analysis of {len(data_summary['symbols_analyzed'])} symbols:

**Active Symbols**: {', '.join(data_summary['symbols_analyzed'])}

**Key Observations**:
- Filing activity is {'increasing' if metrics['filing_activity_change'] > 0 else 'decreasing'} by {abs(metrics['filing_activity_change']):.1f}%
- Insider buy/sell ratio is {metrics['recent_buy_sell_ratio']:.2f}
- Social sentiment is {sentiment['sentiment_consensus']}

## Recommended Actions
1. **Monitor** symbols with significant insider activity changes
2. **Analyze** alignment between insider actions and social sentiment
3. **Consider** the {metrics['sentiment_insider_alignment'].replace('_', ' ')} signals in investment decisions
4. **Track** upcoming earnings and news for active symbols

---
*This report combines SEC insider trading data with social sentiment analysis for comprehensive market intelligence.*
"""
        
        return summary
    
    def _generate_error_summary(self, error_message: str) -> str:
        """Generate error summary when analysis fails."""
        
        return f"""
# Trading Intelligence Report - Error
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Error Summary
An error occurred during report generation: {error_message}

## Fallback Analysis
Limited analysis available due to processing error. Please check:
1. API connectivity and credentials
2. Data source availability  
3. Input data format and completeness

## Recommended Actions
1. Verify environment configuration
2. Check API rate limits and quotas
3. Retry analysis with reduced scope
4. Contact system administrator if errors persist

---
*Error report generated by CrowdWisdom Trading AI Agent*
"""
    
    def _save_summary(self, summary: str):
        """Save summary to output file."""
        try:
            output_dir = Path("output/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trading_intelligence_report_{timestamp}.md"
            
            with open(output_dir / filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            logger.info(f"Report saved: {output_dir / filename}")
            
        except Exception as e:
            logger.error(f"Error saving summary: {e}")

def summarize_report(sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                    sentiment_results: Dict[str, Any]) -> str:
    """
    Main function to generate comprehensive report summary.
    
    Args:
        sec_data: Recent SEC filing data
        history_data: Historical SEC filing data
        sentiment_results: Social sentiment analysis results
    
    Returns:
        Comprehensive report summary
    """
    analyzer = LLMAnalyzer()
    return analyzer.summarize_report(sec_data, history_data, sentiment_results)

if __name__ == "__main__":
    # Test LLM tool with mock data
    mock_sec_data = {
        'AAPL': {
            'filings_count': 2,
            'filings': [
                {
                    'reporting_owner': {'name': 'John Doe'},
                    'transactions': [{'acquired_disposed': 'A'}]
                }
            ]
        }
    }
    
    mock_history_data = {
        'AAPL': {
            'filings_count': 1,
            'filings': [
                {
                    'reporting_owner': {'name': 'Jane Smith'},
                    'transactions': [{'acquired_disposed': 'D'}]
                }
            ]
        }
    }
    
    mock_sentiment = {
        'overall_sentiment': {'score': 0.3, 'sentiment': 'positive'},
        'profile_results': {
            'creator1': {'average_sentiment': {'score': 0.5, 'sentiment': 'positive'}}
        }
    }
    
    print("Testing LLM summary generation...")
    summary = summarize_report(mock_sec_data, mock_history_data, mock_sentiment)
    print(summary)
