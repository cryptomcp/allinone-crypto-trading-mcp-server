"""
Fear & Greed Index integration.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import httpx

from core.exceptions import NewsError
from core.utils import retry_with_backoff, cache_result
from env import config

logger = logging.getLogger(__name__)


class FearGreedClient:
    """Client for Fear & Greed Index API."""
    
    def __init__(self):
        self.base_url = config.FEARGREED_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry_with_backoff(max_retries=3)
    @cache_result(ttl=3600)  # Cache for 1 hour
    async def get_current_index(self) -> Dict[str, Any]:
        """
        Get current Fear & Greed Index.
        
        Returns:
            Current F&G index data
        """
        try:
            response = await self.client.get(self.base_url)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('data'):
                raise NewsError("No Fear & Greed Index data available")
            
            current = data['data'][0]
            
            value = int(current.get('value', 50))
            timestamp = int(current.get('timestamp', 0))
            
            # Classify the index
            if value <= 20:
                classification = "Extreme Fear"
                sentiment = "very_bearish"
            elif value <= 40:
                classification = "Fear"
                sentiment = "bearish"
            elif value <= 60:
                classification = "Neutral"
                sentiment = "neutral"
            elif value <= 80:
                classification = "Greed"
                sentiment = "bullish"
            else:
                classification = "Extreme Greed"
                sentiment = "very_bullish"
            
            return {
                'value': value,
                'classification': classification,
                'sentiment': sentiment,
                'timestamp': datetime.fromtimestamp(timestamp),
                'description': f"Market sentiment is currently showing {classification.lower()} with a score of {value}/100",
                'trading_suggestion': self._get_trading_suggestion(value),
                'source': 'alternative.me'
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Fear & Greed Index API request failed: {e}")
            raise NewsError(f"Failed to fetch Fear & Greed Index: {str(e)}")
        except Exception as e:
            logger.error(f"Fear & Greed Index fetch failed: {e}")
            raise NewsError(f"Fear & Greed Index error: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    @cache_result(ttl=7200)  # Cache for 2 hours
    async def get_historical_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical Fear & Greed Index data.
        
        Args:
            days: Number of days to look back
        
        Returns:
            Historical F&G index data
        """
        try:
            params = {'limit': days, 'format': 'json'}
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            historical_data = []
            
            for item in data.get('data', []):
                value = int(item.get('value', 50))
                timestamp = int(item.get('timestamp', 0))
                
                historical_data.append({
                    'value': value,
                    'timestamp': datetime.fromtimestamp(timestamp),
                    'classification': self._classify_value(value)
                })
            
            return historical_data
        
        except Exception as e:
            logger.error(f"Failed to get historical Fear & Greed data: {e}")
            raise NewsError(f"Failed to fetch historical data: {str(e)}")
    
    def _classify_value(self, value: int) -> str:
        """Classify Fear & Greed Index value."""
        if value <= 20:
            return "Extreme Fear"
        elif value <= 40:
            return "Fear"
        elif value <= 60:
            return "Neutral"
        elif value <= 80:
            return "Greed"
        else:
            return "Extreme Greed"
    
    def _get_trading_suggestion(self, value: int) -> str:
        """Get trading suggestion based on F&G value."""
        if value <= 20:
            return "Potential buying opportunity - market may be oversold"
        elif value <= 40:
            return "Consider accumulating positions - fear may be excessive"
        elif value <= 60:
            return "Balanced market conditions - follow trend"
        elif value <= 80:
            return "Consider taking profits - market showing greed"
        else:
            return "High risk environment - market may be overbought"
    
    async def get_sentiment_analysis(self) -> Dict[str, Any]:
        """Get comprehensive sentiment analysis."""
        try:
            current = await self.get_current_index()
            historical = await self.get_historical_data(7)  # Last 7 days
            
            # Calculate trends
            if len(historical) >= 2:
                recent_avg = sum(item['value'] for item in historical[:3]) / min(3, len(historical))
                older_avg = sum(item['value'] for item in historical[3:]) / max(1, len(historical) - 3)
                trend = "increasing" if recent_avg > older_avg else "decreasing"
                trend_strength = abs(recent_avg - older_avg)
            else:
                trend = "stable"
                trend_strength = 0
            
            return {
                'current': current,
                'trend': trend,
                'trend_strength': trend_strength,
                'weekly_average': sum(item['value'] for item in historical) / len(historical) if historical else current['value'],
                'volatility': self._calculate_volatility(historical),
                'recommendation': self._get_comprehensive_recommendation(current, trend, trend_strength)
            }
        
        except Exception as e:
            logger.error(f"Failed to get sentiment analysis: {e}")
            raise NewsError(f"Sentiment analysis failed: {str(e)}")
    
    def _calculate_volatility(self, historical: List[Dict[str, Any]]) -> float:
        """Calculate volatility of Fear & Greed Index."""
        if len(historical) < 2:
            return 0.0
        
        values = [item['value'] for item in historical]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _get_comprehensive_recommendation(self, current: Dict, trend: str, strength: float) -> str:
        """Get comprehensive trading recommendation."""
        value = current['value']
        
        if value <= 20:
            if trend == "decreasing":
                return "Strong buy signal - extreme fear with worsening sentiment"
            else:
                return "Buy signal - extreme fear but sentiment improving"
        elif value <= 40:
            if trend == "decreasing":
                return "Buy signal - fear increasing, potential opportunity"
            else:
                return "Hold/accumulate - fear present but improving"
        elif value <= 60:
            return f"Neutral - follow market trends, sentiment is {trend}"
        elif value <= 80:
            if trend == "increasing":
                return "Caution - greed increasing, consider reducing exposure"
            else:
                return "Hold - greed present but declining"
        else:
            if trend == "increasing":
                return "Strong sell signal - extreme greed with increasing sentiment"
            else:
                return "Sell signal - extreme greed but sentiment improving"
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_feargreed_client = FearGreedClient()


async def get_fear_greed_data() -> Dict[str, Any]:
    """Get current Fear & Greed Index data."""
    return await _feargreed_client.get_current_index()


async def get_fear_greed_history(days: int = 30) -> List[Dict[str, Any]]:
    """Get historical Fear & Greed Index data."""
    return await _feargreed_client.get_historical_data(days)


async def get_fear_greed_analysis() -> Dict[str, Any]:
    """Get comprehensive Fear & Greed sentiment analysis."""
    return await _feargreed_client.get_sentiment_analysis()