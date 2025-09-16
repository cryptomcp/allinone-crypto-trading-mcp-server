"""
Utility functions for the All-in-One Crypto Trading MCP Server.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union, List
import re
import hashlib
import hmac
import base64
from urllib.parse import urlencode

from .exceptions import ValidationError, RiskManagementError
from env import config

logger = logging.getLogger(__name__)


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================

def format_currency(amount: Union[Decimal, float, str], currency: str = "USD", precision: int = 2) -> str:
    """Format currency amount with appropriate symbols and precision."""
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        return f"Invalid amount"
    
    # Currency symbols
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "BTC": "₿",
        "ETH": "Ξ",
    }
    
    symbol = symbols.get(currency.upper(), currency.upper())
    
    # Format with appropriate precision
    if amount >= 1000000:
        formatted = f"{amount / 1000000:.{max(1, precision-1)}f}M"
    elif amount >= 1000:
        formatted = f"{amount / 1000:.{max(1, precision-1)}f}K"
    else:
        formatted = f"{amount:.{precision}f}"
    
    return f"{symbol}{formatted}" if currency.upper() in symbols else f"{formatted} {currency.upper()}"


def calculate_percentage_change(old_value: Union[Decimal, float], new_value: Union[Decimal, float]) -> Decimal:
    """Calculate percentage change between two values."""
    try:
        old_val = Decimal(str(old_value))
        new_val = Decimal(str(new_value))
        
        if old_val == 0:
            return Decimal('0')
        
        return ((new_val - old_val) / old_val) * 100
    except (InvalidOperation, ValueError):
        return Decimal('0')


def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """Safely convert a value to Decimal."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_address(address: str, blockchain: str) -> bool:
    """Validate blockchain address format."""
    if not address:
        return False
    
    blockchain = blockchain.lower()
    
    # Ethereum-based chains (40 hex chars with 0x prefix)
    if blockchain in ["ethereum", "polygon", "arbitrum", "optimism", "base", "bsc", "avalanche"]:
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    
    # Solana (base58, 32-44 chars)
    elif blockchain == "solana":
        if len(address) < 32 or len(address) > 44:
            return False
        # Basic base58 check (simplified)
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return all(c in base58_chars for c in address)
    
    # Bitcoin (P2PKH, P2SH, Bech32)
    elif blockchain == "bitcoin":
        # Legacy addresses (P2PKH)
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        # Bech32 addresses
        if re.match(r'^bc1[a-z0-9]{39,59}$', address):
            return True
        return False
    
    return False


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format."""
    if not symbol:
        return False
    
    # Support formats: BTC/USDT, BTC-USDT, BTCUSDT
    pattern = r'^[A-Z0-9]{2,10}[/-]?[A-Z0-9]{2,10}$'
    return bool(re.match(pattern, symbol.upper()))


def validate_order_params(symbol: str, amount: Decimal, price: Optional[Decimal] = None) -> None:
    """Validate order parameters."""
    if not validate_symbol(symbol):
        raise ValidationError(f"Invalid symbol: {symbol}")
    
    if amount <= 0:
        raise ValidationError(f"Amount must be positive: {amount}")
    
    if price is not None and price <= 0:
        raise ValidationError(f"Price must be positive: {price}")


# =============================================================================
# RISK MANAGEMENT UTILITIES
# =============================================================================

def check_risk_limits(amount_usd: Decimal, daily_total_usd: Decimal = Decimal('0')) -> None:
    """Check if trade amount violates risk limits."""
    if amount_usd > config.MAX_ORDER_USD:
        raise RiskManagementError(
            f"Order amount ${amount_usd} exceeds maximum allowed ${config.MAX_ORDER_USD}"
        )
    
    if daily_total_usd + amount_usd > config.DAILY_LOSS_LIMIT_USD:
        raise RiskManagementError(
            f"Daily total ${daily_total_usd + amount_usd} would exceed daily limit ${config.DAILY_LOSS_LIMIT_USD}"
        )


def calculate_position_size(
    balance: Decimal, 
    risk_percent: float = 2.0, 
    entry_price: Decimal = Decimal('0'), 
    stop_loss: Decimal = Decimal('0')
) -> Decimal:
    """Calculate position size based on risk management rules."""
    if entry_price <= 0 or stop_loss <= 0:
        # Fallback to percentage of balance
        return balance * Decimal(str(risk_percent / 100))
    
    # Calculate risk per unit
    risk_per_unit = abs(entry_price - stop_loss)
    
    # Calculate total risk amount
    total_risk = balance * Decimal(str(risk_percent / 100))
    
    # Calculate position size
    if risk_per_unit > 0:
        position_size = total_risk / risk_per_unit
        return min(position_size, balance * Decimal('0.5'))  # Max 50% of balance
    
    return balance * Decimal(str(risk_percent / 100))


# =============================================================================
# ASYNC UTILITIES
# =============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class RateLimiter:
    """Simple rate limiter."""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                return await self.wait_if_needed()
        
        # Record this call
        self.calls.append(now)


def rate_limit(max_calls: int = 60, time_window: int = 60):
    """Decorator for rate limiting function calls."""
    limiter = RateLimiter(max_calls, time_window)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await limiter.wait_if_needed()
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# =============================================================================
# CACHING UTILITIES
# =============================================================================

class SimpleCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() < entry['expires']:
                return entry['value']
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL in seconds."""
        self._cache[key] = {
            'value': value,
            'expires': datetime.utcnow() + timedelta(seconds=ttl)
        }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
