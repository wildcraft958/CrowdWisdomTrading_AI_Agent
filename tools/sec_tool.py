"""
SEC data extraction tool using EdgarTools for insider trading analysis.
"""
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

try:
    from edgar import Company, set_identity
    from edgar.core import edgar_mode
except ImportError:
    logging.error("EdgarTools not installed. Please install with: pip install edgartools")
    raise

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_edgar():
    """Initialize EDGAR with user identity."""
    identity = os.getenv('SEC_IDENTITY', 'your.email@example.com')
    set_identity(identity)
    logger.info(f"EDGAR initialized with identity: {identity}")

def fetch_recent_sec_filings(symbols: List[str], days: int = 1) -> Dict[str, Any]:
    """
    Fetch recent SEC Form 4 filings for given symbols.
    
    Args:
        symbols: List of stock symbols to analyze
        days: Number of days to look back (default: 1)
    
    Returns:
        Dictionary with symbol as key and filing data as value
    """
    initialize_edgar()
    results = {}
    cache_dir = Path("data/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    for symbol in symbols:
        try:
            logger.info(f"Fetching recent filings for {symbol}")
            
            # Check cache first
            cache_file = cache_dir / f"{symbol}_recent_{days}d.json"
            if cache_file.exists() and _is_cache_fresh(cache_file, hours=1):
                logger.info(f"Using cached data for {symbol}")
                with open(cache_file, 'r') as f:
                    results[symbol] = json.load(f)
                continue
            
            company = Company(symbol)
            
            # Get Form 4 filings (insider trading)
            filings = company.get_filings(form="4")
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_filings = []
            
            for filing in filings.head(50):  # Limit to avoid too many API calls
                filing_date = filing.filing_date
                if filing_date >= cutoff_date.date():
                    try:
                        filing_data = _extract_filing_data(filing)
                        recent_filings.append(filing_data)
                    except Exception as e:
                        logger.warning(f"Error processing filing for {symbol}: {e}")
                        continue
                else:
                    break  # Filings are sorted by date, so we can break early
            
            results[symbol] = {
                'symbol': symbol,
                'filings_count': len(recent_filings),
                'filings': recent_filings,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the results
            with open(cache_file, 'w') as f:
                json.dump(results[symbol], f, indent=2, default=str)
                
            logger.info(f"Found {len(recent_filings)} recent filings for {symbol}")
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            results[symbol] = {
                'symbol': symbol,
                'error': str(e),
                'filings_count': 0,
                'filings': []
            }
    
    return results

def fetch_historical_sec_filings(symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Fetch historical SEC Form 4 filings for given symbols in date range.
    
    Args:
        symbols: List of stock symbols to analyze
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary with historical filing data
    """
    initialize_edgar()
    results = {}
    cache_dir = Path("data/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    for symbol in symbols:
        try:
            logger.info(f"Fetching historical filings for {symbol} from {start_date} to {end_date}")
            
            # Check cache
            cache_file = cache_dir / f"{symbol}_historical_{start_date}_{end_date}.json"
            if cache_file.exists() and _is_cache_fresh(cache_file, hours=24):
                logger.info(f"Using cached historical data for {symbol}")
                with open(cache_file, 'r') as f:
                    results[symbol] = json.load(f)
                continue
            
            company = Company(symbol)
            filings = company.get_filings(form="4")
            
            historical_filings = []
            for filing in filings.head(200):  # Reasonable limit
                filing_date = filing.filing_date
                if start_dt.date() <= filing_date <= end_dt.date():
                    try:
                        filing_data = _extract_filing_data(filing)
                        historical_filings.append(filing_data)
                    except Exception as e:
                        logger.warning(f"Error processing historical filing for {symbol}: {e}")
                        continue
                elif filing_date < start_dt.date():
                    break  # Stop when we go too far back
            
            results[symbol] = {
                'symbol': symbol,
                'date_range': f"{start_date} to {end_date}",
                'filings_count': len(historical_filings),
                'filings': historical_filings,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the results
            with open(cache_file, 'w') as f:
                json.dump(results[symbol], f, indent=2, default=str)
                
            logger.info(f"Found {len(historical_filings)} historical filings for {symbol}")
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            results[symbol] = {
                'symbol': symbol,
                'error': str(e),
                'filings_count': 0,
                'filings': []
            }
    
    return results

def _extract_filing_data(filing) -> Dict[str, Any]:
    """Extract relevant data from a Form 4 filing."""
    try:
        # Get basic filing info
        filing_data = {
            'accession_number': filing.accession_number,
            'filing_date': filing.filing_date.isoformat() if filing.filing_date else None,
            'url': filing.filing_url if hasattr(filing, 'filing_url') else None
        }
        
        # Try to get more detailed data if available
        try:
            form4_data = filing.obj()
            if hasattr(form4_data, 'issuer'):
                filing_data['issuer'] = {
                    'name': getattr(form4_data.issuer, 'name', None),
                    'cik': getattr(form4_data.issuer, 'cik', None),
                    'symbol': getattr(form4_data.issuer, 'trading_symbol', None)
                }
            
            if hasattr(form4_data, 'reporting_owner'):
                filing_data['reporting_owner'] = {
                    'name': getattr(form4_data.reporting_owner, 'name', None),
                    'cik': getattr(form4_data.reporting_owner, 'cik', None),
                    'is_director': getattr(form4_data.reporting_owner, 'is_director', None),
                    'is_officer': getattr(form4_data.reporting_owner, 'is_officer', None),
                    'is_ten_percent_owner': getattr(form4_data.reporting_owner, 'is_ten_percent_owner', None)
                }
            
            # Extract transaction data if available
            if hasattr(form4_data, 'non_derivative_transactions'):
                transactions = []
                for trans in form4_data.non_derivative_transactions:
                    transaction_data = {
                        'security_title': getattr(trans, 'security_title', None),
                        'transaction_date': getattr(trans, 'transaction_date', None),
                        'transaction_code': getattr(trans, 'transaction_code', None),
                        'shares': getattr(trans, 'shares', None),
                        'price_per_share': getattr(trans, 'price_per_share', None),
                        'acquired_disposed': getattr(trans, 'acquired_disposed_code', None)
                    }
                    transactions.append(transaction_data)
                filing_data['transactions'] = transactions
                
        except Exception as e:
            logger.warning(f"Could not extract detailed Form 4 data: {e}")
            filing_data['extraction_error'] = str(e)
        
        return filing_data
        
    except Exception as e:
        logger.error(f"Error extracting filing data: {e}")
        return {'error': str(e)}

def _is_cache_fresh(cache_file: Path, hours: int = 1) -> bool:
    """Check if cache file is fresh enough to use."""
    if not cache_file.exists():
        return False
    
    file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
    return file_age < timedelta(hours=hours)

def get_insider_trading_summary(filing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary statistics from insider trading data.
    
    Args:
        filing_data: Dictionary containing filing data from fetch_recent_sec_filings
    
    Returns:
        Summary statistics including buy/sell counts and volumes
    """
    summary = {
        'total_filings': 0,
        'buy_transactions': 0,
        'sell_transactions': 0,
        'total_shares_bought': 0,
        'total_shares_sold': 0,
        'unique_insiders': set(),
        'symbols_with_activity': []
    }
    
    for symbol, data in filing_data.items():
        if 'error' in data:
            continue
            
        summary['total_filings'] += data.get('filings_count', 0)
        
        if data.get('filings_count', 0) > 0:
            summary['symbols_with_activity'].append(symbol)
        
        for filing in data.get('filings', []):
            # Add reporting owner to unique insiders
            if 'reporting_owner' in filing and filing['reporting_owner'].get('name'):
                summary['unique_insiders'].add(filing['reporting_owner']['name'])
            
            # Analyze transactions
            for transaction in filing.get('transactions', []):
                acquired_disposed = transaction.get('acquired_disposed', '').upper()
                shares = transaction.get('shares', 0)
                
                try:
                    shares = float(shares) if shares else 0
                except (ValueError, TypeError):
                    shares = 0
                
                if acquired_disposed == 'A':  # Acquired
                    summary['buy_transactions'] += 1
                    summary['total_shares_bought'] += shares
                elif acquired_disposed == 'D':  # Disposed
                    summary['sell_transactions'] += 1
                    summary['total_shares_sold'] += shares
    
    # Convert set to list for JSON serialization
    summary['unique_insiders'] = list(summary['unique_insiders'])
    summary['unique_insider_count'] = len(summary['unique_insiders'])
    
    return summary

if __name__ == "__main__":
    # Test the SEC tool
    test_symbols = ["AAPL", "MSFT"]
    print("Testing SEC data fetch...")
    
    recent_data = fetch_recent_sec_filings(test_symbols, days=7)
    print(f"Recent filings: {json.dumps(recent_data, indent=2, default=str)}")
    
    summary = get_insider_trading_summary(recent_data)
    print(f"Summary: {json.dumps(summary, indent=2, default=str)}")
