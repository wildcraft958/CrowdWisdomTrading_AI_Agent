"""
SEC Data Agent for collecting and processing insider trading data.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from tools.sec_tool import fetch_recent_sec_filings, get_insider_trading_summary

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECDataAgent:
    """Agent responsible for collecting and processing SEC insider trading data."""
    
    def __init__(self):
        """Initialize SEC Data Agent."""
        self.agent_name = "SEC Data Collector"
        self.description = "Specialized agent for extracting and analyzing SEC insider trading filings"
        logger.info(f"Initialized {self.agent_name}")
    
    def run(self, symbols: List[str], days: int = 1) -> Dict[str, Any]:
        """
        Collect recent SEC Form 4 filings for specified symbols.
        
        Args:
            symbols: List of stock symbols to analyze
            days: Number of days to look back for filings (default: 1)
        
        Returns:
            Dictionary containing filing data and analysis
        """
        logger.info(f"SEC Agent analyzing {len(symbols)} symbols for last {days} day(s)")
        
        try:
            # Fetch recent SEC filings
            filing_data = fetch_recent_sec_filings(symbols, days)
            
            # Generate summary statistics
            summary = get_insider_trading_summary(filing_data)
            
            # Prepare agent results
            results = {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'symbols_requested': symbols,
                'days_analyzed': days,
                'raw_data': filing_data,
                'summary': summary,
                'insights': self._generate_insights(filing_data, summary),
                'status': 'success'
            }
            
            logger.info(f"SEC Agent completed analysis: {summary['total_filings']} filings found")
            return results
            
        except Exception as e:
            logger.error(f"SEC Agent error: {e}")
            return {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'symbols_requested': symbols,
                'days_analyzed': days,
                'error': str(e),
                'status': 'error'
            }
    
    def _generate_insights(self, filing_data: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate key insights from SEC filing data."""
        
        insights = {
            'activity_level': 'low',
            'buy_sell_signal': 'neutral',
            'most_active_symbol': None,
            'notable_patterns': [],
            'risk_indicators': []
        }
        
        try:
            # Determine activity level
            total_filings = summary.get('total_filings', 0)
            if total_filings > 10:
                insights['activity_level'] = 'high'
            elif total_filings > 3:
                insights['activity_level'] = 'moderate'
            else:
                insights['activity_level'] = 'low'
            
            # Analyze buy/sell signals
            buy_transactions = summary.get('buy_transactions', 0)
            sell_transactions = summary.get('sell_transactions', 0)
            
            if buy_transactions > sell_transactions * 1.5:
                insights['buy_sell_signal'] = 'bullish'
            elif sell_transactions > buy_transactions * 1.5:
                insights['buy_sell_signal'] = 'bearish'
            else:
                insights['buy_sell_signal'] = 'neutral'
            
            # Find most active symbol
            symbol_activity = {}
            for symbol, data in filing_data.items():
                if 'error' not in data:
                    symbol_activity[symbol] = data.get('filings_count', 0)
            
            if symbol_activity:
                insights['most_active_symbol'] = max(symbol_activity, key=symbol_activity.get)
            
            # Identify notable patterns
            if total_filings > 0:
                # High volume pattern
                if total_filings > 5:
                    insights['notable_patterns'].append('high_volume_activity')
                
                # Concentrated activity pattern
                active_symbols = len(summary.get('symbols_with_activity', []))
                if active_symbols > 0 and total_filings / active_symbols > 3:
                    insights['notable_patterns'].append('concentrated_activity')
                
                # Unusual insider count
                unique_insiders = summary.get('unique_insider_count', 0)
                if unique_insiders > total_filings * 0.8:
                    insights['notable_patterns'].append('widespread_insider_activity')
            
            # Risk indicators
            if sell_transactions > buy_transactions * 2:
                insights['risk_indicators'].append('heavy_insider_selling')
            
            if total_filings > 10 and buy_transactions == 0:
                insights['risk_indicators'].append('no_insider_buying')
            
            # Symbol-specific insights
            insights['symbol_insights'] = {}
            for symbol, data in filing_data.items():
                if 'error' not in data and data.get('filings_count', 0) > 0:
                    symbol_insights = self._analyze_symbol_specific(symbol, data)
                    insights['symbol_insights'][symbol] = symbol_insights
            
        except Exception as e:
            logger.warning(f"Error generating insights: {e}")
            insights['generation_error'] = str(e)
        
        return insights
    
    def _analyze_symbol_specific(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze insights for a specific symbol."""
        
        symbol_insights = {
            'filing_count': data.get('filings_count', 0),
            'transaction_types': {'buys': 0, 'sells': 0},
            'insider_roles': [],
            'notable_transactions': [],
            'risk_level': 'low'
        }
        
        try:
            for filing in data.get('filings', []):
                # Analyze insider roles
                if 'reporting_owner' in filing:
                    owner = filing['reporting_owner']
                    if owner.get('is_director'):
                        symbol_insights['insider_roles'].append('director')
                    if owner.get('is_officer'):
                        symbol_insights['insider_roles'].append('officer')
                    if owner.get('is_ten_percent_owner'):
                        symbol_insights['insider_roles'].append('major_shareholder')
                
                # Analyze transactions
                for transaction in filing.get('transactions', []):
                    acquired_disposed = transaction.get('acquired_disposed', '').upper()
                    shares = transaction.get('shares', 0)
                    
                    try:
                        shares_num = float(shares) if shares else 0
                    except (ValueError, TypeError):
                        shares_num = 0
                    
                    if acquired_disposed == 'A':
                        symbol_insights['transaction_types']['buys'] += 1
                        if shares_num > 100000:  # Large transaction
                            symbol_insights['notable_transactions'].append({
                                'type': 'large_buy',
                                'shares': shares_num
                            })
                    elif acquired_disposed == 'D':
                        symbol_insights['transaction_types']['sells'] += 1
                        if shares_num > 100000:  # Large transaction
                            symbol_insights['notable_transactions'].append({
                                'type': 'large_sell',
                                'shares': shares_num
                            })
            
            # Determine risk level
            buys = symbol_insights['transaction_types']['buys']
            sells = symbol_insights['transaction_types']['sells']
            
            if sells > buys * 2:
                symbol_insights['risk_level'] = 'high'
            elif sells > buys:
                symbol_insights['risk_level'] = 'medium'
            else:
                symbol_insights['risk_level'] = 'low'
            
            # Remove duplicates from insider roles
            symbol_insights['insider_roles'] = list(set(symbol_insights['insider_roles']))
            
        except Exception as e:
            logger.warning(f"Error analyzing symbol {symbol}: {e}")
            symbol_insights['analysis_error'] = str(e)
        
        return symbol_insights
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities."""
        return {
            'agent_name': self.agent_name,
            'status': 'ready',
            'capabilities': [
                'SEC Form 4 filing extraction',
                'Insider trading pattern analysis',
                'Multi-symbol batch processing',
                'Historical trend comparison',
                'Risk assessment'
            ],
            'data_sources': ['SEC EDGAR database'],
            'output_formats': ['structured_data', 'summary_statistics', 'insights']
        }

if __name__ == "__main__":
    # Test the SEC agent
    agent = SECDataAgent()
    
    # Test with sample symbols
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    results = agent.run(test_symbols, days=7)
    
    print(f"Agent Status: {results.get('status')}")
    print(f"Filings Found: {results.get('summary', {}).get('total_filings', 0)}")
    print(f"Insights: {results.get('insights', {}).get('activity_level', 'unknown')}")