_cache = SimpleCache()


def cache_result(ttl: int = 300, key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# =============================================================================
# CRYPTOGRAPHIC UTILITIES
# =============================================================================

def generate_signature(secret: str, message: str, algorithm: str = 'sha256') -> str:
    """Generate HMAC signature for API authentication."""
    return hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        getattr(hashlib, algorithm)
    ).hexdigest()


def generate_signature_base64(secret: str, message: str, algorithm: str = 'sha256') -> str:
    """Generate base64-encoded HMAC signature."""
    return base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            getattr(hashlib, algorithm)
        ).digest()
    ).decode('utf-8')


def create_query_string(params: Dict[str, Any]) -> str:
    """Create query string from parameters."""
    return urlencode(sorted(params.items()))


# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def log_trade(
    action: str,
    symbol: str,
    amount: Decimal,
    price: Optional[Decimal] = None,
    exchange: Optional[str] = None,
    dry_run: bool = False,
    **kwargs
) -> None:
    """Log trading actions with consistent format."""
    log_data = {
        'action': action,
        'symbol': symbol,
        'amount': str(amount),
        'exchange': exchange,
        'dry_run': dry_run,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }
    
    if price:
        log_data['price'] = str(price)
    
    log_level = logging.INFO if not dry_run else logging.DEBUG
    logger.log(log_level, f"Trade {action}: {log_data}")


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """Set up logging configuration."""
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('crypto_mcp.log')
        ]
    )


# =============================================================================
# TIME UTILITIES
# =============================================================================

def get_timestamp() -> int:
    """Get current Unix timestamp in milliseconds."""
    return int(time.time() * 1000)


def get_timestamp_seconds() -> int:
    """Get current Unix timestamp in seconds."""
    return int(time.time())


def parse_timeframe(timeframe: str) -> int:
    """Parse timeframe string to seconds."""
    timeframes = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '1h': 3600,
        '4h': 14400,
        '1d': 86400,
        '1w': 604800,
    }
    return timeframes.get(timeframe.lower(), 300)  # Default to 5 minutes


# =============================================================================
# MATH UTILITIES
# =============================================================================

def round_to_precision(value: Decimal, precision: int) -> Decimal:
    """Round value to specified decimal places."""
    return value.quantize(Decimal('0.1') ** precision)


def calculate_slippage(expected_price: Decimal, executed_price: Decimal) -> Decimal:
    """Calculate slippage percentage."""
    if expected_price == 0:
        return Decimal('0')
    
    return abs(executed_price - expected_price) / expected_price * 100


def calculate_fees(amount: Decimal, fee_rate: Decimal) -> Decimal:
    """Calculate trading fees."""
    return amount * fee_rate


# =============================================================================
# INITIALIZATION
# =============================================================================

def clear_cache() -> None:
    """Clear the global cache."""
    _cache.clear()


# Set up logging on module import
setup_logging(level=config.MCP_LOG_LEVEL)