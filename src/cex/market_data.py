"""
Market data functionality for centralized exchanges.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.types import Price, Candle, Exchange
from core.exceptions import ExchangeError
from core.utils import cache_result, retry_with_backoff
from .exchanges import get_exchange
from env import config

logger = logging.getLogger(__name__)


@cache_result(ttl=30)  # Cache for 30 seconds
@retry_with_backoff(max_retries=3)
async def get_price_data(
    symbol: str,
    vs_currency: str = "USD",
    include_24h_data: bool = True,
    exchange: Exchange = Exchange.BINANCE
) -> Dict[str, Any]:
    """
    Get current price data for a symbol.
    
    Args:
        symbol: Trading symbol
        vs_currency: Quote currency
        include_24h_data: Include 24h change data
        exchange: Exchange to get data from
    
    Returns:
        Price data dictionary
    """
    try:
        exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
        
        # Handle different symbol formats
        if '/' not in symbol and vs_currency:
            symbol = f"{symbol}/{vs_currency}"
        
        ticker = await exchange_client.get_ticker(symbol)
        
        price_data = {
            'symbol': symbol,
            'price': Decimal(str(ticker.get('last', 0))),
            'currency': vs_currency,
            'timestamp': datetime.utcnow(),
            'source': exchange.value
        }
        
        if include_24h_data:
            price_data.update({
                'change_24h': Decimal(str(ticker.get('change', 0))),
                'change_24h_percent': Decimal(str(ticker.get('percentage', 0))),
                'volume_24h': Decimal(str(ticker.get('quoteVolume', 0))),
                'high_24h': Decimal(str(ticker.get('high', 0))),
                'low_24h': Decimal(str(ticker.get('low', 0))),
                'open_24h': Decimal(str(ticker.get('open', 0)))
            })
        
        return price_data
    
    except Exception as e:
        logger.error(f"Failed to get price data for {symbol}: {e}")
        raise ExchangeError(f"Failed to fetch price data: {str(e)}")


@cache_result(ttl=60)  # Cache for 1 minute
async def get_market_overview(
    exchange: Exchange = Exchange.BINANCE,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get market overview with top cryptocurrencies.
    
    Args:
        exchange: Exchange to get data from
        limit: Number of top coins to include
    
    Returns:
        Market overview data
    """
    try:
        exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
        
        # Get all tickers
        tickers = await exchange_client.client.fetch_tickers()
        
        # Filter and sort by volume
        usdt_pairs = {k: v for k, v in tickers.items() if '/USDT' in k}
        sorted_pairs = sorted(
            usdt_pairs.items(), 
            key=lambda x: float(x[1].get('quoteVolume', 0)), 
            reverse=True
        )[:limit]
        
        market_data = []
        total_volume = Decimal('0')
        
        for symbol, ticker in sorted_pairs:
            price_info = {
                'symbol': symbol,
                'price': Decimal(str(ticker.get('last', 0))),
                'change_24h_percent': Decimal(str(ticker.get('percentage', 0))),
                'volume_24h': Decimal(str(ticker.get('quoteVolume', 0))),
                'high_24h': Decimal(str(ticker.get('high', 0))),
                'low_24h': Decimal(str(ticker.get('low', 0)))
            }
            market_data.append(price_info)
            total_volume += price_info['volume_24h']
        
        return {
            'exchange': exchange.value,
            'total_24h_volume': total_volume,
            'top_pairs': market_data,
            'timestamp': datetime.utcnow(),
            'count': len(market_data)
        }
    
    except Exception as e:
        logger.error(f"Failed to get market overview: {e}")
        raise ExchangeError(f"Failed to fetch market overview: {str(e)}")


@cache_result(ttl=300)  # Cache for 5 minutes
async def get_candles(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100,
    exchange: Exchange = Exchange.BINANCE
) -> List[Dict[str, Any]]:
    """
    Get OHLCV candle data for a symbol.
    
    Args:
        symbol: Trading symbol
        timeframe: Candle timeframe (1m, 5m, 1h, 1d, etc.)
        limit: Number of candles to fetch
        exchange: Exchange to get data from
    
    Returns:
        List of candle data
    """
    try:
        exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
        
        # Fetch OHLCV data
        ohlcv = await exchange_client.client.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        candles = []
        for candle_data in ohlcv:
            timestamp, open_price, high, low, close, volume = candle_data
            
            candle = {
                'symbol': symbol,
                'timestamp': datetime.fromtimestamp(timestamp / 1000),
                'open': Decimal(str(open_price)),
                'high': Decimal(str(high)),
                'low': Decimal(str(low)),
                'close': Decimal(str(close)),
                'volume': Decimal(str(volume)),
                'timeframe': timeframe
            }
            candles.append(candle)
        
        return candles
    
    except Exception as e:
        logger.error(f"Failed to get candles for {symbol}: {e}")
        raise ExchangeError(f"Failed to fetch candle data: {str(e)}")


