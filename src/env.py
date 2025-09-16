"""
Environment configuration for the All-in-One Crypto Trading MCP Server.
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # =============================================================================
    # CORE MCP SERVER CONFIGURATION
    # =============================================================================
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "allinone-crypto-mcp")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "2.0.0")
    MCP_HOST: str = os.getenv("MCP_HOST", "localhost")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))
    MCP_DEBUG: bool = os.getenv("MCP_DEBUG", "false").lower() == "true"
    MCP_LOG_LEVEL: str = os.getenv("MCP_LOG_LEVEL", "INFO")

    # =============================================================================
    # SECURITY & RISK MANAGEMENT
    # =============================================================================
    LIVE: bool = os.getenv("LIVE", "false").lower() == "true"
    AM_I_SURE: bool = os.getenv("AM_I_SURE", "false").lower() == "true"
    MAX_ORDER_USD: float = float(os.getenv("MAX_ORDER_USD", "1000"))
    DAILY_LOSS_LIMIT_USD: float = float(os.getenv("DAILY_LOSS_LIMIT_USD", "5000"))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/crypto_mcp.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # =============================================================================
    # CENTRALIZED EXCHANGE INTEGRATIONS
    # =============================================================================
    # Binance
    BINANCE_API_KEY: Optional[str] = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY: Optional[str] = os.getenv("BINANCE_SECRET_KEY")
    BINANCE_TESTNET: bool = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

    # Coinbase Pro
    COINBASE_API_KEY: Optional[str] = os.getenv("COINBASE_API_KEY")
    COINBASE_SECRET_KEY: Optional[str] = os.getenv("COINBASE_SECRET_KEY")
    COINBASE_PASSPHRASE: Optional[str] = os.getenv("COINBASE_PASSPHRASE")
    COINBASE_SANDBOX: bool = os.getenv("COINBASE_SANDBOX", "true").lower() == "true"

    # Kraken
    KRAKEN_API_KEY: Optional[str] = os.getenv("KRAKEN_API_KEY")
    KRAKEN_SECRET_KEY: Optional[str] = os.getenv("KRAKEN_SECRET_KEY")

    # Bybit
    BYBIT_API_KEY: Optional[str] = os.getenv("BYBIT_API_KEY")
    BYBIT_SECRET_KEY: Optional[str] = os.getenv("BYBIT_SECRET_KEY")
    BYBIT_TESTNET: bool = os.getenv("BYBIT_TESTNET", "true").lower() == "true"

    # OKX
    OKX_API_KEY: Optional[str] = os.getenv("OKX_API_KEY")
    OKX_SECRET_KEY: Optional[str] = os.getenv("OKX_SECRET_KEY")
    OKX_PASSPHRASE: Optional[str] = os.getenv("OKX_PASSPHRASE")
    OKX_SANDBOX: bool = os.getenv("OKX_SANDBOX", "true").lower() == "true"

    # =============================================================================
    # EVM BLOCKCHAIN CONFIGURATION
    # =============================================================================
    # Ethereum
    ETH_RPC_URL: str = os.getenv("ETH_RPC_URL", "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY")
    ETH_PRIVATE_KEY: Optional[str] = os.getenv("ETH_PRIVATE_KEY")
    ETH_CHAIN_ID: int = int(os.getenv("ETH_CHAIN_ID", "1"))

    # Polygon
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL", "https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY")
    POLYGON_PRIVATE_KEY: Optional[str] = os.getenv("POLYGON_PRIVATE_KEY")
    POLYGON_CHAIN_ID: int = int(os.getenv("POLYGON_CHAIN_ID", "137"))

    # Arbitrum
    ARBITRUM_RPC_URL: str = os.getenv("ARBITRUM_RPC_URL", "https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY")
    ARBITRUM_PRIVATE_KEY: Optional[str] = os.getenv("ARBITRUM_PRIVATE_KEY")
    ARBITRUM_CHAIN_ID: int = int(os.getenv("ARBITRUM_CHAIN_ID", "42161"))

    # Optimism
    OPTIMISM_RPC_URL: str = os.getenv("OPTIMISM_RPC_URL", "https://opt-mainnet.g.alchemy.com/v2/YOUR_API_KEY")
    OPTIMISM_PRIVATE_KEY: Optional[str] = os.getenv("OPTIMISM_PRIVATE_KEY")
    OPTIMISM_CHAIN_ID: int = int(os.getenv("OPTIMISM_CHAIN_ID", "10"))

    # Base
    BASE_RPC_URL: str = os.getenv("BASE_RPC_URL", "https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY")
    BASE_PRIVATE_KEY: Optional[str] = os.getenv("BASE_PRIVATE_KEY")
    BASE_CHAIN_ID: int = int(os.getenv("BASE_CHAIN_ID", "8453"))

    # BSC
    BSC_RPC_URL: str = os.getenv("BSC_RPC_URL", "https://bsc-dataseed1.binance.org/")
    BSC_PRIVATE_KEY: Optional[str] = os.getenv("BSC_PRIVATE_KEY")
    BSC_CHAIN_ID: int = int(os.getenv("BSC_CHAIN_ID", "56"))

    # Avalanche
    AVAX_RPC_URL: str = os.getenv("AVAX_RPC_URL", "https://api.avax.network/ext/bc/C/rpc")
    AVAX_PRIVATE_KEY: Optional[str] = os.getenv("AVAX_PRIVATE_KEY")
    AVAX_CHAIN_ID: int = int(os.getenv("AVAX_CHAIN_ID", "43114"))

    # =============================================================================
    # SOLANA BLOCKCHAIN CONFIGURATION
    # =============================================================================
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    SOLANA_WS_URL: str = os.getenv("SOLANA_WS_URL", "wss://api.mainnet-beta.solana.com")
    SOLANA_PRIVATE_KEY: Optional[str] = os.getenv("SOLANA_PRIVATE_KEY")
    SOLANA_COMMITMENT: str = os.getenv("SOLANA_COMMITMENT", "confirmed")

    # Jupiter DEX
    JUPITER_API_URL: str = os.getenv("JUPITER_API_URL", "https://quote-api.jup.ag/v6")

    # Raydium
    RAYDIUM_API_URL: str = os.getenv("RAYDIUM_API_URL", "https://api.raydium.io/v2")

    # Orca
    ORCA_API_URL: str = os.getenv("ORCA_API_URL", "https://api.orca.so")

    # Pyth Network
    PYTH_NETWORK_URL: str = os.getenv("PYTH_NETWORK_URL", "https://hermes.pyth.network")
    PYTH_API_KEY: Optional[str] = os.getenv("PYTH_API_KEY")

    # =============================================================================
    # AI & SENTIMENT ANALYSIS
    # =============================================================================
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")

    # =============================================================================
    # TELEGRAM BOT CONFIGURATION
    # =============================================================================
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_ADMIN_IDS: List[str] = os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if os.getenv("TELEGRAM_ADMIN_IDS") else []
    TELEGRAM_WEBHOOK_URL: Optional[str] = os.getenv("TELEGRAM_WEBHOOK_URL")

    # =============================================================================
    # NEWS & MARKET DATA PROVIDERS
    # =============================================================================
    # CryptoPanic
    CRYPTOPANIC_API_KEY: Optional[str] = os.getenv("CRYPTOPANIC_API_KEY")
    CRYPTOPANIC_BASE_URL: str = os.getenv("CRYPTOPANIC_BASE_URL", "https://cryptopanic.com/api/v1")

    # Dappier
    DAPPIER_MCP_URL: str = os.getenv("DAPPIER_MCP_URL", "http://localhost:8001")
    DAPPIER_API_KEY: Optional[str] = os.getenv("DAPPIER_API_KEY")

    # Fear & Greed Index
    FEARGREED_API_URL: str = os.getenv("FEARGREED_API_URL", "https://api.alternative.me/fng/")

    # CoinGecko
    COINGECKO_API_KEY: Optional[str] = os.getenv("COINGECKO_API_KEY")
    COINGECKO_PRO_API_URL: str = os.getenv("COINGECKO_PRO_API_URL", "https://pro-api.coingecko.com/api/v3")

    # CoinMarketCap
    CMC_API_KEY: Optional[str] = os.getenv("CMC_API_KEY")
    CMC_BASE_URL: str = os.getenv("CMC_BASE_URL", "https://pro-api.coinmarketcap.com/v1")

    # =============================================================================
    # WHALE TRACKING & SIGNALS
    # =============================================================================
    WHALE_ALERT_API_KEY: Optional[str] = os.getenv("WHALE_ALERT_API_KEY")
    WHALE_ALERT_BASE_URL: str = os.getenv("WHALE_ALERT_BASE_URL", "https://api.whale-alert.io/v1")
    
    WHALE_THRESHOLD_BTC: float = float(os.getenv("WHALE_THRESHOLD_BTC", "100"))
    WHALE_THRESHOLD_ETH: float = float(os.getenv("WHALE_THRESHOLD_ETH", "1000"))
    WHALE_THRESHOLD_USD: float = float(os.getenv("WHALE_THRESHOLD_USD", "1000000"))

    # =============================================================================
    # DEX ANALYTICS & POOL DATA
    # =============================================================================
    DEXPAPRIKA_API_KEY: Optional[str] = os.getenv("DEXPAPRIKA_API_KEY")
    DEXPAPRIKA_BASE_URL: str = os.getenv("DEXPAPRIKA_BASE_URL", "https://api.dexpaprika.com/v1")
    
    DEXSCREENER_BASE_URL: str = os.getenv("DEXSCREENER_BASE_URL", "https://api.dexscreener.com/latest")
    
    THEGRAPH_API_KEY: Optional[str] = os.getenv("THEGRAPH_API_KEY")
    UNISWAP_SUBGRAPH_URL: str = os.getenv("UNISWAP_SUBGRAPH_URL", "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")

    # =============================================================================
    # CROSS-CHAIN BRIDGES & SERVICES
    # =============================================================================
    WORMHOLE_RPC_URL: str = os.getenv("WORMHOLE_RPC_URL", "https://wormhole-v2-mainnet-api.certus.one")
    
    DEBRIDGE_API_URL: str = os.getenv("DEBRIDGE_API_URL", "https://deswap.debridge.finance/v1.0")
    DEBRIDGE_API_KEY: Optional[str] = os.getenv("DEBRIDGE_API_KEY")

    # =============================================================================
    # EXTERNAL MCP SERVICES
    # =============================================================================
    FREE_USDC_MCP_URL: str = os.getenv("FREE_USDC_MCP_URL", "http://localhost:8002")
    BASE_USDC_CONTRACT: str = os.getenv("BASE_USDC_CONTRACT", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
    
    GOAT_MCP_URL: str = os.getenv("GOAT_MCP_URL", "http://localhost:8003")
    GOAT_PROXY_ENABLED: bool = os.getenv("GOAT_PROXY_ENABLED", "true").lower() == "true"
    
    SOLANA_AGENT_MCP_URL: str = os.getenv("SOLANA_AGENT_MCP_URL", "http://localhost:8004")
    SOLANA_AGENT_ENABLED: bool = os.getenv("SOLANA_AGENT_ENABLED", "true").lower() == "true"
    
    HEURIST_MESH_URL: str = os.getenv("HEURIST_MESH_URL", "http://localhost:8005")
    HEURIST_API_KEY: Optional[str] = os.getenv("HEURIST_API_KEY")

    # =============================================================================
    # BANKLESS ONCHAIN INTEGRATION
    # =============================================================================
    BANKLESS_API_TOKEN: Optional[str] = os.getenv("BANKLESS_API_TOKEN")
    BANKLESS_BASE_URL: str = os.getenv("BANKLESS_BASE_URL", "https://api.bankless.com/v1")

    # =============================================================================
    # PERFORMANCE & CACHING
    # =============================================================================
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "50"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "1"))

    # =============================================================================
    # ADVANCED FEATURES
    # =============================================================================
    MEV_PROTECTION_ENABLED: bool = os.getenv("MEV_PROTECTION_ENABLED", "true").lower() == "true"
    FLASHBOTS_RELAY_URL: str = os.getenv("FLASHBOTS_RELAY_URL", "https://relay.flashbots.net")
    SANDWICH_PROTECTION: bool = os.getenv("SANDWICH_PROTECTION", "true").lower() == "true"
    ADVANCED_ORDERS_ENABLED: bool = os.getenv("ADVANCED_ORDERS_ENABLED", "true").lower() == "true"
    AUTO_REBALANCE_ENABLED: bool = os.getenv("AUTO_REBALANCE_ENABLED", "false").lower() == "true"
    REBALANCE_THRESHOLD_PERCENT: float = float(os.getenv("REBALANCE_THRESHOLD_PERCENT", "5"))

    @classmethod
    def validate_required_config(cls) -> None:
        """Validate that required configuration is present."""
        required_for_production = [
            ("LIVE", "Production mode requires explicit LIVE setting"),
        ]
        
        if cls.LIVE:
            required_for_production.extend([
                ("AM_I_SURE", "Production trading requires AM_I_SURE confirmation"),
            ])
        
        missing = []
        for var_name, description in required_for_production:
            if not getattr(cls, var_name, None):
                missing.append(f"{var_name}: {description}")
        
        if missing:
            raise ValueError(f"Missing required configuration:\n" + "\n".join(missing))

    @classmethod
    def get_chain_config(cls, chain: str) -> dict:
        """Get chain-specific configuration."""
        chain_configs = {
            "ethereum": {
                "rpc_url": cls.ETH_RPC_URL,
                "private_key": cls.ETH_PRIVATE_KEY,
                "chain_id": cls.ETH_CHAIN_ID,
            },
            "polygon": {
                "rpc_url": cls.POLYGON_RPC_URL,
                "private_key": cls.POLYGON_PRIVATE_KEY,
                "chain_id": cls.POLYGON_CHAIN_ID,
            },
            "arbitrum": {
                "rpc_url": cls.ARBITRUM_RPC_URL,
                "private_key": cls.ARBITRUM_PRIVATE_KEY,
                "chain_id": cls.ARBITRUM_CHAIN_ID,
            },
            "optimism": {
                "rpc_url": cls.OPTIMISM_RPC_URL,
                "private_key": cls.OPTIMISM_PRIVATE_KEY,
                "chain_id": cls.OPTIMISM_CHAIN_ID,
            },
            "base": {
                "rpc_url": cls.BASE_RPC_URL,
                "private_key": cls.BASE_PRIVATE_KEY,
                "chain_id": cls.BASE_CHAIN_ID,
            },
            "bsc": {
                "rpc_url": cls.BSC_RPC_URL,
                "private_key": cls.BSC_PRIVATE_KEY,
                "chain_id": cls.BSC_CHAIN_ID,
            },
            "avalanche": {
                "rpc_url": cls.AVAX_RPC_URL,
                "private_key": cls.AVAX_PRIVATE_KEY,
                "chain_id": cls.AVAX_CHAIN_ID,
            },
        }
        return chain_configs.get(chain.lower(), {})


# Global config instance
config = Config()