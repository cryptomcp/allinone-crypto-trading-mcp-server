"""
Main entry point for the All-in-One Crypto Trading MCP Server.
"""

import asyncio
import logging
import sys
from typing import Any, List

import mcp.server.stdio
from mcp.server import NotificationOptions, Server
from mcp.types import ClientCapabilities, InitializationOptions

from env import config
from core.utils import setup_logging

# Import all MCP tools
from mcp_tools import register_all_tools

logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server(config.MCP_SERVER_NAME)


@server.list_prompts()
async def handle_list_prompts() -> List[Any]:
    """List available prompts."""
    return [
        {
            "name": "trading_analysis",
            "description": "Analyze market conditions and provide trading recommendations",
            "arguments": [
                {
                    "name": "symbol",
                    "description": "Trading symbol to analyze (e.g., BTC/USDT)",
                    "required": True
                },
                {
                    "name": "timeframe",
                    "description": "Analysis timeframe (1h, 4h, 1d)",
                    "required": False
                }
            ]
        },
        {
            "name": "portfolio_summary",
            "description": "Generate a comprehensive portfolio analysis",
            "arguments": [
                {
                    "name": "include_risk_metrics",
                    "description": "Include risk analysis in the summary",
                    "required": False
                }
            ]
        },
        {
            "name": "news_sentiment",
            "description": "Analyze recent news sentiment for cryptocurrencies",
            "arguments": [
                {
                    "name": "coins",
                    "description": "Comma-separated list of coins to analyze",
                    "required": False
                }
            ]
        },
        {
            "name": "whale_alert",
            "description": "Generate alerts for whale transactions",
            "arguments": [
                {
                    "name": "min_value",
                    "description": "Minimum transaction value in USD",
                    "required": False
                }
            ]
        },
        {
            "name": "dex_analysis",
            "description": "Analyze DEX pools and trading opportunities",
            "arguments": [
                {
                    "name": "token",
                    "description": "Token to analyze",
                    "required": True
                },
                {
                    "name": "chain",
                    "description": "Blockchain network",
                    "required": False
                }
            ]
        }
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict) -> str:
    """Get a specific prompt with arguments."""
    try:
        if name == "trading_analysis":
            symbol = arguments.get("symbol", "BTC/USDT")
            timeframe = arguments.get("timeframe", "1h")
            
            return f"""
            Please analyze the current market conditions for {symbol} on the {timeframe} timeframe.
            
            Include:
            1. Technical analysis (support/resistance, indicators)
            2. Recent price action and volume
            3. Market sentiment from news and social media
            4. Trading recommendations with risk management
            5. Entry/exit points and stop-loss levels
            
            Use the available tools to gather comprehensive market data.
            """
        
        elif name == "portfolio_summary":
            include_risk = arguments.get("include_risk_metrics", True)
            risk_section = """
            4. Risk metrics and portfolio health
            5. Concentration analysis and diversification suggestions
            6. Value at Risk (VaR) and maximum drawdown analysis
            """ if include_risk else ""
            
            return f"""
            Please provide a comprehensive portfolio analysis including:
            
            1. Current portfolio value and asset allocation
            2. Profit/Loss analysis (realized and unrealized)
            3. Recent performance and trends{risk_section}
            
            Use the portfolio and balance tools to gather current data.
            """
        
        elif name == "news_sentiment":
            coins = arguments.get("coins", "BTC,ETH,SOL")
            
            return f"""
            Analyze recent news sentiment for: {coins}
            
            Include:
            1. Latest news headlines and summaries
            2. Sentiment analysis (positive/negative/neutral)
            3. Market impact assessment
            4. Key events or announcements affecting prices
            5. Social media sentiment trends
            
            Use news and sentiment analysis tools to gather data.
            """
        
        elif name == "whale_alert":
            min_value = arguments.get("min_value", "1000000")
            
            return f"""
            Generate whale transaction alerts for transactions >= ${min_value}
            
            Include:
            1. Recent large transactions across all monitored chains
            2. Analysis of whale behavior patterns
            3. Potential market impact assessment
            4. Exchange inflows/outflows
            5. Notable wallet movements
            
            Use whale tracking tools to gather transaction data.
            """
        
        elif name == "dex_analysis":
            token = arguments.get("token")
            chain = arguments.get("chain", "ethereum")
            
            return f"""
            Analyze DEX trading opportunities for {token} on {chain}
            
            Include:
            1. Liquidity pool analysis across major DEXs
            2. Volume and fees analysis
            3. Price impact calculations
            4. Arbitrage opportunities
            5. Pool performance metrics (APR, impermanent loss)
            
            Use DEX analytics tools to gather pool data.
            """
        
        else:
            return f"Unknown prompt: {name}"
    
    except Exception as e:
        logger.error(f"Error generating prompt {name}: {e}")
        return f"Error generating prompt: {str(e)}"


