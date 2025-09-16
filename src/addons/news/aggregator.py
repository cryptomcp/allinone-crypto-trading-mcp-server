"""
News aggregation and sentiment analysis.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.types import NewsItem, NewsSentiment
from core.exceptions import NewsError
from .cryptopanic_tools import get_cryptopanic_news
from .feargreed_tools import get_fear_greed_data

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Aggregates news from multiple sources."""
    
    def __init__(self):
        self.sources = ['cryptopanic']  # Add more sources as needed
    
    async def get_combined_news(
        self,
        coins: Optional[List[str]] = None,
        sentiment: Optional[NewsSentiment] = None,
        limit: int = 50,
        hours_back: int = 24
    ) -> List[NewsItem]:
        """
        Get news from all available sources.
        
        Args:
            coins: Filter by specific coins
            sentiment: Filter by sentiment
            limit: Maximum number of news items
            hours_back: Hours to look back
        
        Returns:
            Combined list of news items
        """
        all_news = []
        
        try:
            # Get CryptoPanic news
            cryptopanic_news = await get_cryptopanic_news(coins, sentiment, limit, hours_back)
            all_news.extend(cryptopanic_news)
            
            # Add other news sources here as they're implemented
            # dappier_news = await get_dappier_news(...)
            # all_news.extend(dappier_news)
            
        except Exception as e:
            logger.warning(f"Failed to fetch news from some sources: {e}")
        
        # Sort by published date (newest first)
        all_news.sort(key=lambda x: x.published_at, reverse=True)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_news = []
        for news in all_news:
            if news.url not in seen_urls:
                seen_urls.add(news.url)
                unique_news.append(news)
        
        return unique_news[:limit]
    
    async def analyze_sentiment_summary(
        self,
        coins: Optional[List[str]] = None,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze overall sentiment from recent news.
        
        Args:
            coins: Filter by specific coins
            hours_back: Hours to look back
        
        Returns:
            Sentiment analysis summary
        """
        try:
            # Get recent news
            news_items = await self.get_combined_news(coins=coins, hours_back=hours_back, limit=100)
            
            if not news_items:
                return {
                    'total_articles': 0,
                    'sentiment_distribution': {},
                    'average_sentiment': 0.0,
                    'dominant_sentiment': 'neutral',
                    'confidence': 0.0
                }
            
            # Analyze sentiment distribution
            sentiment_counts = {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'mixed': 0
            }
            
            sentiment_scores = []
            
            for news in news_items:
                sentiment_counts[news.sentiment.value] += 1
                if news.sentiment_score is not None:
                    sentiment_scores.append(news.sentiment_score)
            
            # Calculate averages
            total_articles = len(news_items)
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
            
            # Determine dominant sentiment
            dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            confidence = sentiment_counts[dominant_sentiment] / total_articles
            
            # Get Fear & Greed Index for context
            try:
                fng_data = await get_fear_greed_data()
                market_sentiment = {
                    'fear_greed_index': fng_data['value'],
                    'fear_greed_classification': fng_data['classification'],
                    'fear_greed_sentiment': fng_data['sentiment']
                }
            except Exception:
                market_sentiment = None
            
            return {
                'total_articles': total_articles,
                'sentiment_distribution': sentiment_counts,
                'sentiment_percentages': {
                    k: (v / total_articles * 100) for k, v in sentiment_counts.items()
                },
                'average_sentiment': avg_sentiment,
                'dominant_sentiment': dominant_sentiment,
                'confidence': confidence,
                'market_sentiment': market_sentiment,
                'analysis_period_hours': hours_back,
                'timestamp': datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            raise NewsError(f"Sentiment analysis failed: {str(e)}")
    
    async def get_coin_specific_sentiment(
        self,
        coin: str,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Get sentiment analysis for a specific coin.
        
        Args:
            coin: Coin symbol (e.g., 'BTC', 'ETH')
            hours_back: Hours to look back
        
        Returns:
            Coin-specific sentiment analysis
        """
        try:
            # Get news mentioning the specific coin
            news_items = await self.get_combined_news(coins=[coin.upper()], hours_back=hours_back)
            
            if not news_items:
                return {
                    'coin': coin.upper(),
                    'total_articles': 0,
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'recent_headlines': []
                }
            
            # Analyze sentiment
            positive_count = sum(1 for news in news_items if news.sentiment == NewsSentiment.POSITIVE)
            negative_count = sum(1 for news in news_items if news.sentiment == NewsSentiment.NEGATIVE)
            neutral_count = len(news_items) - positive_count - negative_count
            
            total = len(news_items)
            
            # Determine overall sentiment
            if positive_count > negative_count and positive_count > neutral_count:
                overall_sentiment = 'positive'
                confidence = positive_count / total
            elif negative_count > positive_count and negative_count > neutral_count:
                overall_sentiment = 'negative'
                confidence = negative_count / total
            else:
                overall_sentiment = 'neutral'
                confidence = neutral_count / total
            
            # Get recent headlines
            recent_headlines = [
                {
                    'title': news.title,
                    'sentiment': news.sentiment.value,
                    'published_at': news.published_at,
                    'source': news.source,
                    'url': news.url
                }
                for news in news_items[:10]
            ]
            
            return {
                'coin': coin.upper(),
                'total_articles': total,
                'sentiment': overall_sentiment,
                'confidence': confidence,
                'sentiment_breakdown': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'neutral': neutral_count
                },
                'recent_headlines': recent_headlines,
                'analysis_period_hours': hours_back,
                'timestamp': datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze sentiment for {coin}: {e}")
            raise NewsError(f"Coin sentiment analysis failed: {str(e)}")


# Global aggregator instance
_news_aggregator = NewsAggregator()


async def get_news_feed(
    coins: Optional[List[str]] = None,
    sentiment: Optional[NewsSentiment] = None,
    limit: int = 20,
    hours_back: int = 24
) -> List[NewsItem]:
    """Get aggregated news feed."""
    return await _news_aggregator.get_combined_news(coins, sentiment, limit, hours_back)


async def analyze_sentiment(
    coins: Optional[List[str]] = None,
    hours_back: int = 24
) -> Dict[str, Any]:
    """Analyze overall market sentiment from news."""
    return await _news_aggregator.analyze_sentiment_summary(coins, hours_back)


async def get_coin_sentiment(coin: str, hours_back: int = 24) -> Dict[str, Any]:
    """Get sentiment analysis for a specific coin."""
    return await _news_aggregator.get_coin_specific_sentiment(coin, hours_back)