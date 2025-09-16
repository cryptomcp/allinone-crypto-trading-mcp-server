"""
MCP Tools Registry for the All-in-One Crypto Trading MCP Server.

This module registers all available tools with the MCP server.
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

import mcp
from mcp.server import Server
from pydantic import BaseModel, Field

from core.types import *
from core.exceptions import *
from core.utils import *
from env import config

logger = logging.getLogger(__name__)


# =============================================================================
# TRADING TOOL MODELS
# =============================================================================

class TradeRequest(BaseModel):
    """Request model for trade execution."""
    symbol: str = Field(..., description="Trading pair symbol (e.g., BTC/USDT)")
    side: OrderSide = Field(..., description="Order side (buy/sell)")
    amount: Decimal = Field(..., description="Order amount")
    order_type: OrderType = Field(OrderType.MARKET, description="Order type")
    price: Optional[Decimal] = Field(None, description="Limit price (for limit orders)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price (for stop orders)")
    exchange: Exchange = Field(Exchange.BINANCE, description="Exchange to trade on")
    dry_run: bool = Field(True, description="Whether to execute as dry run")


class BalanceRequest(BaseModel):
    """Request model for balance queries."""
    exchange: Optional[Exchange] = Field(None, description="Specific exchange (all if not specified)")
    currency: Optional[str] = Field(None, description="Specific currency filter")
    include_zero: bool = Field(False, description="Include zero balances")


class PriceRequest(BaseModel):
    """Request model for price queries."""
    symbol: str = Field(..., description="Asset symbol or trading pair")
    vs_currency: str = Field("USD", description="Quote currency")
    include_24h_data: bool = Field(True, description="Include 24h change data")


class NewsRequest(BaseModel):
    """Request model for news queries."""
    coins: Optional[List[str]] = Field(None, description="Filter by specific coins")
    sentiment: Optional[NewsSentiment] = Field(None, description="Filter by sentiment")
    limit: int = Field(20, description="Maximum number of news items")
    hours_back: int = Field(24, description="Hours to look back")


class WhaleRequest(BaseModel):
    """Request model for whale transaction queries."""
    blockchain: Optional[Blockchain] = Field(None, description="Filter by blockchain")
    min_value_usd: Decimal = Field(Decimal('1000000'), description="Minimum transaction value")
    limit: int = Field(50, description="Maximum number of transactions")
    hours_back: int = Field(24, description="Hours to look back")


class DexRequest(BaseModel):
    """Request model for DEX analytics."""
    token: str = Field(..., description="Token symbol or address")
    blockchain: Blockchain = Field(Blockchain.ETHEREUM, description="Blockchain network")
    include_pools: bool = Field(True, description="Include pool data")
    include_volume: bool = Field(True, description="Include volume metrics")


# =============================================================================
# CORE TRADING TOOLS
# =============================================================================

def register_trading_tools(server: Server) -> None:
    """Register core trading tools."""
    
    @server.tool()
    async def execute_trade(request: TradeRequest) -> TradeResponse:
        """Execute a cryptocurrency trade on a specified exchange.
        
        This tool allows you to buy or sell cryptocurrencies on supported exchanges.
        Always use dry_run=True for testing before live trading.
        """
        try:
            # Import here to avoid circular imports
            from cex.trading import execute_trade as _execute_trade
            
            # Log the trade attempt
            log_trade(
                action=f"{request.side}_{request.order_type}",
                symbol=request.symbol,
                amount=request.amount,
                price=request.price,
                exchange=request.exchange.value,
                dry_run=request.dry_run
            )
            
            # Execute the trade
            result = await _execute_trade(
                symbol=request.symbol,
                side=request.side,
                amount=request.amount,
                order_type=request.order_type,
                price=request.price,
                stop_price=request.stop_price,
                exchange=request.exchange,
                dry_run=request.dry_run
            )
            
            return TradeResponse(
                success=True,
                data=result,
                message=f"Trade executed successfully ({'dry run' if request.dry_run else 'live'})"
            )
        
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return TradeResponse(
                success=False,
                error=str(e),
                message="Trade execution failed"
            )
    
    @server.tool()
    async def get_portfolio_balance(request: BalanceRequest) -> PortfolioResponse:
        """Get portfolio balances across exchanges and wallets.
        
        Returns current balances for all assets or filtered by exchange/currency.
        """
        try:
            from portfolio.manager import get_balances
            
            balances = await get_balances(
                exchange=request.exchange,
                currency=request.currency,
                include_zero=request.include_zero
            )
            
            return PortfolioResponse(
                success=True,
                data=balances,
                message="Balances retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get balances: {e}")
            return PortfolioResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve balances"
            )
    
    @server.tool()
    async def get_crypto_price(request: PriceRequest) -> MarketDataResponse:
        """Get current cryptocurrency prices and market data.
        
        Returns real-time price data including 24h changes and volume.
        """
        try:
            from cex.market_data import get_price_data
            
            price_data = await get_price_data(
                symbol=request.symbol,
                vs_currency=request.vs_currency,
                include_24h_data=request.include_24h_data
            )
            
            return MarketDataResponse(
                success=True,
                data=price_data,
                message="Price data retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get price data: {e}")
            return MarketDataResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve price data"
            )


# =============================================================================
# NEWS & SENTIMENT TOOLS
# =============================================================================

def register_news_tools(server: Server) -> None:
    """Register news and sentiment analysis tools."""
    
    @server.tool()
    async def get_crypto_news(request: NewsRequest) -> NewsResponse:
        """Get latest cryptocurrency news with sentiment analysis.
        
        Returns recent news articles with sentiment scores and market impact analysis.
        """
        try:
            from addons.news.aggregator import get_news_feed
            
            news_data = await get_news_feed(
                coins=request.coins,
                sentiment=request.sentiment,
                limit=request.limit,
                hours_back=request.hours_back
            )
            
            return NewsResponse(
                success=True,
                data=news_data,
                message="News data retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get news data: {e}")
            return NewsResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve news data"
            )
    
    @server.tool()
    async def get_fear_greed_index() -> ApiResponse:
        """Get the current Fear & Greed Index for cryptocurrency markets.
        
        Returns market sentiment indicator from 0 (Extreme Fear) to 100 (Extreme Greed).
        """
        try:
            from addons.news.feargreed_tools import get_fear_greed_data
            
            fng_data = await get_fear_greed_data()
            
            return ApiResponse(
                success=True,
                data=fng_data,
                message="Fear & Greed Index retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get Fear & Greed Index: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve Fear & Greed Index"
            )


# =============================================================================
# WHALE TRACKING TOOLS
# =============================================================================

def register_whale_tools(server: Server) -> None:
    """Register whale tracking and monitoring tools."""
    
    @server.tool()
    async def track_whale_transactions(request: WhaleRequest) -> WhaleResponse:
        """Track large cryptocurrency transactions (whale movements).
        
        Monitors and returns significant transactions that may impact market prices.
        """
        try:
            from addons.signals.whales_tools import get_whale_transactions
            
            whale_data = await get_whale_transactions(
                blockchain=request.blockchain,
                min_value_usd=request.min_value_usd,
                limit=request.limit,
                hours_back=request.hours_back
            )
            
            return WhaleResponse(
                success=True,
                data=whale_data,
                message="Whale transactions retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get whale transactions: {e}")
            return WhaleResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve whale transactions"
            )


# =============================================================================
# DEX ANALYTICS TOOLS
# =============================================================================

def register_dex_tools(server: Server) -> None:
    """Register DEX analytics and pool monitoring tools."""
    
    @server.tool()
    async def analyze_dex_pools(request: DexRequest) -> ApiResponse:
        """Analyze DEX liquidity pools and trading metrics.
        
        Returns comprehensive analytics for DEX pools including liquidity, volume, and APY.
        """
        try:
            from addons.signals.dex_analytics import analyze_token_pools
            
            pool_data = await analyze_token_pools(
                token=request.token,
                blockchain=request.blockchain,
                include_pools=request.include_pools,
                include_volume=request.include_volume
            )
            
            return ApiResponse(
                success=True,
                data=pool_data,
                message="DEX pool analysis completed successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to analyze DEX pools: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Failed to analyze DEX pools"
            )


# =============================================================================
# CROSS-CHAIN TOOLS
# =============================================================================

def register_bridge_tools(server: Server) -> None:
    """Register cross-chain bridge tools."""
    
    @server.tool()
    async def bridge_tokens(
        from_chain: Blockchain,
        to_chain: Blockchain,
        token: str,
        amount: Decimal,
        recipient_address: str,
        bridge_provider: str = "wormhole",
        dry_run: bool = True
    ) -> ApiResponse:
        """Bridge tokens across different blockchain networks.
        
        Transfers tokens from one blockchain to another using supported bridge protocols.
        """
        try:
            from addons.bridges.cross_chain import execute_bridge
            
            bridge_result = await execute_bridge(
                from_chain=from_chain,
                to_chain=to_chain,
                token=token,
                amount=amount,
                recipient_address=recipient_address,
                bridge_provider=bridge_provider,
                dry_run=dry_run
            )
            
            return ApiResponse(
                success=True,
                data=bridge_result,
                message=f"Bridge operation completed ({'dry run' if dry_run else 'live'})"
            )
        
        except Exception as e:
            logger.error(f"Bridge operation failed: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Bridge operation failed"
            )


# =============================================================================
# AI ANALYSIS TOOLS
# =============================================================================

def register_ai_tools(server: Server) -> None:
    """Register AI analysis and signal generation tools."""
    
    @server.tool()
    async def generate_trading_signals(
        symbols: List[str],
        timeframe: str = "1h",
        analysis_type: str = "technical",
        include_sentiment: bool = True
    ) -> SignalResponse:
        """Generate AI-powered trading signals and market analysis.
        
        Creates trading signals based on technical analysis, sentiment, and market data.
        """
        try:
            from ai.signals import generate_signals
            
            signals = await generate_signals(
                symbols=symbols,
                timeframe=timeframe,
                analysis_type=analysis_type,
                include_sentiment=include_sentiment
            )
            
            return SignalResponse(
                success=True,
                data=signals,
                message="Trading signals generated successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to generate trading signals: {e}")
            return SignalResponse(
                success=False,
                error=str(e),
                message="Failed to generate trading signals"
            )


# =============================================================================
# PORTFOLIO TOOLS
# =============================================================================

def register_portfolio_tools(server: Server) -> None:
    """Register portfolio management tools."""
    
    @server.tool()
    async def get_portfolio_summary(
        include_exchanges: bool = True,
        include_wallets: bool = True,
        include_staking: bool = True
    ) -> ApiResponse:
        """Get comprehensive portfolio summary with balances and positions.
        
        Returns portfolio data across all exchanges and wallets.
        """
        try:
            from portfolio.manager import get_portfolio_summary as _get_portfolio
            
            portfolio = await _get_portfolio(include_exchanges, include_wallets, include_staking)
            
            return ApiResponse(
                success=True,
                data=portfolio.dict(),
                message="Portfolio summary retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve portfolio summary"
            )
    
    @server.tool()
    async def get_asset_allocation() -> ApiResponse:
        """Get portfolio asset allocation and diversification metrics.
        
        Returns detailed breakdown of portfolio allocation by asset.
        """
        try:
            from portfolio.manager import get_asset_allocation as _get_allocation
            
            allocation = await _get_allocation()
            
            return ApiResponse(
                success=True,
                data=allocation,
                message="Asset allocation retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get asset allocation: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve asset allocation"
            )


# =============================================================================
# GOAT PROXY TOOLS
# =============================================================================

def register_goat_tools(server: Server) -> None:
    """Register GOAT SDK proxy tools."""
    
    @server.tool()
    async def execute_goat_command(
        command: str,
        parameters: Dict[str, Any],
        blockchain: Blockchain = Blockchain.ETHEREUM,
        dry_run: bool = True
    ) -> ApiResponse:
        """Execute GOAT SDK command for enhanced EVM operations.
        
        Provides access to advanced DeFi operations through GOAT SDK.
        """
        try:
            from addons.goat.goat_proxy import execute_goat_command as _execute_goat
            
            result = await _execute_goat(command, parameters, blockchain, dry_run)
            
            return ApiResponse(
                success=result.get('success', False),
                data=result,
                message=result.get('message', 'GOAT command executed')
            )
        
        except Exception as e:
            logger.error(f"GOAT command execution failed: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="GOAT command execution failed"
            )
    
    @server.tool()
    async def get_goat_status() -> ApiResponse:
        """Get GOAT SDK proxy status and capabilities.
        
        Returns information about available GOAT features.
        """
        try:
            from addons.goat.goat_proxy import get_goat_status as _get_status
            
            status = await _get_status()
            
            return ApiResponse(
                success=True,
                data=status,
                message="GOAT status retrieved successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to get GOAT status: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve GOAT status"
            )


# =============================================================================
# BASE FREE USDC TOOLS
# =============================================================================

def register_base_free_tools(server: Server) -> None:
    """Register Base network free USDC transfer tools."""
    
    @server.tool()
    async def transfer_free_usdc(
        to_address: str,
        amount: Decimal,
        dry_run: bool = True
    ) -> ApiResponse:
        """Transfer USDC on Base network with free gas using MPC wallets.
        
        Enables gas-free USDC transfers on Base network.
        """
        try:
            from addons.base_free.base_free_usdc import transfer_free_usdc as _transfer
            
            result = await _transfer(to_address, amount, dry_run)
            
            return ApiResponse(
                success=result.get('success', False),
                data=result,
                message=result.get('message', 'Free USDC transfer completed')
            )
        
        except Exception as e:
            logger.error(f"Free USDC transfer failed: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Free USDC transfer failed"
            )
    
    @server.tool()
    async def check_free_usdc_eligibility(
        to_address: str,
        amount: Decimal
    ) -> ApiResponse:
        """Check eligibility for free USDC transfer.
        
        Validates transfer requirements and daily limits.
        """
        try:
            from addons.base_free.base_free_usdc import check_transfer_eligibility
            
            eligibility = await check_transfer_eligibility(to_address, amount)
            
            return ApiResponse(
                success=True,
                data=eligibility,
                message="Eligibility check completed"
            )
        
        except Exception as e:
            logger.error(f"Eligibility check failed: {e}")
            return ApiResponse(
                success=False,
                error=str(e),
                message="Eligibility check failed"
            )


# =============================================================================
# MAIN REGISTRATION FUNCTION
# =============================================================================

def register_all_tools(server: Server) -> None:
    """Register all MCP tools with the server."""
    try:
        logger.info("Registering MCP tools...")
        
        # Register core trading tools
        register_trading_tools(server)
        logger.info("Registered trading tools")
        
        # Register portfolio tools
        register_portfolio_tools(server)
        logger.info("Registered portfolio tools")
        
        # Register news and sentiment tools
        register_news_tools(server)
        logger.info("Registered news and sentiment tools")
        
        # Register whale tracking tools
        register_whale_tools(server)
        logger.info("Registered whale tracking tools")
        
        # Register DEX analytics tools
        register_dex_tools(server)
        logger.info("Registered DEX analytics tools")
        
        # Register bridge tools
        register_bridge_tools(server)
        logger.info("Registered bridge tools")
        
        # Register AI analysis tools
        register_ai_tools(server)
        logger.info("Registered AI analysis tools")
        
        # Register GOAT proxy tools
        register_goat_tools(server)
        logger.info("Registered GOAT proxy tools")
        
        # Register Base free USDC tools
        register_base_free_tools(server)
        logger.info("Registered Base free USDC tools")
        
        logger.info("All MCP tools registered successfully")
    
    except Exception as e:
        logger.error(f"Failed to register MCP tools: {e}")
        raise