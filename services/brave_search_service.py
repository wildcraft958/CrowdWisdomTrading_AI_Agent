"""
Brave Search API service for real-time web search and news retrieval.
Provides access to current web content about financial influencers and market sentiment.
"""
import os
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv('configs/.env')

logger = logging.getLogger(__name__)

class BraveSearchService:
    """Service for Brave Search API integration."""
    
    def __init__(self):
        self.api_key = os.getenv('BRAVE_SEARCH_API_KEY')
        self.base_url = 'https://api.search.brave.com/res/v1'
        self.rate_limit_delay = float(os.getenv('BRAVE_SEARCH_RATE_LIMIT', '2'))
        
        if not self.api_key:
            logger.warning("No Brave Search API key found. Search functionality disabled.")
            
        self.last_request_time = {}
        
    def _rate_limit(self, endpoint: str = 'default'):
        """Rate limiting for Brave Search API."""
        current_time = time.time()
        last_time = self.last_request_time.get(endpoint, 0)
        
        if current_time - last_time < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - (current_time - last_time)
            time.sleep(sleep_time)
        
        self.last_request_time[endpoint] = time.time()
    
    def search_web(self, query: str, count: int = 10, market: str = 'US') -> List[Dict[str, Any]]:
        """
        Search the web using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return (max 20)
            market: Market region (US, GB, CA, etc.)
            
        Returns:
            List of search results
        """
        if not self.api_key:
            logger.warning("Brave Search API key not configured")
            return []
        
        try:
            self._rate_limit('web')
            
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': self.api_key
            }
            
            params = {
                'q': query,
                'count': min(count, 20),
                'offset': 0,
                'mkt': market,
                'safesearch': 'moderate',
                'textDecorations': False,
                'textFormat': 'Raw'
            }
            
            response = requests.get(
                f'{self.base_url}/web/search',
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_web_results(data.get('web', {}).get('results', []))
            else:
                logger.warning(f"Brave Search API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Brave Search web search error: {e}")
            return []
    
    def search_news(self, query: str, count: int = 10, freshness: str = 'pd') -> List[Dict[str, Any]]:
        """
        Search news using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return (max 20)
            freshness: Time range (pd=past day, pw=past week, pm=past month)
            
        Returns:
            List of news results
        """
        if not self.api_key:
            logger.warning("Brave Search API key not configured")
            return []
        
        try:
            self._rate_limit('news')
            
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': self.api_key
            }
            
            params = {
                'q': query,
                'count': min(count, 20),
                'offset': 0,
                'freshness': freshness,
                'textDecorations': False
            }
            
            response = requests.get(
                f'{self.base_url}/news/search',
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_news_results(data.get('results', []))
            else:
                logger.warning(f"Brave Search News API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Brave Search news search error: {e}")
            return []
    
    def search_profile_mentions(self, profile: str, symbols: Optional[List[str]] = None, 
                              days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for mentions of a financial profile across web and news.
        
        Args:
            profile: Profile name (e.g., 'Elon Musk', 'Cathie Wood')
            symbols: Optional stock symbols to include in search
            days_back: How many days back to search
            
        Returns:
            Combined web and news results
        """
        results = []
        
        # Build search queries
        queries = self._build_profile_queries(profile, symbols)
        
        # Set freshness based on days_back
        if days_back <= 1:
            freshness = 'pd'  # past day
        elif days_back <= 7:
            freshness = 'pw'  # past week
        else:
            freshness = 'pm'  # past month
        
        for query in queries[:3]:  # Limit to 3 queries to avoid rate limits
            try:
                # Search news
                news_results = self.search_news(query, count=5, freshness=freshness)
                for result in news_results:
                    result['search_query'] = query
                    result['search_type'] = 'news'
                results.extend(news_results)
                
                # Search web
                web_results = self.search_web(query, count=5)
                for result in web_results:
                    result['search_query'] = query
                    result['search_type'] = 'web'
                results.extend(web_results)
                
            except Exception as e:
                logger.warning(f"Error searching for query '{query}': {e}")
                continue
        
        # Remove duplicates and sort by relevance
        return self._deduplicate_and_rank(results, profile, symbols)
    
    def search_market_sentiment(self, symbols: List[str], time_range: str = 'pd') -> List[Dict[str, Any]]:
        """
        Search for market sentiment about specific symbols.
        
        Args:
            symbols: List of stock symbols
            time_range: Time range for search (pd, pw, pm)
            
        Returns:
            List of sentiment-related content
        """
        results = []
        
        for symbol in symbols[:5]:  # Limit to 5 symbols
            queries = [
                f'{symbol} stock sentiment analysis',
                f'{symbol} bullish bearish outlook',
                f'{symbol} price target upgrade downgrade',
                f'{symbol} institutional buying selling'
            ]
            
            for query in queries[:2]:  # 2 queries per symbol
                try:
                    news_results = self.search_news(query, count=3, freshness=time_range)
                    for result in news_results:
                        result['symbol'] = symbol
                        result['search_type'] = 'market_sentiment'
                    results.extend(news_results)
                    
                except Exception as e:
                    logger.warning(f"Error searching market sentiment for {symbol}: {e}")
                    continue
        
        return results
    
    def _build_profile_queries(self, profile: str, symbols: Optional[List[str]] = None) -> List[str]:
        """Build search queries for a financial profile."""
        queries = []
        
        # Profile name variations
        profile_lower = profile.lower()
        
        # Map common profiles to their real names and associations
        profile_mappings = {
            'elonmusk': ['Elon Musk', 'Tesla CEO', 'SpaceX'],
            'chamath': ['Chamath Palihapitiya', 'Social Capital', 'SPAC king'],
            'cathiedwood': ['Cathie Wood', 'ARK Invest', 'innovation investor'],
            'jimcramer': ['Jim Cramer', 'Mad Money', 'CNBC'],
            'garyblack00': ['Gary Black', 'Tesla analyst'],
            'reformedbroker': ['Josh Brown', 'Reformed Broker'],
            'teslacharts': ['Tesla Charts', 'Tesla analysis'],
            'unusual_whales': ['Unusual Whales', 'options flow'],
            'zerohedge': ['Zero Hedge', 'financial news'],
            'stockmktnewz': ['Stock Market News', 'trading news']
        }
        
        profile_terms = profile_mappings.get(profile_lower, [profile])
        
        # Base queries
        for term in profile_terms[:3]:  # Limit to 3 terms
            queries.append(f'"{term}" stock market')
            queries.append(f'"{term}" trading investment')
            
            if symbols:
                symbol_str = ' OR '.join(symbols[:3])  # Limit symbols
                queries.append(f'"{term}" {symbol_str}')
        
        # Financial context queries
        queries.extend([
            f'{profile} bullish bearish prediction',
            f'{profile} stock pick recommendation',
            f'{profile} market outlook sentiment'
        ])
        
        return queries[:8]  # Return max 8 queries
    
    def _process_web_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Process and normalize web search results."""
        processed = []
        
        for result in results:
            try:
                processed.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('description', ''),
                    'source': 'brave_web',
                    'date': datetime.now().isoformat(),  # Web results don't have dates
                    'text': f"{result.get('title', '')} {result.get('description', '')}",
                    'relevance_score': 0.7  # Default relevance for web results
                })
            except Exception as e:
                logger.warning(f"Error processing web result: {e}")
                continue
        
        return processed
    
    def _process_news_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Process and normalize news search results."""
        processed = []
        
        for result in results:
            try:
                # Parse date if available
                date_str = result.get('age', '')
                try:
                    # Brave returns relative dates like "2 hours ago"
                    date = self._parse_relative_date(date_str)
                except:
                    date = datetime.now().isoformat()
                
                processed.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('description', ''),
                    'source': 'brave_news',
                    'date': date,
                    'text': f"{result.get('title', '')} {result.get('description', '')}",
                    'relevance_score': 0.8,  # Higher relevance for news
                    'publisher': result.get('meta_url', {}).get('hostname', 'unknown')
                })
            except Exception as e:
                logger.warning(f"Error processing news result: {e}")
                continue
        
        return processed
    
    def _parse_relative_date(self, date_str: str) -> str:
        """Parse relative date strings like '2 hours ago' to ISO format."""
        try:
            now = datetime.now()
            date_str_lower = date_str.lower()
            
            if 'hour' in date_str_lower:
                hours = int(date_str_lower.split()[0])
                date = now - timedelta(hours=hours)
            elif 'day' in date_str_lower:
                days = int(date_str_lower.split()[0])
                date = now - timedelta(days=days)
            elif 'minute' in date_str_lower:
                minutes = int(date_str_lower.split()[0])
                date = now - timedelta(minutes=minutes)
            else:
                date = now
            
            return date.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _deduplicate_and_rank(self, results: List[Dict], profile: str, symbols: Optional[List[str]]) -> List[Dict]:
        """Remove duplicates and rank results by relevance."""
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                
                # Calculate relevance score
                relevance = self._calculate_relevance(result, profile, symbols)
                result['calculated_relevance'] = relevance
                
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.get('calculated_relevance', 0), reverse=True)
        
        return unique_results[:20]  # Return top 20 results
    
    def _calculate_relevance(self, result: Dict, profile: str, symbols: Optional[List[str]]) -> float:
        """Calculate relevance score for a search result."""
        score = result.get('relevance_score', 0.5)
        text = result.get('text', '').lower()
        
        # Boost for profile mentions
        if profile.lower() in text:
            score += 0.3
        
        # Boost for symbol mentions
        if symbols:
            for symbol in symbols:
                if symbol.lower() in text or f'${symbol}'.lower() in text:
                    score += 0.2
        
        # Boost for financial keywords
        financial_keywords = ['stock', 'trading', 'investment', 'market', 'bullish', 'bearish', 'price', 'target']
        keyword_count = sum(1 for keyword in financial_keywords if keyword in text)
        score += keyword_count * 0.1
        
        # Boost for news results
        if result.get('source') == 'brave_news':
            score += 0.1
        
        return min(1.0, score)
