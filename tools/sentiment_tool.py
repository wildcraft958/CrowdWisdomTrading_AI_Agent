"""
Social sentiment analysis tool for X (Twitter) creators and general sentiment analysis.
"""
import os
import logging
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import time
import re
from urllib.parse import quote

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Sentiment analysis using free APIs and web scraping."""
    
    def __init__(self):
        self.twinword_key = os.getenv('TWINWORD_API_KEY')
        self.scrapingdog_key = os.getenv('SCRAPINGDOG_API_KEY')
        self.twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN')
        self.cache_dir = Path("data/cache/sentiment")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_profiles_sentiment(self, profile_list: List[str], symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment from social posts for specified profile list.
        
        Args:
            profile_list: List of X/Twitter usernames (with or without @)
            symbols: Optional list of stock symbols to filter content
        
        Returns:
            Dictionary with sentiment analysis results
        """
        logger.info(f"Analyzing sentiment for {len(profile_list)} profiles")
        
        results = {
            'profiles_analyzed': len(profile_list),
            'analysis_timestamp': datetime.now().isoformat(),
            'symbols_filter': symbols or [],
            'profile_results': {},
            'overall_sentiment': {},
            'errors': []
        }
        
        for profile in profile_list:
            try:
                profile_clean = profile.lstrip('@')
                logger.info(f"Analyzing profile: {profile_clean}")
                
                # Get recent posts for this profile
                posts = self._get_recent_posts(profile_clean, symbols)
                
                if not posts:
                    logger.warning(f"No posts found for {profile_clean}")
                    results['profile_results'][profile_clean] = {
                        'error': 'No posts found',
                        'post_count': 0,
                        'sentiment_score': 0
                    }
                    continue
                
                # Analyze sentiment for each post
                profile_sentiments = []
                for post in posts:
                    sentiment = self._analyze_text_sentiment(post['text'])
                    if sentiment:
                        sentiment['post_date'] = post.get('date', 'unknown')
                        sentiment['post_text'] = post['text'][:200] + '...' if len(post['text']) > 200 else post['text']
                        profile_sentiments.append(sentiment)
                
                # Calculate aggregate sentiment for profile
                if profile_sentiments:
                    avg_sentiment = self._calculate_average_sentiment(profile_sentiments)
                    results['profile_results'][profile_clean] = {
                        'post_count': len(profile_sentiments),
                        'average_sentiment': avg_sentiment,
                        'sentiment_distribution': self._get_sentiment_distribution(profile_sentiments),
                        'individual_posts': profile_sentiments[:5]  # Limit to 5 most recent
                    }
                else:
                    results['profile_results'][profile_clean] = {
                        'error': 'Failed to analyze sentiment',
                        'post_count': len(posts),
                        'sentiment_score': 0
                    }
                    
            except Exception as e:
                logger.error(f"Error analyzing profile {profile}: {e}")
                results['errors'].append(f"Profile {profile}: {str(e)}")
                results['profile_results'][profile] = {'error': str(e)}
        
        # Calculate overall sentiment
        results['overall_sentiment'] = self._calculate_overall_sentiment(results['profile_results'])
        
        # Cache results
        self._cache_results(results, profile_list)
        
        return results
    
    def _get_recent_posts(self, username: str, symbols: Optional[List[str]] = None, max_posts: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent posts from a user. This is a simplified version that would need
        proper API integration or web scraping in production.
        """
        cache_file = self.cache_dir / f"{username}_posts.json"
        
        # Check cache first
        if cache_file.exists() and self._is_cache_fresh(cache_file, hours=2):
            logger.info(f"Using cached posts for {username}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        posts = []
        
        # Method 1: Try Twitter API if available
        if self.twitter_bearer:
            posts = self._fetch_twitter_posts(username, symbols, max_posts)
        
        # Method 2: Try web scraping as fallback
        if not posts and self.scrapingdog_key:
            posts = self._scrape_twitter_posts(username, symbols, max_posts)
        
        # Method 3: Generate mock data for testing (remove in production)
        if not posts:
            logger.warning(f"No real posts found for {username}, generating mock data for testing")
            posts = self._generate_mock_posts(username, symbols, max_posts)
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(posts, f, indent=2, default=str)
        
        return posts
    
    def _fetch_twitter_posts(self, username: str, symbols: Optional[List[str]], max_posts: int) -> List[Dict[str, Any]]:
        """Fetch posts using Twitter API v2."""
        if not self.twitter_bearer:
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.twitter_bearer}'}
            
            # Get user ID first
            user_url = f"https://api.twitter.com/2/users/by/username/{username}"
            user_response = requests.get(user_url, headers=headers)
            
            if user_response.status_code != 200:
                logger.warning(f"Failed to get user ID for {username}: {user_response.status_code}")
                return []
            
            user_id = user_response.json()['data']['id']
            
            # Get user tweets
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': min(max_posts, 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations'
            }
            
            response = requests.get(tweets_url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch tweets for {username}: {response.status_code}")
                return []
            
            data = response.json()
            posts = []
            
            for tweet in data.get('data', []):
                # Filter by symbols if provided
                if symbols:
                    tweet_text = tweet['text'].upper()
                    if not any(f"${symbol}" in tweet_text or f" {symbol} " in tweet_text for symbol in symbols):
                        continue
                
                posts.append({
                    'text': tweet['text'],
                    'date': tweet.get('created_at', ''),
                    'metrics': tweet.get('public_metrics', {}),
                    'source': 'twitter_api'
                })
            
            logger.info(f"Fetched {len(posts)} posts from Twitter API for {username}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching Twitter posts for {username}: {e}")
            return []
    
    def _scrape_twitter_posts(self, username: str, symbols: Optional[List[str]], max_posts: int) -> List[Dict[str, Any]]:
        """Scrape posts using ScrapingDog or similar service."""
        if not self.scrapingdog_key:
            return []
        
        try:
            # This is a simplified example - actual implementation would need
            # proper URL construction and HTML parsing
            url = f"https://twitter.com/{username}"
            scraping_url = f"https://api.scrapingdog.com/scrape"
            
            params = {
                'api_key': self.scrapingdog_key,
                'url': url,
                'dynamic': 'false'
            }
            
            response = requests.get(scraping_url, params=params)
            
            if response.status_code == 200:
                # Parse HTML and extract tweets (simplified)
                # In production, you'd use BeautifulSoup or similar to parse
                posts = self._parse_twitter_html(response.text, symbols, max_posts)
                logger.info(f"Scraped {len(posts)} posts for {username}")
                return posts
            else:
                logger.warning(f"Scraping failed for {username}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping posts for {username}: {e}")
            return []
    
    def _parse_twitter_html(self, html: str, symbols: Optional[List[str]], max_posts: int) -> List[Dict[str, Any]]:
        """Parse Twitter HTML to extract posts (simplified)."""
        # This is a placeholder - real implementation would use BeautifulSoup
        # to properly parse the HTML and extract tweet content
        return []
    
    def _generate_mock_posts(self, username: str, symbols: Optional[List[str]], max_posts: int) -> List[Dict[str, Any]]:
        """Generate mock posts for testing purposes."""
        mock_templates = [
            "Watching ${symbol} closely today. The technicals look interesting 📈",
            "Big volume on ${symbol} - something brewing here? 🤔",
            "${symbol} breaking out of resistance. Time to pay attention! 🚀",
            "Earnings week for ${symbol}. Expecting volatility ahead ⚡",
            "Love the long-term story on ${symbol}. Building position gradually 💪",
            "Market sentiment shifting on ${symbol}. Bears getting nervous? 🐻",
            "${symbol} chart looking clean. Potential breakout setup forming 📊",
            "Insider activity on ${symbol} worth noting. Following closely 👀",
            "Risk/reward favorable on ${symbol} at these levels 💎",
            "Multiple catalysts lining up for ${symbol} in Q4 🎯"
        ]
        
        posts = []
        for i in range(min(max_posts, len(mock_templates))):
            symbol = symbols[i % len(symbols)] if symbols else "SPY"
            text = mock_templates[i].replace("${symbol}", f"${symbol}")
            
            posts.append({
                'text': text,
                'date': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                'source': 'mock_data',
                'username': username
            })
        
        logger.info(f"Generated {len(posts)} mock posts for {username}")
        return posts
    
    def _analyze_text_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment of a single text using available APIs."""
        
        # Method 1: Try Twinword API
        if self.twinword_key:
            twinword_result = self._analyze_with_twinword(text)
            if twinword_result:
                return twinword_result
        
        # Method 2: Fallback to simple rule-based analysis
        return self._analyze_with_rules(text)
    
    def _analyze_with_twinword(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment using Twinword API."""
        try:
            endpoint = "https://api.twinword.com/v6/sentiment/"
            
            params = {
                'text': text,
                'key': self.twinword_key
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'sentiment': data.get('type', 'neutral'),
                    'score': data.get('score', 0),
                    'confidence': data.get('ratio', 0.5),
                    'source': 'twinword'
                }
            else:
                logger.warning(f"Twinword API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Twinword sentiment analysis: {e}")
            return None
    
    def _analyze_with_rules(self, text: str) -> Dict[str, Any]:
        """Simple rule-based sentiment analysis as fallback."""
        positive_words = [
            'bullish', 'buy', 'long', 'up', 'green', 'moon', 'rocket', 'gain',
            'profit', 'strong', 'good', 'great', 'excellent', 'love', 'like',
            'breakout', 'rally', 'surge', 'pump', 'bull', 'calls'
        ]
        
        negative_words = [
            'bearish', 'sell', 'short', 'down', 'red', 'crash', 'dump', 'loss',
            'weak', 'bad', 'terrible', 'hate', 'avoid', 'breakdown', 'fall',
            'drop', 'bear', 'puts', 'decline', 'correction'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = max(-0.8, -0.5 - (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            score = 0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': 0.6 if sentiment != 'neutral' else 0.3,
            'source': 'rule_based',
            'positive_signals': positive_count,
            'negative_signals': negative_count
        }
    
    def _calculate_average_sentiment(self, sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average sentiment from a list of sentiment analyses."""
        if not sentiments:
            return {'score': 0, 'sentiment': 'neutral', 'confidence': 0}
        
        total_score = sum(s.get('score', 0) for s in sentiments)
        avg_score = total_score / len(sentiments)
        
        avg_confidence = sum(s.get('confidence', 0) for s in sentiments) / len(sentiments)
        
        if avg_score > 0.1:
            avg_sentiment = 'positive'
        elif avg_score < -0.1:
            avg_sentiment = 'negative'
        else:
            avg_sentiment = 'neutral'
        
        return {
            'score': round(avg_score, 3),
            'sentiment': avg_sentiment,
            'confidence': round(avg_confidence, 3),
            'sample_size': len(sentiments)
        }
    
    def _get_sentiment_distribution(self, sentiments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of sentiment types."""
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for sentiment in sentiments:
            sentiment_type = sentiment.get('sentiment', 'neutral')
            if sentiment_type in distribution:
                distribution[sentiment_type] += 1
        
        return distribution
    
    def _calculate_overall_sentiment(self, profile_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall sentiment across all profiles."""
        all_scores = []
        all_post_counts = []
        
        for profile, data in profile_results.items():
            if 'error' not in data and 'average_sentiment' in data:
                score = data['average_sentiment'].get('score', 0)
                post_count = data.get('post_count', 0)
                all_scores.append(score)
                all_post_counts.append(post_count)
        
        if not all_scores:
            return {'score': 0, 'sentiment': 'neutral', 'confidence': 0}
        
        # Weight by post count
        weighted_score = sum(score * count for score, count in zip(all_scores, all_post_counts))
        total_posts = sum(all_post_counts)
        
        if total_posts > 0:
            overall_score = weighted_score / total_posts
        else:
            overall_score = sum(all_scores) / len(all_scores)
        
        if overall_score > 0.1:
            overall_sentiment = 'positive'
        elif overall_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'score': round(overall_score, 3),
            'sentiment': overall_sentiment,
            'profiles_analyzed': len([p for p in profile_results.values() if 'error' not in p]),
            'total_posts': total_posts
        }
    
    def _cache_results(self, results: Dict[str, Any], profile_list: List[str]):
        """Cache sentiment analysis results."""
        cache_file = self.cache_dir / f"sentiment_{'_'.join(profile_list[:3])}_{datetime.now().strftime('%Y%m%d_%H')}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _is_cache_fresh(self, cache_file: Path, hours: int = 2) -> bool:
        """Check if cache file is fresh enough."""
        if not cache_file.exists():
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age < timedelta(hours=hours)

def analyze_profiles_sentiment(profile_list: List[str], symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Main function to analyze sentiment from social profiles.
    
    Args:
        profile_list: List of social media usernames
        symbols: Optional list of stock symbols to filter content
    
    Returns:
        Sentiment analysis results
    """
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_profiles_sentiment(profile_list, symbols)

if __name__ == "__main__":
    # Test the sentiment tool
    test_profiles = ["@elonmusk", "@chamath", "@cathiedwood"]
    test_symbols = ["TSLA", "AAPL"]
    
    print("Testing sentiment analysis...")
    results = analyze_profiles_sentiment(test_profiles, test_symbols)
    print(json.dumps(results, indent=2, default=str))
