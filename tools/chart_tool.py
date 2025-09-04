"""
Chart generation tool using QuickChart API for visualization.
"""
import os
import logging
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartGenerator:
    """Chart generation using QuickChart API and other free charting services."""
    
    def __init__(self):
        self.quickchart_base_url = os.getenv('QUICKCHART_BASE_URL', 'https://quickchart.io/chart')
        self.output_dir = Path("output/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_chart(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                      sentiment_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate comprehensive chart combining SEC and historical data.
        
        Args:
            sec_data: Recent SEC filing data
            history_data: Historical SEC filing data
            sentiment_data: Optional sentiment analysis data
        
        Returns:
            Path to generated chart image
        """
        logger.info("Generating comprehensive trading activity chart")
        
        try:
            # Prepare data for visualization
            chart_data = self._prepare_chart_data(sec_data, history_data, sentiment_data)
            
            # Generate main activity chart
            activity_chart_path = self._generate_activity_chart(chart_data)
            
            # Generate sentiment chart if data available
            if sentiment_data:
                sentiment_chart_path = self._generate_sentiment_chart(sentiment_data)
                logger.info(f"Generated sentiment chart: {sentiment_chart_path}")
            
            # Generate summary dashboard
            dashboard_path = self._generate_dashboard(chart_data, sentiment_data)
            
            return dashboard_path
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return self._generate_error_chart(str(e))
    
    def _prepare_chart_data(self, sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                           sentiment_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare data for chart generation."""
        
        # Aggregate SEC data
        recent_summary = self._aggregate_sec_data(sec_data)
        historical_summary = self._aggregate_sec_data(history_data)
        
        # Prepare chart datasets
        chart_data = {
            'labels': ['Historical Period', 'Recent Activity'],
            'datasets': [
                {
                    'label': 'Insider Buys',
                    'data': [historical_summary['buy_count'], recent_summary['buy_count']],
                    'backgroundColor': 'rgba(34, 197, 94, 0.8)',
                    'borderColor': 'rgba(34, 197, 94, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Insider Sells',
                    'data': [historical_summary['sell_count'], recent_summary['sell_count']],
                    'backgroundColor': 'rgba(239, 68, 68, 0.8)',
                    'borderColor': 'rgba(239, 68, 68, 1)',
                    'borderWidth': 2
                }
            ],
            'summary': {
                'recent': recent_summary,
                'historical': historical_summary,
                'symbols': list(set(list(sec_data.keys()) + list(history_data.keys())))
            }
        }
        
        # Add sentiment data if available
        if sentiment_data:
            chart_data['sentiment'] = self._aggregate_sentiment_data(sentiment_data)
        
        return chart_data
    
    def _aggregate_sec_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate SEC data for charting."""
        summary = {
            'buy_count': 0,
            'sell_count': 0,
            'total_filings': 0,
            'symbols_with_activity': [],
            'insider_count': 0
        }
        
        insiders = set()
        
        for symbol, symbol_data in data.items():
            if 'error' in symbol_data:
                continue
            
            summary['total_filings'] += symbol_data.get('filings_count', 0)
            
            if symbol_data.get('filings_count', 0) > 0:
                summary['symbols_with_activity'].append(symbol)
            
            for filing in symbol_data.get('filings', []):
                # Count unique insiders
                if 'reporting_owner' in filing and filing['reporting_owner'].get('name'):
                    insiders.add(filing['reporting_owner']['name'])
                
                # Count transactions
                for transaction in filing.get('transactions', []):
                    acquired_disposed = transaction.get('acquired_disposed', '').upper()
                    if acquired_disposed == 'A':
                        summary['buy_count'] += 1
                    elif acquired_disposed == 'D':
                        summary['sell_count'] += 1
        
        summary['insider_count'] = len(insiders)
        return summary
    
    def _aggregate_sentiment_data(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate sentiment data for charting."""
        overall = sentiment_data.get('overall_sentiment', {})
        
        return {
            'score': overall.get('score', 0),
            'sentiment': overall.get('sentiment', 'neutral'),
            'profiles_count': overall.get('profiles_analyzed', 0),
            'total_posts': overall.get('total_posts', 0)
        }
    
    def _generate_activity_chart(self, chart_data: Dict[str, Any]) -> str:
        """Generate insider trading activity chart."""
        
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': chart_data['labels'],
                'datasets': chart_data['datasets']
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Insider Trading Activity Comparison',
                        'font': {'size': 16}
                    },
                    'legend': {
                        'display': True,
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Number of Transactions'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Time Period'
                        }
                    }
                }
            }
        }
        
        return self._save_chart(chart_config, 'insider_activity_comparison.png')
    
    def _generate_sentiment_chart(self, sentiment_data: Dict[str, Any]) -> str:
        """Generate sentiment analysis chart."""
        
        # Prepare sentiment distribution data
        profiles = sentiment_data.get('profile_results', {})
        labels = []
        scores = []
        colors = []
        
        for profile, data in profiles.items():
            if 'error' not in data and 'average_sentiment' in data:
                labels.append(profile)
                score = data['average_sentiment'].get('score', 0)
                scores.append(score)
                
                # Color based on sentiment
                if score > 0.1:
                    colors.append('rgba(34, 197, 94, 0.8)')  # Green for positive
                elif score < -0.1:
                    colors.append('rgba(239, 68, 68, 0.8)')  # Red for negative
                else:
                    colors.append('rgba(156, 163, 175, 0.8)')  # Gray for neutral
        
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Sentiment Score',
                    'data': scores,
                    'backgroundColor': colors,
                    'borderColor': [color.replace('0.8', '1') for color in colors],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Social Sentiment Analysis by Creator',
                        'font': {'size': 16}
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'min': -1,
                        'max': 1,
                        'title': {
                            'display': True,
                            'text': 'Sentiment Score (-1 to 1)'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Creators'
                        }
                    }
                }
            }
        }
        
        return self._save_chart(chart_config, 'sentiment_analysis.png')
    
    def _generate_dashboard(self, chart_data: Dict[str, Any], 
                           sentiment_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a comprehensive dashboard chart."""
        
        # Create a multi-panel dashboard
        recent = chart_data['summary']['recent']
        historical = chart_data['summary']['historical']
        
        # Dashboard configuration
        dashboard_config = {
            'type': 'bar',
            'data': {
                'labels': ['Buy Transactions', 'Sell Transactions', 'Total Filings', 'Active Symbols'],
                'datasets': [
                    {
                        'label': 'Historical',
                        'data': [
                            historical['buy_count'],
                            historical['sell_count'],
                            historical['total_filings'],
                            len(historical['symbols_with_activity'])
                        ],
                        'backgroundColor': 'rgba(59, 130, 246, 0.8)',
                        'borderColor': 'rgba(59, 130, 246, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'Recent',
                        'data': [
                            recent['buy_count'],
                            recent['sell_count'],
                            recent['total_filings'],
                            len(recent['symbols_with_activity'])
                        ],
                        'backgroundColor': 'rgba(168, 85, 247, 0.8)',
                        'borderColor': 'rgba(168, 85, 247, 1)',
                        'borderWidth': 2
                    }
                ]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Trading Intelligence Dashboard',
                        'font': {'size': 18}
                    },
                    'legend': {
                        'display': True,
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Count'
                        }
                    }
                }
            }
        }
        
        return self._save_chart(dashboard_config, 'trading_dashboard.png')
    
    def _save_chart(self, chart_config: Dict[str, Any], filename: str) -> str:
        """Save chart using QuickChart API."""
        try:
            # Encode chart configuration
            chart_json = json.dumps(chart_config)
            encoded_config = urllib.parse.quote(chart_json)
            
            # Construct URL
            url = f"{self.quickchart_base_url}?c={encoded_config}&width=800&height=600&format=png"
            
            # Make request
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Save to file
                chart_path = self.output_dir / filename
                with open(chart_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Chart saved: {chart_path}")
                return str(chart_path)
            else:
                logger.error(f"QuickChart API error: {response.status_code}")
                return self._generate_error_chart(f"API Error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            return self._generate_error_chart(str(e))
    
    def _generate_error_chart(self, error_message: str) -> str:
        """Generate a simple error chart."""
        error_config = {
            'type': 'bar',
            'data': {
                'labels': ['Error'],
                'datasets': [{
                    'label': 'Chart Generation Failed',
                    'data': [1],
                    'backgroundColor': 'rgba(239, 68, 68, 0.8)'
                }]
            },
            'options': {
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Chart Error: {error_message[:100]}...',
                        'font': {'size': 14}
                    }
                }
            }
        }
        
        return self._save_chart(error_config, 'error_chart.png')
    
    def generate_symbol_comparison_chart(self, data: Dict[str, Any]) -> str:
        """Generate chart comparing activity across different symbols."""
        
        symbols = []
        buy_counts = []
        sell_counts = []
        
        for symbol, symbol_data in data.items():
            if 'error' in symbol_data:
                continue
            
            symbols.append(symbol)
            
            buy_count = 0
            sell_count = 0
            
            for filing in symbol_data.get('filings', []):
                for transaction in filing.get('transactions', []):
                    acquired_disposed = transaction.get('acquired_disposed', '').upper()
                    if acquired_disposed == 'A':
                        buy_count += 1
                    elif acquired_disposed == 'D':
                        sell_count += 1
            
            buy_counts.append(buy_count)
            sell_counts.append(sell_count)
        
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': symbols,
                'datasets': [
                    {
                        'label': 'Buy Transactions',
                        'data': buy_counts,
                        'backgroundColor': 'rgba(34, 197, 94, 0.8)'
                    },
                    {
                        'label': 'Sell Transactions',
                        'data': sell_counts,
                        'backgroundColor': 'rgba(239, 68, 68, 0.8)'
                    }
                ]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Insider Trading Activity by Symbol',
                        'font': {'size': 16}
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Number of Transactions'
                        }
                    }
                }
            }
        }
        
        return self._save_chart(chart_config, 'symbol_comparison.png')

def generate_chart(sec_data: Dict[str, Any], history_data: Dict[str, Any], 
                  sentiment_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Main function to generate comprehensive trading charts.
    
    Args:
        sec_data: Recent SEC filing data
        history_data: Historical SEC filing data
        sentiment_data: Optional sentiment analysis data
    
    Returns:
        Path to generated chart image
    """
    generator = ChartGenerator()
    return generator.generate_chart(sec_data, history_data, sentiment_data)

if __name__ == "__main__":
    # Test chart generation with mock data
    mock_sec_data = {
        'AAPL': {
            'filings_count': 3,
            'filings': [
                {
                    'transactions': [
                        {'acquired_disposed': 'A'},
                        {'acquired_disposed': 'D'}
                    ]
                }
            ]
        }
    }
    
    mock_history_data = {
        'AAPL': {
            'filings_count': 5,
            'filings': [
                {
                    'transactions': [
                        {'acquired_disposed': 'A'},
                        {'acquired_disposed': 'A'},
                        {'acquired_disposed': 'D'}
                    ]
                }
            ]
        }
    }
    
    print("Testing chart generation...")
    chart_path = generate_chart(mock_sec_data, mock_history_data)
    print(f"Chart generated: {chart_path}")