@server.list_resources()
async def handle_list_resources() -> List[Any]:
    """List available resources."""
    return [
        {
            "uri": "crypto://markets",
            "name": "Cryptocurrency Markets",
            "description": "Real-time cryptocurrency market data",
            "mimeType": "application/json"
        },
        {
            "uri": "crypto://portfolio",
            "name": "Portfolio Data",
            "description": "Current portfolio balances and positions",
            "mimeType": "application/json"
        },
        {
            "uri": "crypto://news",
            "name": "Crypto News",
            "description": "Latest cryptocurrency news and sentiment",
            "mimeType": "application/json"
        },
        {
            "uri": "crypto://whales",
            "name": "Whale Transactions",
            "description": "Large cryptocurrency transactions",
            "mimeType": "application/json"
        },
        {
            "uri": "crypto://dex",
            "name": "DEX Analytics",
            "description": "Decentralized exchange analytics and pool data",
            "mimeType": "application/json"
        },
        {
            "uri": "crypto://signals",
            "name": "Trading Signals",
            "description": "AI-generated trading signals and analysis",
            "mimeType": "application/json"
        }
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    try:
        if uri == "crypto://markets":
            # Import here to avoid circular imports
            from cex.market_data import get_market_overview
            data = await get_market_overview()
            return str(data)
        
        elif uri == "crypto://portfolio":
            from portfolio.manager import get_portfolio_summary
            data = await get_portfolio_summary()
            return str(data)
        
        elif uri == "crypto://news":
            from addons.news.aggregator import get_latest_news
            data = await get_latest_news(limit=20)
            return str(data)
        
        elif uri == "crypto://whales":
            from addons.signals.whales_tools import get_recent_whale_transactions
            data = await get_recent_whale_transactions(limit=50)
            return str(data)
        
        elif uri == "crypto://dex":
            from addons.signals.dex_analytics import get_top_pools
            data = await get_top_pools(limit=20)
            return str(data)
        
        elif uri == "crypto://signals":
            from ai.signals import get_latest_signals
            data = await get_latest_signals(limit=10)
            return str(data)
        
        else:
            return f"Unknown resource: {uri}"
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return f"Error reading resource: {str(e)}"


async def initialize_server():
    """Initialize the MCP server with all tools."""
    try:
        logger.info("Initializing All-in-One Crypto Trading MCP Server...")
        
        # Validate configuration
        config.validate_required_config()
        
        # Register all MCP tools
        register_all_tools(server)
        
        logger.info(f"Server initialized successfully with {len(server._tools)} tools")
        
        # Log available tools
        for tool_name in server._tools:
            logger.debug(f"Registered tool: {tool_name}")
        
        return server
    
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


async def main():
    """Main server entry point."""
    try:
        # Set up logging
        setup_logging(level=config.MCP_LOG_LEVEL)
        
        logger.info("Starting All-in-One Crypto Trading MCP Server...")
        logger.info(f"Version: {config.MCP_SERVER_VERSION}")
        logger.info(f"Debug mode: {config.MCP_DEBUG}")
        logger.info(f"Live trading: {config.LIVE}")
        
        # Initialize server
        server = await initialize_server()
        
        # Create notification options
        notification_options = NotificationOptions(
            prompts_changed=True,
            resources_changed=True,
            tools_changed=True
        )
        
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server started successfully")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.MCP_SERVER_NAME,
                    server_version=config.MCP_SERVER_VERSION,
                    capabilities=ClientCapabilities(
                        roots={"prompts": True, "resources": True, "tools": True}
                    )
                ),
                notification_options
            )
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())