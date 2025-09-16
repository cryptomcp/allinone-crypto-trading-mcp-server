"""
Pyth Network price feed integration.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx

from core.exceptions import BlockchainError
from core.utils import retry_with_backoff, cache_result
from env import config

logger = logging.getLogger(__name__)


class PythClient:
    """Pyth Network price feed client."""
    
    def __init__(self):
        self.base_url = config.PYTH_NETWORK_URL
        self.api_key = config.PYTH_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry_with_backoff(max_retries=3)
    @cache_result(ttl=10)  # Cache for 10 seconds
    async def get_price(self, price_feed_id: str) -> Dict[str, Any]:
        """
        Get real-time price from Pyth Network.
        
        Args:
            price_feed_id: Pyth price feed ID
        
        Returns:
            Price data with confidence intervals
        """
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = await self.client.get(
                f"{self.base_url}/api/latest_price_feeds",
                params={'ids[]': price_feed_id},
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data or not data[0].get('price'):
                raise BlockchainError(f"No price data for feed {price_feed_id}")
            
            price_data = data[0]['price']
            
            # Convert price with proper scaling
            price = Decimal(price_data['price']) / Decimal(10 ** abs(price_data['expo']))
            confidence = Decimal(price_data['conf']) / Decimal(10 ** abs(price_data['expo']))
            
            return {
                'price_feed_id': price_feed_id,
                'price': price,
                'confidence': confidence,
                'publish_time': datetime.fromtimestamp(price_data['publish_time']),
                'prev_price': Decimal(price_data.get('prev_price', price_data['price'])) / Decimal(10 ** abs(price_data['expo'])),
                'prev_publish_time': datetime.fromtimestamp(price_data.get('prev_publish_time', price_data['publish_time']))
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Pyth API request failed: {e}")
            raise BlockchainError(f"Pyth price fetch failed: {str(e)}")
        except Exception as e:
            logger.error(f"Pyth price fetch failed: {e}")
            raise BlockchainError(f"Pyth error: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    async def get_multiple_prices(self, price_feed_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get multiple prices at once."""
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Build query params for multiple IDs
            params = []
            for feed_id in price_feed_ids:
                params.append(('ids[]', feed_id))
            
            response = await self.client.get(
                f"{self.base_url}/api/latest_price_feeds",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            prices = {}
            
            for item in data:
                if item.get('price'):
                    price_data = item['price']
                    feed_id = item['id']
                    
                    price = Decimal(price_data['price']) / Decimal(10 ** abs(price_data['expo']))
                    confidence = Decimal(price_data['conf']) / Decimal(10 ** abs(price_data['expo']))
                    
                    prices[feed_id] = {
                        'price': price,
                        'confidence': confidence,
                        'publish_time': datetime.fromtimestamp(price_data['publish_time'])
                    }
            
            return prices
        
        except Exception as e:
            logger.error(f"Pyth multiple prices fetch failed: {e}")
            raise BlockchainError(f"Pyth multiple prices failed: {str(e)}")
    
    async def get_price_feeds(self, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available price feeds."""
        try:
            response = await self.client.get(f"{self.base_url}/api/price_feeds")
            response.raise_for_status()
            
            feeds = response.json()
            
            if asset_type:
                feeds = [feed for feed in feeds if feed.get('asset_type') == asset_type]
            
            return feeds
        
        except Exception as e:
            logger.error(f"Failed to get price feeds: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Common Pyth price feed IDs
PYTH_FEEDS = {
    'BTC/USD': 'e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43',
    'ETH/USD': 'ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace',
    'SOL/USD': 'ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d',
    'USDC/USD': 'eaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a',
    'USDT/USD': '2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca5e58e59c1c7b6e5f2b7b95c8c'
}


# Global client instance
_pyth_client = PythClient()


async def get_pyth_price(symbol: str) -> Dict[str, Any]:
    """Get Pyth price for a symbol."""
    try:
        feed_id = PYTH_FEEDS.get(symbol.upper())
        if not feed_id:
            raise BlockchainError(f"No Pyth feed available for {symbol}")
        
        return await _pyth_client.get_price(feed_id)
    
    except Exception as e:
        logger.error(f"Failed to get Pyth price for {symbol}: {e}")
        raise


async def get_multiple_pyth_prices(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Get multiple Pyth prices."""
    try:
        feed_ids = []
        symbol_to_feed = {}
        
        for symbol in symbols:
            feed_id = PYTH_FEEDS.get(symbol.upper())
            if feed_id:
                feed_ids.append(feed_id)
                symbol_to_feed[feed_id] = symbol.upper()
        
        if not feed_ids:
            return {}
        
        feed_prices = await _pyth_client.get_multiple_prices(feed_ids)
        
        # Convert back to symbol-based mapping
        symbol_prices = {}
        for feed_id, price_data in feed_prices.items():
            symbol = symbol_to_feed.get(feed_id)
            if symbol:
                symbol_prices[symbol] = price_data
        
        return symbol_prices
    
    except Exception as e:
        logger.error(f"Failed to get multiple Pyth prices: {e}")
        return {}