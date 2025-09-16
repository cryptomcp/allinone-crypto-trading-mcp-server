"""
Core types and models for the All-in-One Crypto Trading MCP Server.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"
    DCA = "dca"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Exchange(str, Enum):
    """Supported exchanges."""
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"
    BYBIT = "bybit"
    OKX = "okx"


class Blockchain(str, Enum):
    """Supported blockchains."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    BSC = "bsc"
    AVALANCHE = "avalanche"
    SOLANA = "solana"


class SignalType(str, Enum):
    """Trading signal types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class NewsSentiment(str, Enum):
    """News sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


# =============================================================================
# TRADING MODELS
# =============================================================================

class TradingPair(BaseModel):
    """Trading pair information."""
    symbol: str = Field(..., description="Trading pair symbol (e.g., BTC/USDT)")
    base_asset: str = Field(..., description="Base asset symbol")
    quote_asset: str = Field(..., description="Quote asset symbol")
    exchange: Exchange = Field(..., description="Exchange where pair is traded")
    active: bool = Field(True, description="Whether pair is active for trading")
    min_order_size: Optional[Decimal] = Field(None, description="Minimum order size")
    max_order_size: Optional[Decimal] = Field(None, description="Maximum order size")
    price_precision: int = Field(8, description="Price decimal precision")
    quantity_precision: int = Field(8, description="Quantity decimal precision")


class Order(BaseModel):
    """Trading order model."""
    id: Optional[str] = Field(None, description="Order ID")
    symbol: str = Field(..., description="Trading pair symbol")
    side: OrderSide = Field(..., description="Order side (buy/sell)")
    order_type: OrderType = Field(..., description="Order type")
    amount: Decimal = Field(..., description="Order amount")
    price: Optional[Decimal] = Field(None, description="Order price (for limit orders)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Order status")
    exchange: Exchange = Field(..., description="Exchange")
    filled_amount: Decimal = Field(Decimal('0'), description="Filled amount")
    remaining_amount: Decimal = Field(..., description="Remaining amount")
    fee: Decimal = Field(Decimal('0'), description="Trading fee")
    fee_currency: Optional[str] = Field(None, description="Fee currency")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    dry_run: bool = Field(False, description="Whether this is a dry run")

    @validator('remaining_amount', always=True)
    def calculate_remaining(cls, v, values):
        amount = values.get('amount', Decimal('0'))
        filled = values.get('filled_amount', Decimal('0'))
        return amount - filled


class Position(BaseModel):
    """Trading position model."""
    symbol: str = Field(..., description="Trading pair symbol")
    side: str = Field(..., description="Position side (long/short)")
    size: Decimal = Field(..., description="Position size")
    entry_price: Decimal = Field(..., description="Average entry price")
    current_price: Decimal = Field(..., description="Current market price")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    realized_pnl: Decimal = Field(Decimal('0'), description="Realized P&L")
    margin: Decimal = Field(Decimal('0'), description="Margin used")
    leverage: Decimal = Field(Decimal('1'), description="Position leverage")
    exchange: Exchange = Field(..., description="Exchange")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Balance(BaseModel):
    """Account balance model."""
    currency: str = Field(..., description="Currency symbol")
    total: Decimal = Field(..., description="Total balance")
    available: Decimal = Field(..., description="Available balance")
    locked: Decimal = Field(Decimal('0'), description="Locked balance")
    exchange: Optional[Exchange] = Field(None, description="Exchange")
    blockchain: Optional[Blockchain] = Field(None, description="Blockchain network")
    address: Optional[str] = Field(None, description="Wallet address")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Portfolio(BaseModel):
    """Portfolio model."""
    total_value_usd: Decimal = Field(..., description="Total portfolio value in USD")
    balances: List[Balance] = Field(default_factory=list, description="All balances")
    positions: List[Position] = Field(default_factory=list, description="All positions")
    unrealized_pnl: Decimal = Field(Decimal('0'), description="Total unrealized P&L")
    realized_pnl: Decimal = Field(Decimal('0'), description="Total realized P&L")
    daily_pnl: Decimal = Field(Decimal('0'), description="Daily P&L")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# MARKET DATA MODELS
