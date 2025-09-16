"""
CryptoPanic news integration.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import httpx

from core.types import NewsItem, NewsSentiment
from core.exceptions import NewsError
from core.utils import retry_with_backoff, cache_result
from env import config

logger = logging.getLogger(__name__)


class CryptoPanicClient:
    """Client for CryptoPanic news API."""
    
    def __init__(self):
        self.base_url = config.CRYPTOPANIC_BASE_URL
        self.api_key = config.CRYPTOPANIC_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry_with_backoff(max_retries=3)
    @cache_result(ttl=300)  # Cache for 5 minutes
    async def get_news(
        self,
        coins: Optional[List[str]] = None,
        filter_sentiment: Optional[NewsSentiment] = None,
        limit: int = 20,
        hours_back: int = 24
    ) -> List[NewsItem]:
        """
        Get news from CryptoPanic API.
        
        Args:
            coins: List of coin symbols to filter by
            filter_sentiment: Filter by sentiment
            limit: Maximum number of news items
            hours_back: Hours to look back
        
        Returns:
            List of news items
        """
        try:
            if not self.api_key:
                raise NewsError("CryptoPanic API key not configured")
            
            params = {
                'auth_token': self.api_key,
                'public': 'true',
                'kind': 'news',
                'format': 'json'
            }
            
            if coins:
                params['currencies'] = ','.join(coins)
            
            if filter_sentiment:
                sentiment_map = {
                    NewsSentiment.POSITIVE: 'positive',
                    NewsSentiment.NEGATIVE: 'negative',
                    NewsSentiment.NEUTRAL: 'neutral'
                }
                params['filter'] = sentiment_map.get(filter_sentiment)
            
            response = await self.client.get(f"{self.base_url}/posts/", params=params)
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            for item in data.get('results', [])[:limit]:
                try:
                    # Parse published date
                    published_str = item.get('published_at', '')
                    published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    
                    # Check if within time window
                    if published_at < datetime.utcnow() - timedelta(hours=hours_back):
                        continue
                    
                    # Extract sentiment
                    votes = item.get('votes', {})
                    positive_votes = votes.get('positive', 0)
                    negative_votes = votes.get('negative', 0)
                    
                    if positive_votes > negative_votes:
                        sentiment = NewsSentiment.POSITIVE
                        sentiment_score = min(1.0, positive_votes / (positive_votes + negative_votes + 1))
                    elif negative_votes > positive_votes:
                        sentiment = NewsSentiment.NEGATIVE
                        sentiment_score = -min(1.0, negative_votes / (positive_votes + negative_votes + 1))
                    else:
                        sentiment = NewsSentiment.NEUTRAL
                        sentiment_score = 0.0
                    
                    # Extract mentioned coins
                    currencies = item.get('currencies', [])
                    coins_mentioned = [curr.get('code', '').upper() for curr in currencies if curr.get('code')]
                    
                    news_item = NewsItem(
                        id=str(item.get('id', '')),
                        title=item.get('title', ''),
                        content=item.get('title', ''),  # CryptoPanic doesn't provide full content
                        url=item.get('url', ''),
                        source=item.get('source', {}).get('domain', 'cryptopanic.com'),
                        published_at=published_at,
                        sentiment=sentiment,
                        sentiment_score=sentiment_score,
                        coins_mentioned=coins_mentioned,
                        impact_score=min(1.0, (positive_votes + negative_votes) / 100)  # Simple impact calculation
                    )
                    
                    news_items.append(news_item)
                
                except Exception as e:
                    logger.warning(f"Failed to parse news item: {e}")
                    continue
            
            return news_items
        
        except httpx.HTTPError as e:
            logger.error(f"CryptoPanic API request failed: {e}")
            raise NewsError(f"Failed to fetch news from CryptoPanic: {str(e)}")
        except Exception as e:
            logger.error(f"CryptoPanic news fetch failed: {e}")
            raise NewsError(f"CryptoPanic error: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    async def get_trending_news(self, limit: int = 10) -> List[NewsItem]:
        """Get trending news from CryptoPanic."""
        try:
            if not self.api_key:
                raise NewsError("CryptoPanic API key not configured")
            
            params = {
                'auth_token': self.api_key,
                'public': 'true',
                'kind': 'news',
                'filter': 'trending',
                'format': 'json'
            }
            
            response = await self.client.get(f"{self.base_url}/posts/", params=params)
            response.raise_for_status()
            
            data = response.json()
            return await self._parse_news_items(data.get('results', [])[:limit])
        
        except Exception as e:
            logger.error(f"Failed to get trending news: {e}")
            raise NewsError(f"Failed to fetch trending news: {str(e)}")
    
    async def _parse_news_items(self, items: List[Dict[str, Any]]) -> List[NewsItem]:
        """Parse news items from API response."""
        news_items = []
        
        for item in items:
            try:
                published_str = item.get('published_at', '')
                published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                
                votes = item.get('votes', {})
                positive_votes = votes.get('positive', 0)
                negative_votes = votes.get('negative', 0)
                
                if positive_votes > negative_votes:
                    sentiment = NewsSentiment.POSITIVE
                    sentiment_score = positive_votes / (positive_votes + negative_votes + 1)
                elif negative_votes > positive_votes:
                    sentiment = NewsSentiment.NEGATIVE
                    sentiment_score = -negative_votes / (positive_votes + negative_votes + 1)
                else:
                    sentiment = NewsSentiment.NEUTRAL
                    sentiment_score = 0.0
                
                currencies = item.get('currencies', [])
                coins_mentioned = [curr.get('code', '').upper() for curr in currencies if curr.get('code')]
                
                news_item = NewsItem(
                    id=str(item.get('id', '')),
                    title=item.get('title', ''),
                    content=item.get('title', ''),
                    url=item.get('url', ''),
                    source=item.get('source', {}).get('domain', 'cryptopanic.com'),
                    published_at=published_at,
                    sentiment=sentiment,
                    sentiment_score=sentiment_score,
                    coins_mentioned=coins_mentioned,
                    impact_score=min(1.0, (positive_votes + negative_votes) / 100)
                )
                
                news_items.append(news_item)
            
            except Exception as e:
                logger.warning(f"Failed to parse news item: {e}")
                continue
        
        return news_items
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_cryptopanic_client = CryptoPanicClient()


async def get_cryptopanic_news(
    coins: Optional[List[str]] = None,
    sentiment: Optional[NewsSentiment] = None,
    limit: int = 20,
    hours_back: int = 24
) -> List[NewsItem]:
    """Get news from CryptoPanic."""
    return await _cryptopanic_client.get_news(coins, sentiment, limit, hours_back)


async def get_trending_cryptopanic_news(limit: int = 10) -> List[NewsItem]:
    """Get trending news from CryptoPanic."""
    return await _cryptopanic_client.get_trending_news(limit)