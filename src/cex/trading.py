"""
Trading functionality for centralized exchanges.
"""

import logging
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.types import Order, OrderSide, OrderType, OrderStatus, Exchange, Position, TradeResponse
from core.exceptions import ExchangeError, RiskManagementError, ValidationError, InsufficientFundsError
from core.utils import check_risk_limits, validate_order_params, log_trade
from .exchanges import get_exchange
from env import config

logger = logging.getLogger(__name__)


async def execute_trade(
    symbol: str,
    side: OrderSide,
    amount: Decimal,
    order_type: OrderType = OrderType.MARKET,
    price: Optional[Decimal] = None,
    stop_price: Optional[Decimal] = None,
    exchange: Exchange = Exchange.BINANCE,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Execute a trade on the specified exchange.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT')
        side: Order side (buy/sell)
        amount: Order amount
        order_type: Order type (market, limit, etc.)
        price: Limit price (required for limit orders)
        stop_price: Stop price (for stop orders)
        exchange: Exchange to trade on
        dry_run: Whether to simulate the trade
    
    Returns:
        Trade execution result
    """
    try:
        # Validate inputs
        validate_order_params(symbol, amount, price)
        
        # Check risk limits (estimate USD value)
        estimated_usd = amount * (price or Decimal('50000'))  # Rough estimate
        check_risk_limits(estimated_usd)
        
        # Safety check for live trading
        if not dry_run and not config.LIVE:
            raise RiskManagementError("Live trading not enabled. Set LIVE=true in config.")
        
        if not dry_run and not config.AM_I_SURE:
            raise RiskManagementError("Live trading requires AM_I_SURE=true confirmation.")
        
        # Log the trade attempt
        log_trade(
            action=f"{side.value}_{order_type.value}",
            symbol=symbol,
            amount=amount,
            price=price,
            exchange=exchange.value,
            dry_run=dry_run
        )
        
        if dry_run:
            # Simulate the trade
            return await _simulate_trade(symbol, side, amount, order_type, price, exchange)
        else:
            # Execute real trade
            return await _execute_real_trade(symbol, side, amount, order_type, price, stop_price, exchange)
    
    except Exception as e:
        logger.error(f"Trade execution failed: {e}")
        raise


async def _simulate_trade(
    symbol: str,
    side: OrderSide,
    amount: Decimal,
    order_type: OrderType,
    price: Optional[Decimal],
    exchange: Exchange
) -> Dict[str, Any]:
    """Simulate a trade without actual execution."""
    try:
        # Get current market price for simulation
        exchange_client = await get_exchange(exchange, testnet=True)
        ticker = await exchange_client.get_ticker(symbol)
        market_price = Decimal(str(ticker.get('last', 0)))
        
        # Simulate execution price
        if order_type == OrderType.MARKET:
            execution_price = market_price
        else:
            execution_price = price or market_price
        
        # Calculate fees (typical 0.1% for most exchanges)
        fee_rate = Decimal('0.001')
        fee = amount * execution_price * fee_rate
        
        # Create simulated order
        simulated_order = Order(
            id=f"SIM_{datetime.utcnow().timestamp()}",
            symbol=symbol,
            side=side,
            order_type=order_type,
            amount=amount,
            price=execution_price,
            status=OrderStatus.FILLED,
            exchange=exchange,
            filled_amount=amount,
            fee=fee,
            fee_currency=symbol.split('/')[1] if '/' in symbol else 'USDT',
            dry_run=True
        )
        
        return {
            'order': simulated_order,
            'execution_price': execution_price,
            'total_cost': amount * execution_price + fee,
            'fee': fee,
            'market_price': market_price,
            'simulated': True,
            'message': 'Trade simulated successfully'
        }
    
    except Exception as e:
        logger.error(f"Trade simulation failed: {e}")
        raise ExchangeError(f"Failed to simulate trade: {str(e)}")


async def _execute_real_trade(
    symbol: str,
    side: OrderSide,
    amount: Decimal,
    order_type: OrderType,
    price: Optional[Decimal],
    stop_price: Optional[Decimal],
    exchange: Exchange
) -> Dict[str, Any]:
    """Execute a real trade on the exchange."""
    try:
        exchange_client = await get_exchange(exchange, testnet=False)
        
        # Place the order
        order = await exchange_client.place_order(
            symbol=symbol,
            side=side,
            amount=amount,
            order_type=order_type,
            price=price,
            stop_price=stop_price
        )
        
        # Get current market price for reference
        ticker = await exchange_client.get_ticker(symbol)
        market_price = Decimal(str(ticker.get('last', 0)))
        
        return {
            'order': order,
            'market_price': market_price,
            'simulated': False,
            'message': 'Trade executed successfully'
        }
    
    except Exception as e:
        logger.error(f"Real trade execution failed: {e}")
        raise


async def get_balances(
    exchange: Optional[Exchange] = None,
    currency: Optional[str] = None,
    include_zero: bool = False
) -> List[Dict[str, Any]]:
    """
    Get account balances from exchanges.
    
    Args:
        exchange: Specific exchange (all if None)
        currency: Filter by currency
        include_zero: Include zero balances
    
    Returns:
        List of balance data
    """
    try:
        balances = []
        
        if exchange:
            # Get balances from specific exchange
            exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
            exchange_balances = await exchange_client.get_balance(currency)
            balances.extend([balance.dict() for balance in exchange_balances])
        else:
            # Get balances from all configured exchanges
            exchanges_to_check = []
            
            if config.BINANCE_API_KEY:
                exchanges_to_check.append(Exchange.BINANCE)
            if config.COINBASE_API_KEY:
                exchanges_to_check.append(Exchange.COINBASE)
            # Add other exchanges as needed
            
            for exch in exchanges_to_check:
                try:
                    exchange_client = await get_exchange(exch, testnet=not config.LIVE)
                    exchange_balances = await exchange_client.get_balance(currency)
                    balances.extend([balance.dict() for balance in exchange_balances])
                except Exception as e:
                    logger.warning(f"Failed to get balances from {exch.value}: {e}")
        
        # Filter zero balances if requested
        if not include_zero:
            balances = [b for b in balances if b['total'] > 0]
        
        return balances
    
    except Exception as e:
        logger.error(f"Failed to get balances: {e}")
        raise


async def get_orders(
    exchange: Exchange,
    symbol: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get orders from an exchange.
    
    Args:
        exchange: Exchange to query
        symbol: Filter by symbol
        status: Filter by status
    
    Returns:
        List of orders
    """
    try:
        exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
        orders = await exchange_client.get_orders(symbol, status)
        return [order.dict() for order in orders]
    
    except Exception as e:
        logger.error(f"Failed to get orders: {e}")
        raise


async def cancel_order(
    exchange: Exchange,
    order_id: str,
    symbol: str,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Cancel an order on an exchange.
    
    Args:
        exchange: Exchange where order was placed
        order_id: Order ID to cancel
        symbol: Trading symbol
        dry_run: Whether to simulate cancellation
    
    Returns:
        Cancellation result
    """
    try:
        if dry_run:
            return {
                'success': True,
                'message': 'Order cancellation simulated',
                'order_id': order_id,
                'simulated': True
            }
        
        # Safety check for live trading
        if not config.LIVE or not config.AM_I_SURE:
            raise RiskManagementError("Live order cancellation requires LIVE=true and AM_I_SURE=true")
        
        exchange_client = await get_exchange(exchange, testnet=False)
        success = await exchange_client.cancel_order(order_id, symbol)
        
        return {
            'success': success,
            'message': 'Order cancelled successfully' if success else 'Order cancellation failed',
            'order_id': order_id,
            'simulated': False
        }
    
    except Exception as e:
        logger.error(f"Failed to cancel order: {e}")
        raise


async def get_open_positions(exchange: Exchange) -> List[Position]:
    """
    Get open positions from an exchange (for margin/futures trading).
    
    Args:
        exchange: Exchange to query
    
    Returns:
        List of open positions
    """
    try:
        # This would be implemented for exchanges that support margin/futures
        # For now, return empty list as most spot trading doesn't have positions
        return []
    
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise


# Trading utilities
async def calculate_order_size(
    symbol: str,
    percentage: float,
    exchange: Exchange,
    side: OrderSide = OrderSide.BUY
) -> Decimal:
    """
    Calculate order size based on percentage of available balance.
    
    Args:
        symbol: Trading symbol
        percentage: Percentage of balance to use (0-100)
        exchange: Exchange to check balance on
        side: Order side (affects which currency to check)
    
    Returns:
        Calculated order size
    """
    try:
        # Get base and quote currencies
        base, quote = symbol.split('/')
        
        # Determine which currency balance to check
        currency = quote if side == OrderSide.BUY else base
        
        # Get balance
        balances = await get_balances(exchange, currency)
        available_balance = Decimal('0')
        
        for balance in balances:
            if balance['currency'] == currency:
                available_balance = Decimal(str(balance['available']))
                break
        
        if available_balance <= 0:
            raise InsufficientFundsError(f"No available {currency} balance")
        
        # Calculate order size
        percentage_decimal = Decimal(str(percentage / 100))
        
        if side == OrderSide.BUY:
            # For buy orders, we need to factor in the price
            exchange_client = await get_exchange(exchange, testnet=not config.LIVE)
            ticker = await exchange_client.get_ticker(symbol)
            price = Decimal(str(ticker.get('last', 0)))
            
            if price <= 0:
                raise ValueError(f"Invalid price for {symbol}")
            
            # Calculate how much base currency we can buy
            order_size = (available_balance * percentage_decimal) / price
        else:
            # For sell orders, use percentage of base currency balance
            order_size = available_balance * percentage_decimal
        
        return order_size
    
    except Exception as e:
        logger.error(f"Failed to calculate order size: {e}")
        raise