# =============================================================================

class Price(BaseModel):
    """Price data model."""
    symbol: str = Field(..., description="Asset symbol")
    price: Decimal = Field(..., description="Current price")
    currency: str = Field("USD", description="Price currency")
    change_24h: Optional[Decimal] = Field(None, description="24h price change")
    change_24h_percent: Optional[Decimal] = Field(None, description="24h percentage change")
    volume_24h: Optional[Decimal] = Field(None, description="24h trading volume")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = Field(None, description="Data source")


class Candle(BaseModel):
    """OHLCV candle data."""
    symbol: str = Field(..., description="Trading pair symbol")
    timestamp: datetime = Field(..., description="Candle timestamp")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="High price")
    low: Decimal = Field(..., description="Low price")
    close: Decimal = Field(..., description="Closing price")
    volume: Decimal = Field(..., description="Trading volume")
    timeframe: str = Field(..., description="Timeframe (1m, 5m, 1h, 1d, etc.)")


class WhaleTransaction(BaseModel):
    """Whale transaction model."""
    transaction_id: str = Field(..., description="Transaction hash/ID")
    blockchain: Blockchain = Field(..., description="Blockchain network")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    token_symbol: str = Field(..., description="Token symbol")
    token_address: Optional[str] = Field(None, description="Token contract address")
    amount: Decimal = Field(..., description="Transaction amount")
    amount_usd: Decimal = Field(..., description="Transaction value in USD")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    transaction_type: str = Field(..., description="Transaction type (transfer, swap, etc.)")
    exchange: Optional[str] = Field(None, description="Exchange involved (if any)")


class NewsItem(BaseModel):
    """News item model."""
    id: str = Field(..., description="News item ID")
    title: str = Field(..., description="News title")
    content: Optional[str] = Field(None, description="News content")
    url: str = Field(..., description="News URL")
    source: str = Field(..., description="News source")
    published_at: datetime = Field(..., description="Publication timestamp")
    sentiment: NewsSentiment = Field(NewsSentiment.NEUTRAL, description="Sentiment analysis")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    coins_mentioned: List[str] = Field(default_factory=list, description="Mentioned cryptocurrencies")
    impact_score: Optional[float] = Field(None, description="Predicted market impact (0-1)")


class Signal(BaseModel):
    """Trading signal model."""
    id: str = Field(..., description="Signal ID")
    symbol: str = Field(..., description="Trading pair symbol")
    signal_type: SignalType = Field(..., description="Signal type")
    confidence: float = Field(..., description="Signal confidence (0-1)")
    price_target: Optional[Decimal] = Field(None, description="Price target")
    stop_loss: Optional[Decimal] = Field(None, description="Stop loss level")
    take_profit: Optional[Decimal] = Field(None, description="Take profit level")
    timeframe: str = Field(..., description="Signal timeframe")
    reasoning: str = Field(..., description="Signal reasoning/analysis")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Signal expiration")


# =============================================================================
# BLOCKCHAIN MODELS
# =============================================================================

class TokenInfo(BaseModel):
    """Token information model."""
    symbol: str = Field(..., description="Token symbol")
    name: str = Field(..., description="Token name")
    address: str = Field(..., description="Token contract address")
    blockchain: Blockchain = Field(..., description="Blockchain network")
    decimals: int = Field(..., description="Token decimals")
    total_supply: Optional[Decimal] = Field(None, description="Total token supply")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    price_usd: Optional[Decimal] = Field(None, description="Current price in USD")
    verified: bool = Field(False, description="Whether token is verified")