async def get_order_book(
    symbol: str,
    depth: int = 20,
    exchange: Exchange = Exchange.BINANCE
) -> Dict[str, Any]:
    """
    Get order book data for a symbol.
    
    Args:
        symbol: Trading symbol
        depth: Order book depth
        exchange: Exchange to get data from
    
    Returns:
        Order book data
    """
    try:
        exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
        
        order_book = await exchange_client.client.fetch_order_book(symbol, depth)
        
        return {
            'symbol': symbol,
            'bids': [[Decimal(str(price)), Decimal(str(amount))] for price, amount in order_book['bids']],
            'asks': [[Decimal(str(price)), Decimal(str(amount))] for price, amount in order_book['asks']],
            'timestamp': datetime.utcnow(),
            'exchange': exchange.value
        }
    
    except Exception as e:
        logger.error(f"Failed to get order book for {symbol}: {e}")
        raise ExchangeError(f"Failed to fetch order book: {str(e)}")


async def get_trades(
    symbol: str,
    limit: int = 50,
    exchange: Exchange = Exchange.BINANCE
) -> List[Dict[str, Any]]:
    """
    Get recent trades for a symbol.
    
    Args:
        symbol: Trading symbol
        limit: Number of trades to fetch
        exchange: Exchange to get data from
    
    Returns:
        List of recent trades
    """
    try:
        exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
        
        trades = await exchange_client.client.fetch_trades(symbol, limit=limit)
        
        trade_data = []
        for trade in trades:
            trade_info = {
                'id': trade.get('id'),
                'timestamp': datetime.fromtimestamp(trade.get('timestamp', 0) / 1000),
                'symbol': symbol,
                'side': trade.get('side'),
                'amount': Decimal(str(trade.get('amount', 0))),
                'price': Decimal(str(trade.get('price', 0))),
                'cost': Decimal(str(trade.get('cost', 0)))
            }
            trade_data.append(trade_info)
        
        return trade_data
    
    except Exception as e:
        logger.error(f"Failed to get trades for {symbol}: {e}")
        raise ExchangeError(f"Failed to fetch trades: {str(e)}")


async def calculate_technical_indicators(
    symbol: str,
    timeframe: str = "1h",
    period: int = 14,
    exchange: Exchange = Exchange.BINANCE
) -> Dict[str, Any]:
    """
    Calculate basic technical indicators for a symbol.
    
    Args:
        symbol: Trading symbol
        timeframe: Candle timeframe
        period: Period for indicators
        exchange: Exchange to get data from
    
    Returns:
        Technical indicators
    """
    try:
        # Get candle data
        candles = await get_candles(symbol, timeframe, period * 2, exchange)
        
        if len(candles) < period:
            raise ValueError(f"Insufficient data for technical analysis (need {period}, got {len(candles)})")
        
        closes = [float(candle['close']) for candle in candles]
        highs = [float(candle['high']) for candle in candles]
        lows = [float(candle['low']) for candle in candles]
        
        # Simple Moving Average
        sma = sum(closes[-period:]) / period
        
        # RSI calculation (simplified)
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period if gains else 0
        avg_loss = sum(losses[-period:]) / period if losses else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Bollinger Bands (simplified)
        std_dev = (sum([(close - sma) ** 2 for close in closes[-period:]]) / period) ** 0.5
        upper_band = sma + (2 * std_dev)
        lower_band = sma - (2 * std_dev)
        
        # Support and Resistance (recent highs/lows)
        recent_high = max(highs[-period:])
        recent_low = min(lows[-period:])
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': closes[-1],
            'sma': Decimal(str(sma)),
            'rsi': Decimal(str(rsi)),
            'bollinger_upper': Decimal(str(upper_band)),
            'bollinger_lower': Decimal(str(lower_band)),
            'support': Decimal(str(recent_low)),
            'resistance': Decimal(str(recent_high)),
            'timestamp': datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to calculate technical indicators for {symbol}: {e}")
        raise ExchangeError(f"Failed to calculate technical indicators: {str(e)}")


async def get_funding_rate(
    symbol: str,
    exchange: Exchange = Exchange.BINANCE
) -> Dict[str, Any]:
    """
    Get funding rate for futures contracts.
    
    Args:
        symbol: Trading symbol
        exchange: Exchange to get data from
    
    Returns:
        Funding rate data
    """
    try:
        # This would be implemented for exchanges that support futures
        # For now, return placeholder data
        return {
            'symbol': symbol,
            'funding_rate': Decimal('0'),
            'next_funding_time': datetime.utcnow() + timedelta(hours=8),
            'exchange': exchange.value,
            'timestamp': datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to get funding rate for {symbol}: {e}")
        raise ExchangeError(f"Failed to fetch funding rate: {str(e)}")