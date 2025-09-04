"""
Historical Data Agent for analyzing trading trends and patterns.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from tools.sec_tool import fetch_historical_sec_filings, get_insider_trading_summary

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoryDataAgent:
    """Agent responsible for historical trend analysis and comparison."""
    
    def __init__(self):
        """Initialize History Data Agent."""
        self.agent_name = "Historical Data Analyst"
        self.description = "Specialized agent for analyzing historical insider trading trends"
        logger.info(f"Initialized {self.agent_name}")
    
    def run(self, symbols: List[str], start_date: str, end_date: str, 
            compare_to_recent: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze historical insider trading patterns and compare with recent activity.
        
        Args:
            symbols: List of stock symbols to analyze
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            compare_to_recent: Optional recent data for comparison
        
        Returns:
            Dictionary containing historical analysis and trends
        """
        logger.info(f"History Agent analyzing {len(symbols)} symbols from {start_date} to {end_date}")
        
        try:
            # Fetch historical SEC filings
            historical_data = fetch_historical_sec_filings(symbols, start_date, end_date)
            
            # Generate summary statistics
            historical_summary = get_insider_trading_summary(historical_data)
            
            # Perform trend analysis
            trend_analysis = self._analyze_trends(historical_data, start_date, end_date)
            
            # Compare with recent data if provided
            comparison = None
            if compare_to_recent:
                comparison = self._compare_periods(historical_summary, compare_to_recent)
            
            # Prepare agent results
            results = {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'symbols_analyzed': symbols,
                'period': f"{start_date} to {end_date}",
                'raw_data': historical_data,
                'summary': historical_summary,
                'trend_analysis': trend_analysis,
                'comparison': comparison,
                'insights': self._generate_historical_insights(historical_data, trend_analysis),
                'status': 'success'
            }
            
            logger.info(f"History Agent completed: {historical_summary['total_filings']} historical filings analyzed")
            return results
            
        except Exception as e:
            logger.error(f"History Agent error: {e}")
            return {
                'agent': self.agent_name,
                'execution_time': datetime.now().isoformat(),
                'symbols_analyzed': symbols,
                'period': f"{start_date} to {end_date}",
                'error': str(e),
                'status': 'error'
            }
    
    def _analyze_trends(self, historical_data: Dict[str, Any], start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyze trends in historical data."""
        
        trends = {
            'period_summary': {
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': self._calculate_period_duration(start_date, end_date)
            },
            'activity_patterns': {},
            'symbol_trends': {},
            'temporal_distribution': {},
            'insider_behavior_patterns': {}
        }
        
        try:
            # Analyze activity patterns across symbols
            for symbol, data in historical_data.items():
                if 'error' in data:
                    continue
                
                symbol_trends = self._analyze_symbol_trends(symbol, data)
                trends['symbol_trends'][symbol] = symbol_trends
            
            # Analyze overall patterns
            trends['activity_patterns'] = self._identify_activity_patterns(historical_data)
            
            # Analyze temporal distribution
            trends['temporal_distribution'] = self._analyze_temporal_patterns(historical_data)
            
            # Analyze insider behavior patterns
            trends['insider_behavior_patterns'] = self._analyze_insider_patterns(historical_data)
            
        except Exception as e:
            logger.warning(f"Error in trend analysis: {e}")
            trends['analysis_error'] = str(e)
        
        return trends
    
    def _analyze_symbol_trends(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends for a specific symbol."""
        
        symbol_trends = {
            'total_activity': data.get('filings_count', 0),
            'transaction_breakdown': {'buys': 0, 'sells': 0, 'other': 0},
            'insider_count': 0,
            'activity_intensity': 'low',
            'dominant_transaction_type': 'none',
            'notable_periods': []
        }
        
        try:
            insiders = set()
            transactions_by_date = {}
            
            for filing in data.get('filings', []):
                # Count unique insiders
                if 'reporting_owner' in filing and filing['reporting_owner'].get('name'):
                    insiders.add(filing['reporting_owner']['name'])
                
                # Analyze transactions
                filing_date = filing.get('filing_date', '')
                if filing_date not in transactions_by_date:
                    transactions_by_date[filing_date] = {'buys': 0, 'sells': 0, 'other': 0}
                
                for transaction in filing.get('transactions', []):
                    acquired_disposed = transaction.get('acquired_disposed', '').upper()
                    if acquired_disposed == 'A':
                        symbol_trends['transaction_breakdown']['buys'] += 1
                        transactions_by_date[filing_date]['buys'] += 1
                    elif acquired_disposed == 'D':
                        symbol_trends['transaction_breakdown']['sells'] += 1
                        transactions_by_date[filing_date]['sells'] += 1
                    else:
                        symbol_trends['transaction_breakdown']['other'] += 1
                        transactions_by_date[filing_date]['other'] += 1
            
            symbol_trends['insider_count'] = len(insiders)
            
            # Determine activity intensity
            total_transactions = sum(symbol_trends['transaction_breakdown'].values())
            if total_transactions > 20:
                symbol_trends['activity_intensity'] = 'high'
            elif total_transactions > 5:
                symbol_trends['activity_intensity'] = 'moderate'
            else:
                symbol_trends['activity_intensity'] = 'low'
            
            # Determine dominant transaction type
            breakdown = symbol_trends['transaction_breakdown']
            if breakdown['buys'] > breakdown['sells'] * 1.5:
                symbol_trends['dominant_transaction_type'] = 'buying'
            elif breakdown['sells'] > breakdown['buys'] * 1.5:
                symbol_trends['dominant_transaction_type'] = 'selling'
            else:
                symbol_trends['dominant_transaction_type'] = 'mixed'
            
            # Identify notable periods (dates with high activity)
            for date, counts in transactions_by_date.items():
                total_day_transactions = sum(counts.values())
                if total_day_transactions > 3:  # Threshold for notable activity
                    symbol_trends['notable_periods'].append({
                        'date': date,
                        'transactions': total_day_transactions,
                        'breakdown': counts
                    })
            
            # Sort notable periods by activity
            symbol_trends['notable_periods'].sort(key=lambda x: x['transactions'], reverse=True)
            
        except Exception as e:
            logger.warning(f"Error analyzing trends for {symbol}: {e}")
            symbol_trends['analysis_error'] = str(e)
        
        return symbol_trends
    
    def _identify_activity_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify overall activity patterns across all symbols."""
        
        patterns = {
            'cross_symbol_correlation': 'low',
            'activity_concentration': {},
            'common_insiders': [],
            'pattern_types': []
        }
        
        try:
            # Analyze cross-symbol activity
            all_insiders = {}
            symbol_activity_dates = {}
            
            for symbol, data in historical_data.items():
                if 'error' in data:
                    continue
                
                symbol_activity_dates[symbol] = set()
                
                for filing in data.get('filings', []):
                    filing_date = filing.get('filing_date', '')
                    symbol_activity_dates[symbol].add(filing_date)
                    
                    # Track insiders across symbols
                    if 'reporting_owner' in filing and filing['reporting_owner'].get('name'):
                        insider_name = filing['reporting_owner']['name']
                        if insider_name not in all_insiders:
                            all_insiders[insider_name] = set()
                        all_insiders[insider_name].add(symbol)
            
            # Find common insiders (appearing in multiple symbols)
            patterns['common_insiders'] = [
                {'insider': insider, 'symbols': list(symbols)}
                for insider, symbols in all_insiders.items()
                if len(symbols) > 1
            ]
            
            # Analyze activity concentration
            total_symbols = len([s for s in historical_data.keys() if 'error' not in historical_data[s]])
            active_symbols = len([s for s, data in historical_data.items() 
                                if 'error' not in data and data.get('filings_count', 0) > 0])
            
            if total_symbols > 0:
                concentration_ratio = active_symbols / total_symbols
                if concentration_ratio < 0.3:
                    patterns['activity_concentration']['level'] = 'highly_concentrated'
                elif concentration_ratio < 0.7:
                    patterns['activity_concentration']['level'] = 'moderately_concentrated'
                else:
                    patterns['activity_concentration']['level'] = 'widely_distributed'
                
                patterns['activity_concentration']['ratio'] = round(concentration_ratio, 2)
                patterns['activity_concentration']['active_symbols'] = active_symbols
                patterns['activity_concentration']['total_symbols'] = total_symbols
            
            # Identify pattern types
            if len(patterns['common_insiders']) > 0:
                patterns['pattern_types'].append('cross_symbol_insider_activity')
            
            if patterns['activity_concentration']['level'] == 'highly_concentrated':
                patterns['pattern_types'].append('concentrated_activity')
            elif patterns['activity_concentration']['level'] == 'widely_distributed':
                patterns['pattern_types'].append('broad_market_activity')
            
        except Exception as e:
            logger.warning(f"Error identifying activity patterns: {e}")
            patterns['analysis_error'] = str(e)
        
        return patterns
    
    def _analyze_temporal_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal distribution of trading activity."""
        
        temporal = {
            'filing_frequency': {},
            'activity_clustering': [],
            'peak_activity_periods': []
        }
        
        try:
            all_filing_dates = []
            
            # Collect all filing dates
            for symbol, data in historical_data.items():
                if 'error' in data:
                    continue
                
                for filing in data.get('filings', []):
                    filing_date = filing.get('filing_date', '')
                    if filing_date:
                        all_filing_dates.append(filing_date)
            
            # Analyze frequency
            date_counts = {}
            for date in all_filing_dates:
                date_counts[date] = date_counts.get(date, 0) + 1
            
            temporal['filing_frequency'] = {
                'total_unique_dates': len(date_counts),
                'average_filings_per_active_date': round(len(all_filing_dates) / max(len(date_counts), 1), 2),
                'most_active_dates': sorted(date_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            }
            
            # Identify peak periods (dates with above-average activity)
            if date_counts:
                avg_activity = len(all_filing_dates) / len(date_counts)
                peak_dates = [date for date, count in date_counts.items() if count > avg_activity * 1.5]
                
                temporal['peak_activity_periods'] = [
                    {'date': date, 'filings': date_counts[date]}
                    for date in peak_dates
                ]
                temporal['peak_activity_periods'].sort(key=lambda x: x['filings'], reverse=True)
        
        except Exception as e:
            logger.warning(f"Error in temporal analysis: {e}")
            temporal['analysis_error'] = str(e)
        
        return temporal
    
    def _analyze_insider_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze insider behavior patterns."""
        
        insider_patterns = {
            'role_distribution': {'directors': 0, 'officers': 0, 'major_shareholders': 0, 'other': 0},
            'transaction_patterns': {},
            'repeat_insiders': [],
            'notable_insiders': []
        }
        
        try:
            insider_activity = {}
            
            for symbol, data in historical_data.items():
                if 'error' in data:
                    continue
                
                for filing in data.get('filings', []):
                    if 'reporting_owner' not in filing:
                        continue
                    
                    owner = filing['reporting_owner']
                    insider_name = owner.get('name', 'Unknown')
                    
                    # Initialize insider tracking
                    if insider_name not in insider_activity:
                        insider_activity[insider_name] = {
                            'symbols': set(),
                            'total_transactions': 0,
                            'buy_transactions': 0,
                            'sell_transactions': 0,
                            'roles': set(),
                            'filings': []
                        }
                    
                    # Track insider info
                    insider_activity[insider_name]['symbols'].add(symbol)
                    insider_activity[insider_name]['filings'].append(filing)
                    
                    # Track roles
                    if owner.get('is_director'):
                        insider_activity[insider_name]['roles'].add('director')
                        insider_patterns['role_distribution']['directors'] += 1
                    if owner.get('is_officer'):
                        insider_activity[insider_name]['roles'].add('officer')
                        insider_patterns['role_distribution']['officers'] += 1
                    if owner.get('is_ten_percent_owner'):
                        insider_activity[insider_name]['roles'].add('major_shareholder')
                        insider_patterns['role_distribution']['major_shareholders'] += 1
                    
                    if not any([owner.get('is_director'), owner.get('is_officer'), owner.get('is_ten_percent_owner')]):
                        insider_patterns['role_distribution']['other'] += 1
                    
                    # Track transactions
                    for transaction in filing.get('transactions', []):
                        insider_activity[insider_name]['total_transactions'] += 1
                        acquired_disposed = transaction.get('acquired_disposed', '').upper()
                        if acquired_disposed == 'A':
                            insider_activity[insider_name]['buy_transactions'] += 1
                        elif acquired_disposed == 'D':
                            insider_activity[insider_name]['sell_transactions'] += 1
            
            # Identify repeat insiders (multiple filings)
            for insider, activity in insider_activity.items():
                if len(activity['filings']) > 1:
                    insider_patterns['repeat_insiders'].append({
                        'name': insider,
                        'filing_count': len(activity['filings']),
                        'symbols': list(activity['symbols']),
                        'total_transactions': activity['total_transactions'],
                        'roles': list(activity['roles'])
                    })
            
            # Sort repeat insiders by activity level
            insider_patterns['repeat_insiders'].sort(key=lambda x: x['filing_count'], reverse=True)
            
            # Identify notable insiders (high activity or cross-symbol)
            for insider, activity in insider_activity.items():
                if activity['total_transactions'] > 5 or len(activity['symbols']) > 1:
                    insider_patterns['notable_insiders'].append({
                        'name': insider,
                        'total_transactions': activity['total_transactions'],
                        'buy_sell_ratio': activity['buy_transactions'] / max(activity['sell_transactions'], 1),
                        'symbols_count': len(activity['symbols']),
                        'symbols': list(activity['symbols']),
                        'roles': list(activity['roles'])
                    })
            
            # Sort notable insiders by transaction count
            insider_patterns['notable_insiders'].sort(key=lambda x: x['total_transactions'], reverse=True)
            
        except Exception as e:
            logger.warning(f"Error in insider pattern analysis: {e}")
            insider_patterns['analysis_error'] = str(e)
        
        return insider_patterns
    
    def _compare_periods(self, historical_summary: Dict[str, Any], recent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare historical period with recent data."""
        
        comparison = {
            'filing_change': {},
            'transaction_pattern_change': {},
            'insider_activity_change': {},
            'trend_direction': 'neutral',
            'significance_level': 'low'
        }
        
        try:
            # Get recent summary if it's raw data
            if 'summary' in recent_data:
                recent_summary = recent_data['summary']
            else:
                recent_summary = recent_data
            
            # Compare filing counts
            hist_filings = historical_summary.get('total_filings', 0)
            recent_filings = recent_summary.get('total_filings', 0)
            
            if hist_filings > 0:
                filing_change_pct = ((recent_filings - hist_filings) / hist_filings) * 100
            else:
                filing_change_pct = 100 if recent_filings > 0 else 0
            
            comparison['filing_change'] = {
                'historical': hist_filings,
                'recent': recent_filings,
                'absolute_change': recent_filings - hist_filings,
                'percentage_change': round(filing_change_pct, 1)
            }
            
            # Compare transaction patterns
            hist_buys = historical_summary.get('buy_transactions', 0)
            hist_sells = historical_summary.get('sell_transactions', 0)
            recent_buys = recent_summary.get('buy_transactions', 0)
            recent_sells = recent_summary.get('sell_transactions', 0)
            
            comparison['transaction_pattern_change'] = {
                'historical_buy_ratio': hist_buys / max(hist_buys + hist_sells, 1),
                'recent_buy_ratio': recent_buys / max(recent_buys + recent_sells, 1),
                'buy_transaction_change': recent_buys - hist_buys,
                'sell_transaction_change': recent_sells - hist_sells
            }
            
            # Compare insider activity
            hist_insiders = historical_summary.get('unique_insider_count', 0)
            recent_insiders = recent_summary.get('unique_insider_count', 0)
            
            comparison['insider_activity_change'] = {
                'historical_insider_count': hist_insiders,
                'recent_insider_count': recent_insiders,
                'insider_count_change': recent_insiders - hist_insiders
            }
            
            # Determine trend direction
            if filing_change_pct > 20:
                comparison['trend_direction'] = 'increasing'
                comparison['significance_level'] = 'high' if filing_change_pct > 50 else 'moderate'
            elif filing_change_pct < -20:
                comparison['trend_direction'] = 'decreasing'
                comparison['significance_level'] = 'high' if filing_change_pct < -50 else 'moderate'
            else:
                comparison['trend_direction'] = 'stable'
                comparison['significance_level'] = 'low'
            
        except Exception as e:
            logger.warning(f"Error in period comparison: {e}")
            comparison['comparison_error'] = str(e)
        
        return comparison
    
    def _generate_historical_insights(self, historical_data: Dict[str, Any], 
                                    trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from historical analysis."""
        
        insights = {
            'key_trends': [],
            'risk_indicators': [],
            'opportunity_signals': [],
            'pattern_assessment': 'normal',
            'historical_context': {}
        }
        
        try:
            activity_patterns = trend_analysis.get('activity_patterns', {})
            symbol_trends = trend_analysis.get('symbol_trends', {})
            temporal = trend_analysis.get('temporal_distribution', {})
            
            # Key trends
            if activity_patterns.get('activity_concentration', {}).get('level') == 'highly_concentrated':
                insights['key_trends'].append('Activity concentrated in few symbols')
            
            if len(activity_patterns.get('common_insiders', [])) > 0:
                insights['key_trends'].append('Cross-symbol insider activity detected')
            
            # Risk indicators
            sell_heavy_symbols = [
                symbol for symbol, trends in symbol_trends.items()
                if trends.get('dominant_transaction_type') == 'selling'
            ]
            if len(sell_heavy_symbols) > len(symbol_trends) * 0.5:
                insights['risk_indicators'].append('Widespread insider selling pattern')
            
            # Opportunity signals
            buy_heavy_symbols = [
                symbol for symbol, trends in symbol_trends.items()
                if trends.get('dominant_transaction_type') == 'buying'
            ]
            if len(buy_heavy_symbols) > 0:
                insights['opportunity_signals'].append(f'Insider buying in {len(buy_heavy_symbols)} symbols')
            
            # Pattern assessment
            total_activity = sum(data.get('filings_count', 0) for data in historical_data.values() if 'error' not in data)
            if total_activity > 50:
                insights['pattern_assessment'] = 'high_activity'
            elif total_activity > 20:
                insights['pattern_assessment'] = 'moderate_activity'
            else:
                insights['pattern_assessment'] = 'low_activity'
            
            # Historical context
            insights['historical_context'] = {
                'total_filings_analyzed': total_activity,
                'symbols_with_activity': len([s for s, d in historical_data.items() if 'error' not in d and d.get('filings_count', 0) > 0]),
                'peak_activity_days': len(temporal.get('peak_activity_periods', [])),
                'cross_symbol_insiders': len(activity_patterns.get('common_insiders', []))
            }
            
        except Exception as e:
            logger.warning(f"Error generating historical insights: {e}")
            insights['insight_error'] = str(e)
        
        return insights
    
    def _calculate_period_duration(self, start_date: str, end_date: str) -> int:
        """Calculate duration in days between two dates."""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            return (end_dt - start_dt).days + 1
        except Exception:
            return 0
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities."""
        return {
            'agent_name': self.agent_name,
            'status': 'ready',
            'capabilities': [
                'Historical trend analysis',
                'Pattern recognition',
                'Period comparison',
                'Temporal analysis',
                'Insider behavior tracking'
            ],
            'analysis_types': [
                'symbol_trends',
                'activity_patterns',
                'temporal_distribution',
                'insider_patterns',
                'period_comparison'
            ],
            'output_formats': ['trend_analysis', 'comparative_metrics', 'insights']
        }

if __name__ == "__main__":
    # Test the History agent
    agent = HistoryDataAgent()
    
    # Test with sample data
    test_symbols = ["AAPL", "MSFT"]
    start_date = "2024-08-01"
    end_date = "2024-08-31"
    
    results = agent.run(test_symbols, start_date, end_date)
    
    print(f"Agent Status: {results.get('status')}")
    print(f"Historical Filings: {results.get('summary', {}).get('total_filings', 0)}")
    print(f"Trend Assessment: {results.get('insights', {}).get('pattern_assessment', 'unknown')}")
