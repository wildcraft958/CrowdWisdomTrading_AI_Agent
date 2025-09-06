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

def _safe_float(value) -> float:
    """Safely convert value to float, returning 0.0 if conversion fails."""
    try:
        if value is None or value == '':
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def _extract_filing_data(filing) -> Dict[str, Any]:
    """Extract relevant data from a Form 4 filing."""
    try:
        # Get basic filing info
        filing_data = {
            'accession_number': filing.accession_number,
            'filing_date': filing.filing_date.isoformat() if filing.filing_date else None,
            'url': filing.filing_url if hasattr(filing, 'filing_url') else None,
            'transactions': []
        }
        
        # Try to get the actual Form 4 object and parse transactions
        try:
            form4 = filing.obj()
            
            # Extract issuer information
            if hasattr(form4, 'issuer'):
                filing_data['issuer'] = {
                    'name': getattr(form4.issuer, 'name', None),
                    'cik': getattr(form4.issuer, 'cik', None),
                    'symbol': getattr(form4.issuer, 'trading_symbol', None)
                }
            
            # Extract reporting owner information  
            if hasattr(form4, 'reporting_owners') and form4.reporting_owners:
                # Get the first reporting owner
                owner = form4.reporting_owners[0] if isinstance(form4.reporting_owners, list) else form4.reporting_owners
                filing_data['reporting_owner'] = {
                    'name': getattr(owner, 'name', None),
                    'cik': getattr(owner, 'cik', None),
                    'is_director': getattr(owner, 'is_director', False),
                    'is_officer': getattr(owner, 'is_officer', False),
                    'is_ten_percent_owner': getattr(owner, 'is_ten_percent_owner', False)
                }
            
            # Parse non-derivative transactions using the correct EdgarTools API
            transactions = []
            
            # Check for non-derivative table
            if hasattr(form4, 'non_derivative_table') and form4.non_derivative_table is not None:
                nd_table = form4.non_derivative_table
                
                if hasattr(nd_table, 'transactions') and nd_table.transactions is not None:
                    trans_obj = nd_table.transactions
                    
                    # Access the DataFrame with transaction data
                    if hasattr(trans_obj, 'data') and trans_obj.data is not None:
                        df = trans_obj.data
                        logger.info(f"Found {len(df)} transactions in non-derivative table for {filing.accession_number}")
                        
                        for _, row in df.iterrows():
                            try:
                                transaction_data = {
                                    'security_title': row.get('Security', ''),
                                    'transaction_date': str(row.get('Date', '')),
                                    'transaction_code': row.get('Code', ''),
                                    'transaction_type': row.get('TransactionType', ''),
                                    'shares': _safe_float(row.get('Shares', 0)),
                                    'price_per_share': _safe_float(row.get('Price', 0)),
                                    'acquired_disposed': row.get('AcquiredDisposed', ''),
                                    'ownership_nature': row.get('DirectIndirect', 'D'),
                                    'remaining_shares': _safe_float(row.get('Remaining', 0))
                                }
                                
                                # Only add valid transactions with actual share amounts
                                if transaction_data['shares'] > 0 and transaction_data['transaction_code']:
                                    transactions.append(transaction_data)
                                    logger.info(f"Transaction: {transaction_data['transaction_code']} - "
                                              f"{transaction_data['shares']} shares - "
                                              f"Type: {transaction_data['transaction_type']}")
                                    
                            except Exception as e:
                                logger.warning(f"Error parsing transaction row: {e}")
                                continue
            
            # Also check derivative transactions if present
            if hasattr(form4, 'derivative_table') and form4.derivative_table is not None:
                deriv_table = form4.derivative_table
                
                if hasattr(deriv_table, 'transactions') and deriv_table.transactions is not None:
                    deriv_trans_obj = deriv_table.transactions
                    
                    if hasattr(deriv_trans_obj, 'data') and deriv_trans_obj.data is not None:
                        df = deriv_trans_obj.data
                        logger.info(f"Found {len(df)} derivative transactions for {filing.accession_number}")
                        
                        for _, row in df.iterrows():
                            try:
                                transaction_data = {
                                    'security_title': row.get('Security', ''),
                                    'transaction_date': str(row.get('Date', '')),
                                    'transaction_code': row.get('Code', ''),
                                    'transaction_type': row.get('TransactionType', ''),
                                    'shares': _safe_float(row.get('Shares', 0)),
                                    'price_per_share': _safe_float(row.get('Price', 0)),
                                    'acquired_disposed': row.get('AcquiredDisposed', ''),
                                    'derivative': True,
                                    'underlying_shares': _safe_float(row.get('UnderlyingShares', 0))
                                }
                                
                                if transaction_data['shares'] > 0 or transaction_data['underlying_shares'] > 0:
                                    transactions.append(transaction_data)
                                    
                            except Exception as e:
                                logger.warning(f"Error parsing derivative transaction: {e}")
                                continue
            
            filing_data['transactions'] = transactions
            filing_data['transaction_count'] = len(transactions)
            
            if len(transactions) == 0:
                logger.warning(f"No transactions found in filing {filing.accession_number}")
            else:
                logger.info(f"Successfully extracted {len(transactions)} transactions from {filing.accession_number}")
                
        except Exception as e:
            logger.error(f"Error extracting Form 4 data from {filing.accession_number}: {e}")
            filing_data['extraction_error'] = str(e)
            
            # Try alternative parsing method if needed
            try:
                filing_text = filing.text()
                if 'transactionCode' in filing_text and ('P' in filing_text or 'S' in filing_text):
                    logger.info(f"Found transaction codes in text for {filing.accession_number}")
                    filing_data['has_transactions_in_text'] = True
            except:
                pass
        
        return filing_data
        
    except Exception as e:
        logger.error(f"Error extracting filing data: {e}")
        return {
            'error': str(e),
            'accession_number': getattr(filing, 'accession_number', 'unknown'),
            'transactions': []
        }

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
        'symbols_with_activity': [],
        'transaction_details': []
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
            
            # Analyze transactions - this is the key fix!
            for transaction in filing.get('transactions', []):
                transaction_code = transaction.get('transaction_code', '').upper()
                acquired_disposed = transaction.get('acquired_disposed', '').upper()
                shares = _safe_float(transaction.get('shares', 0))
                
                # Create transaction detail for debugging
                trans_detail = {
                    'symbol': symbol,
                    'code': transaction_code,
                    'acquired_disposed': acquired_disposed,
                    'shares': shares,
                    'security_title': transaction.get('security_title', '')
                }
                summary['transaction_details'].append(trans_detail)
                
                # Common purchase codes: P (Purchase), A (Grant/Award), etc.
                # Common sale codes: S (Sale), D (Disposition), etc.
                
                # Check both transaction_code and acquired_disposed_code
                if transaction_code in ['P', 'A', 'G', 'L'] or acquired_disposed == 'A':
                    # This is a purchase/acquisition
                    summary['buy_transactions'] += 1
                    summary['total_shares_bought'] += shares
                    logger.info(f"BUY: {symbol} - {shares} shares (code: {transaction_code}, A/D: {acquired_disposed})")
                    
                elif transaction_code in ['S', 'D', 'F', 'M'] or acquired_disposed == 'D':
                    # This is a sale/disposition
                    summary['sell_transactions'] += 1
                    summary['total_shares_sold'] += shares
                    logger.info(f"SELL: {symbol} - {shares} shares (code: {transaction_code}, A/D: {acquired_disposed})")
                    
                else:
                    logger.warning(f"Unknown transaction type: {symbol} - code: {transaction_code}, A/D: {acquired_disposed}")
    
    # Convert set to list for JSON serialization
    summary['unique_insiders'] = list(summary['unique_insiders'])
    summary['unique_insider_count'] = len(summary['unique_insiders'])
    
    # Add some calculated ratios
    total_transactions = summary['buy_transactions'] + summary['sell_transactions']
    summary['total_transactions'] = total_transactions
    
    if total_transactions > 0:
        summary['buy_sell_ratio'] = summary['buy_transactions'] / total_transactions
    else:
        summary['buy_sell_ratio'] = 0.5  # neutral if no transactions
    
    logger.info(f"Summary: {summary['buy_transactions']} buys, {summary['sell_transactions']} sells, "
                f"{summary['total_shares_bought']:.0f} shares bought, {summary['total_shares_sold']:.0f} shares sold")
    
    return summary

if __name__ == "__main__":
    # Test the SEC tool
    test_symbols = ["AAPL", "MSFT"]
    print("Testing SEC data fetch...")
    
    recent_data = fetch_recent_sec_filings(test_symbols, days=7)
    print(f"Recent filings: {json.dumps(recent_data, indent=2, default=str)}")
    
    summary = get_insider_trading_summary(recent_data)
    print(f"Summary: {json.dumps(summary, indent=2, default=str)}")