class Transaction(BaseModel):
    """Blockchain transaction model."""
    hash: str = Field(..., description="Transaction hash")
    blockchain: Blockchain = Field(..., description="Blockchain network")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    value: Decimal = Field(..., description="Transaction value")
    gas_used: Optional[int] = Field(None, description="Gas used")
    gas_price: Optional[Decimal] = Field(None, description="Gas price")
    fee: Decimal = Field(..., description="Transaction fee")
    status: str = Field(..., description="Transaction status")
    block_number: Optional[int] = Field(None, description="Block number")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    token_transfers: List[Dict[str, Any]] = Field(default_factory=list, description="Token transfers")


# =============================================================================
# DEX MODELS
# =============================================================================

class DexPool(BaseModel):
    """DEX liquidity pool model."""
    pool_id: str = Field(..., description="Pool ID")
    dex: str = Field(..., description="DEX name")
    blockchain: Blockchain = Field(..., description="Blockchain network")
    token0: TokenInfo = Field(..., description="First token in pair")
    token1: TokenInfo = Field(..., description="Second token in pair")
    liquidity_usd: Decimal = Field(..., description="Total liquidity in USD")
    volume_24h_usd: Decimal = Field(..., description="24h volume in USD")
    fees_24h_usd: Decimal = Field(..., description="24h fees in USD")
    apr: Optional[Decimal] = Field(None, description="Annual percentage rate")
    price_token0: Decimal = Field(..., description="Price of token0 in token1")
    price_token1: Decimal = Field(..., description="Price of token1 in token0")
    pool_address: str = Field(..., description="Pool contract address")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# RISK MODELS
# =============================================================================

class RiskMetrics(BaseModel):
    """Risk metrics model."""
    portfolio_value: Decimal = Field(..., description="Current portfolio value")
    max_drawdown: Decimal = Field(..., description="Maximum drawdown")
    var_95: Decimal = Field(..., description="Value at Risk (95%)")
    sharpe_ratio: Optional[Decimal] = Field(None, description="Sharpe ratio")
    volatility: Decimal = Field(..., description="Portfolio volatility")
    beta: Optional[Decimal] = Field(None, description="Beta to market")
    daily_pnl: Decimal = Field(..., description="Daily P&L")
    exposure_by_asset: Dict[str, Decimal] = Field(default_factory=dict, description="Asset exposure")
    exposure_by_exchange: Dict[str, Decimal] = Field(default_factory=dict, description="Exchange exposure")
    concentration_risk: Decimal = Field(..., description="Concentration risk score")
    liquidity_risk: Decimal = Field(..., description="Liquidity risk score")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ApiResponse(BaseModel):
    """Standard API response model."""
    success: bool = Field(..., description="Whether operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TradeResponse(ApiResponse):
    """Trade execution response."""
    order: Optional[Order] = Field(None, description="Created order")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")


class PortfolioResponse(ApiResponse):
    """Portfolio data response."""
    portfolio: Optional[Portfolio] = Field(None, description="Portfolio data")
    risk_metrics: Optional[RiskMetrics] = Field(None, description="Risk metrics")


class MarketDataResponse(ApiResponse):
    """Market data response."""
    prices: Optional[List[Price]] = Field(None, description="Price data")
    candles: Optional[List[Candle]] = Field(None, description="Candle data")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class NewsResponse(ApiResponse):
    """News data response."""
    news: List[NewsItem] = Field(default_factory=list, description="News items")
    total_count: int = Field(0, description="Total news count")
    sentiment_summary: Optional[Dict[str, int]] = Field(None, description="Sentiment distribution")


class SignalResponse(ApiResponse):
    """Trading signals response."""
    signals: List[Signal] = Field(default_factory=list, description="Trading signals")
    summary: Optional[Dict[str, Any]] = Field(None, description="Signals summary")


class WhaleResponse(ApiResponse):
    """Whale transactions response."""
    transactions: List[WhaleTransaction] = Field(default_factory=list, description="Whale transactions")
    total_value_usd: Decimal = Field(Decimal('0'), description="Total transaction value")
    unique_addresses: int = Field(0, description="Number of unique addresses")