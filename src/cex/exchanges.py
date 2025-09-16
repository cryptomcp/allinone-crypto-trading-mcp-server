"""
Centralized exchange base classes and implementations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime

import ccxt.async_support as ccxt
from ccxt.base.errors import BaseError as CCXTError

from core.types import Balance, Order, OrderSide, OrderType, OrderStatus, Exchange, TradingPair
from core.exceptions import ExchangeError, AuthenticationError, InsufficientFundsError
from core.utils import retry_with_backoff, rate_limit
from env import config

logger = logging.getLogger(__name__)


class BaseExchange(ABC):
    """Base class for all exchange implementations."""
    
    def __init__(self, exchange_id: Exchange, testnet: bool = True):
        self.exchange_id = exchange_id
        self.testnet = testnet
        self.client: Optional[ccxt.Exchange] = None
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the exchange connection."""
        pass
    
    @abstractmethod
    async def get_balance(self, currency: Optional[str] = None) -> List[Balance]:
        """Get account balances."""
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: Decimal,
        order_type: OrderType,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
    ) -> Order:
        """Place a trading order."""
        pass
    
    @abstractmethod
    async def get_orders(self, symbol: Optional[str] = None, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders (open, filled, cancelled)."""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol."""
        pass
    
    async def close(self) -> None:
        """Close the exchange connection."""
        if self.client:
            await self.client.close()


class BinanceExchange(BaseExchange):
    """Binance exchange implementation."""
    
    def __init__(self, testnet: bool = True):
        super().__init__(Exchange.BINANCE, testnet)
    
    async def initialize(self) -> None:
        """Initialize Binance connection."""
        try:
            api_key = config.BINANCE_API_KEY
            secret = config.BINANCE_SECRET_KEY
            
            if not api_key or not secret:
                raise AuthenticationError("Binance API credentials not configured")
            
            self.client = ccxt.binance({
                'apiKey': api_key,
                'secret': secret,
                'sandbox': self.testnet or config.BINANCE_TESTNET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # spot, margin, future, delivery
                }
            })
            
            # Test connection
            await self.client.fetch_balance()
            self._initialized = True
            logger.info(f"Binance exchange initialized (testnet: {self.testnet})")
        
        except Exception as e:
            logger.error(f"Failed to initialize Binance: {e}")
            raise ExchangeError(f"Binance initialization failed: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    @rate_limit(max_calls=1200, time_window=60)  # Binance rate limit
    async def get_balance(self, currency: Optional[str] = None) -> List[Balance]:
        """Get Binance account balances."""
        if not self._initialized:
            await self.initialize()
        
        try:
            balance_data = await self.client.fetch_balance()
            balances = []
            
            for symbol, data in balance_data.get('info', {}).get('balances', []):
                if isinstance(data, dict):
                    free = Decimal(str(data.get('free', '0')))
                    locked = Decimal(str(data.get('locked', '0')))
                    total = free + locked
                    
                    if currency and symbol.upper() != currency.upper():
                        continue
                    
                    if total > 0:  # Only include non-zero balances
                        balances.append(Balance(
                            currency=symbol.upper(),
                            total=total,
                            available=free,
                            locked=locked,
                            exchange=self.exchange_id
                        ))
            
            return balances
        
        except CCXTError as e:
            logger.error(f"Binance balance fetch failed: {e}")
            raise ExchangeError(f"Failed to fetch Binance balance: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    @rate_limit(max_calls=1200, time_window=60)
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: Decimal,
        order_type: OrderType,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
    ) -> Order:
        """Place order on Binance."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert order type to Binance format
            binance_type = self._convert_order_type(order_type)
            
            params = {}
            if order_type == OrderType.STOP_LOSS and stop_price:
                params['stopPrice'] = float(stop_price)
            
            order_data = await self.client.create_order(
                symbol=symbol,
                type=binance_type,
                side=side.value,
                amount=float(amount),
                price=float(price) if price else None,
                params=params
            )
            
            return self._convert_order_response(order_data, symbol)
        
        except CCXTError as e:
            logger.error(f"Binance order placement failed: {e}")
            if "insufficient balance" in str(e).lower():
                raise InsufficientFundsError(f"Insufficient balance for order: {str(e)}")
            raise ExchangeError(f"Failed to place Binance order: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    @rate_limit(max_calls=1200, time_window=60)
    async def get_orders(self, symbol: Optional[str] = None, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders from Binance."""
        if not self._initialized:
            await self.initialize()
        
        try:
            if symbol:
                orders_data = await self.client.fetch_orders(symbol)
            else:
                orders_data = await self.client.fetch_orders()
            
            orders = []
            for order_data in orders_data:
                order = self._convert_order_response(order_data, order_data.get('symbol', ''))
                
                if status and order.status != status:
                    continue
                
                orders.append(order)
            
            return orders
        
        except CCXTError as e:
            logger.error(f"Binance orders fetch failed: {e}")
            raise ExchangeError(f"Failed to fetch Binance orders: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    @rate_limit(max_calls=1200, time_window=60)
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order on Binance."""
        if not self._initialized:
            await self.initialize()
        
        try:
            await self.client.cancel_order(order_id, symbol)
            return True
        
        except CCXTError as e:
            logger.error(f"Binance order cancellation failed: {e}")
            raise ExchangeError(f"Failed to cancel Binance order: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    @rate_limit(max_calls=1200, time_window=60)
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data from Binance."""
        if not self._initialized:
            await self.initialize()
        
        try:
            return await self.client.fetch_ticker(symbol)
        
        except CCXTError as e:
            logger.error(f"Binance ticker fetch failed: {e}")
            raise ExchangeError(f"Failed to fetch Binance ticker: {str(e)}")
    
    def _convert_order_type(self, order_type: OrderType) -> str:
        """Convert OrderType to Binance format."""
        mapping = {
            OrderType.MARKET: 'market',
            OrderType.LIMIT: 'limit',
            OrderType.STOP_LOSS: 'stop_loss',
            OrderType.TAKE_PROFIT: 'take_profit',
            OrderType.STOP_LIMIT: 'stop_loss_limit',
        }
        return mapping.get(order_type, 'market')
    
    def _convert_order_response(self, order_data: Dict[str, Any], symbol: str) -> Order:
        """Convert Binance order response to Order model."""
        status_mapping = {
            'NEW': OrderStatus.OPEN,
            'PARTIALLY_FILLED': OrderStatus.PARTIALLY_FILLED,
            'FILLED': OrderStatus.FILLED,
            'CANCELED': OrderStatus.CANCELLED,
            'REJECTED': OrderStatus.REJECTED,
            'EXPIRED': OrderStatus.EXPIRED,
        }
        
        return Order(
            id=str(order_data.get('id', '')),
            symbol=symbol,
            side=OrderSide(order_data.get('side', 'buy').lower()),
            order_type=OrderType.MARKET,  # Simplified for now
            amount=Decimal(str(order_data.get('amount', '0'))),
            price=Decimal(str(order_data.get('price', '0'))) if order_data.get('price') else None,
            status=status_mapping.get(order_data.get('status', 'NEW'), OrderStatus.OPEN),
            exchange=self.exchange_id,
            filled_amount=Decimal(str(order_data.get('filled', '0'))),
            fee=Decimal(str(order_data.get('fee', {}).get('cost', '0'))),
            fee_currency=order_data.get('fee', {}).get('currency'),
            created_at=datetime.fromtimestamp(order_data.get('timestamp', 0) / 1000) if order_data.get('timestamp') else datetime.utcnow()
        )


class CoinbaseExchange(BaseExchange):
    """Coinbase Pro exchange implementation."""
    
    def __init__(self, testnet: bool = True):
        super().__init__(Exchange.COINBASE, testnet)
    
    async def initialize(self) -> None:
        """Initialize Coinbase Pro connection."""
        try:
            api_key = config.COINBASE_API_KEY
            secret = config.COINBASE_SECRET_KEY
            passphrase = config.COINBASE_PASSPHRASE
            
            if not all([api_key, secret, passphrase]):
                raise AuthenticationError("Coinbase Pro API credentials not configured")
            
            self.client = ccxt.coinbasepro({
                'apiKey': api_key,
                'secret': secret,
                'password': passphrase,
                'sandbox': self.testnet or config.COINBASE_SANDBOX,
                'enableRateLimit': True,
            })
            
            # Test connection
            await self.client.fetch_balance()
            self._initialized = True
            logger.info(f"Coinbase Pro exchange initialized (testnet: {self.testnet})")
        
        except Exception as e:
            logger.error(f"Failed to initialize Coinbase Pro: {e}")
            raise ExchangeError(f"Coinbase Pro initialization failed: {str(e)}")
    
    # Implement similar methods as Binance...
    async def get_balance(self, currency: Optional[str] = None) -> List[Balance]:
        """Get Coinbase Pro account balances."""
        # Implementation similar to Binance
        pass
    
    async def place_order(self, symbol: str, side: OrderSide, amount: Decimal, order_type: OrderType, price: Optional[Decimal] = None, stop_price: Optional[Decimal] = None) -> Order:
        """Place order on Coinbase Pro."""
        # Implementation similar to Binance
        pass
    
    async def get_orders(self, symbol: Optional[str] = None, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders from Coinbase Pro."""
        # Implementation similar to Binance
        pass
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order on Coinbase Pro."""
        # Implementation similar to Binance
        pass
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data from Coinbase Pro."""
        # Implementation similar to Binance
        pass


# Exchange factory
class ExchangeFactory:
    """Factory for creating exchange instances."""
    
    _exchanges = {
        Exchange.BINANCE: BinanceExchange,
        Exchange.COINBASE: CoinbaseExchange,
        # Add other exchanges as needed
    }
    
    @classmethod
    async def create_exchange(cls, exchange_id: Exchange, testnet: bool = True) -> BaseExchange:
        """Create and initialize an exchange instance."""
        if exchange_id not in cls._exchanges:
            raise ValueError(f"Unsupported exchange: {exchange_id}")
        
        exchange_class = cls._exchanges[exchange_id]
        exchange = exchange_class(testnet=testnet)
        await exchange.initialize()
        return exchange


# Global exchange instances cache
_exchange_cache: Dict[str, BaseExchange] = {}


async def get_exchange(exchange_id: Exchange, testnet: bool = True) -> BaseExchange:
    """Get or create an exchange instance."""
    cache_key = f"{exchange_id.value}_{testnet}"
    
    if cache_key not in _exchange_cache:
        _exchange_cache[cache_key] = await ExchangeFactory.create_exchange(exchange_id, testnet)
    
    return _exchange_cache[cache_key]


async def close_all_exchanges() -> None:
    """Close all cached exchange connections."""
    for exchange in _exchange_cache.values():
        await exchange.close()
    _exchange_cache.clear()