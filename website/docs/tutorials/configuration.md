# Configuration Guide

Comprehensive configuration guide for setting up the All-in-One Crypto Trading MCP Server for your specific trading needs.

## 🔧 Configuration Overview

The system uses environment variables and configuration files for maximum flexibility and security. All sensitive information is stored in environment variables, while operational settings can be configured through various methods.

**Configuration Sources (in priority order):**
1. Command-line arguments
2. Environment variables
3. `.env` file
4. Configuration file (`config.yaml`)
5. Default values

## 📄 Environment File Setup

### Basic Environment Configuration

#### Create and Edit .env File
```bash
# Copy the template
cp .env.example .env

# Edit with your preferred editor
nano .env          # or vim .env or code .env
```

#### Essential Security Settings
```env
# CRITICAL SAFETY SETTINGS - NEVER SET TO TRUE INITIALLY
LIVE=false                          # Enable live trading (DANGER!)
AM_I_SURE=false                     # Additional confirmation (DANGER!)
DEBUG=true                          # Enable debug mode for testing

# Security
SECRET_KEY=your_generated_secret_key_here_must_be_32_chars_minimum
ENCRYPTION_KEY=another_32_char_key_for_encrypting_sensitive_data

# Environment
ENVIRONMENT=development             # development, staging, production
```

### Exchange Configuration

#### Binance Setup
```env
# Binance Configuration
BINANCE_ENABLED=true
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=true                # Start with testnet!
BINANCE_RATE_LIMIT=1200             # Requests per minute
BINANCE_DEFAULT_LEVERAGE=1          # No leverage initially

# Advanced Binance Settings
BINANCE_RECV_WINDOW=5000            # API recv window (ms)
BINANCE_TIME_OFFSET=0               # Time offset adjustment
BINANCE_AUTO_TIMESTAMP=true         # Auto timestamp adjustment
```

#### Coinbase Pro Setup
```env
# Coinbase Pro Configuration
COINBASE_ENABLED=true
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key  
COINBASE_PASSPHRASE=your_coinbase_passphrase
COINBASE_SANDBOX=true               # Start with sandbox!
COINBASE_RATE_LIMIT=10              # Requests per second
```

#### Additional Exchanges
```env
# Kraken
KRAKEN_ENABLED=false
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET_KEY=your_kraken_secret_key
KRAKEN_TIER=2                       # API tier (1-4)

# Bybit
BYBIT_ENABLED=false
BYBIT_API_KEY=your_bybit_api_key
BYBIT_SECRET_KEY=your_bybit_secret_key
BYBIT_TESTNET=true

# OKX
OKX_ENABLED=false
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase
OKX_SIMULATION=true                 # Start with simulation
```

### Blockchain Configuration

#### Ethereum Network Setup
```env
# Ethereum Configuration
ETH_ENABLED=true
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETH_RPC_URL_BACKUP=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETH_CHAIN_ID=1                      # 1 = mainnet, 5 = goerli testnet
ETH_PRIVATE_KEY=your_ethereum_private_key
ETH_GAS_STRATEGY=medium             # slow, medium, fast, aggressive
ETH_MAX_GAS_PRICE=100               # Max gas price in gwei
ETH_CONFIRMATION_BLOCKS=3           # Confirmation blocks required

# EVM-Compatible Networks
POLYGON_ENABLED=true
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_CHAIN_ID=137
POLYGON_PRIVATE_KEY=your_polygon_private_key

ARBITRUM_ENABLED=true  
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ARBITRUM_CHAIN_ID=42161
ARBITRUM_PRIVATE_KEY=your_arbitrum_private_key

OPTIMISM_ENABLED=true
OPTIMISM_RPC_URL=https://opt-mainnet.g.alchemy.com/v2/YOUR_API_KEY
OPTIMISM_CHAIN_ID=10
OPTIMISM_PRIVATE_KEY=your_optimism_private_key

BASE_ENABLED=true
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY
BASE_CHAIN_ID=8453
BASE_PRIVATE_KEY=your_base_private_key

BSC_ENABLED=true
BSC_RPC_URL=https://bsc-dataseed.binance.org/
BSC_CHAIN_ID=56
BSC_PRIVATE_KEY=your_bsc_private_key

AVALANCHE_ENABLED=true
AVALANCHE_RPC_URL=https://api.avax.network/ext/bc/C/rpc
AVALANCHE_CHAIN_ID=43114
AVALANCHE_PRIVATE_KEY=your_avalanche_private_key
```

#### Solana Configuration
```env
# Solana Configuration
SOLANA_ENABLED=true
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_RPC_URL_BACKUP=https://solana-api.projectserum.com
SOLANA_PRIVATE_KEY=your_solana_private_key
SOLANA_COMMITMENT=confirmed         # processed, confirmed, finalized
SOLANA_SKIP_PREFLIGHT=false
SOLANA_MAX_RETRIES=3
```

### Data Provider Configuration

#### News and Sentiment APIs
```env
# CryptoPanic API
CRYPTOPANIC_ENABLED=true
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key
CRYPTOPANIC_RATE_LIMIT=300          # Requests per hour
CRYPTOPANIC_CURRENCIES=BTC,ETH,SOL,ADA,MATIC

# Whale Alert API
WHALE_ALERT_ENABLED=true
WHALE_ALERT_API_KEY=your_whale_alert_api_key
WHALE_ALERT_MIN_VALUE_USD=1000000   # $1M minimum for alerts

# DexPaprika API
DEXPAPRIKA_ENABLED=true
DEXPAPRIKA_API_KEY=your_dexpaprika_api_key

# Dappier AI API
DAPPIER_ENABLED=true
DAPPIER_API_KEY=your_dappier_api_key

# Fear & Greed Index
FEAR_GREED_ENABLED=true
FEAR_GREED_UPDATE_INTERVAL=3600     # Update every hour
```

#### Price Data Providers
```env
# CoinGecko API
COINGECKO_ENABLED=true
COINGECKO_API_KEY=your_coingecko_api_key
COINGECKO_RATE_LIMIT=50             # Requests per minute

# CoinMarketCap API
COINMARKETCAP_ENABLED=false
COINMARKETCAP_API_KEY=your_cmc_api_key

# Pyth Network
PYTH_ENABLED=true
PYTH_RPC_URL=https://api.pythnet.pyth.network
```

### Database Configuration

#### SQLite (Default)
```env
# SQLite Configuration (Default)
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./data/trading.db
DATABASE_ECHO=false                 # Log SQL queries
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_BACKUP_ENABLED=true
DATABASE_BACKUP_INTERVAL=3600       # Backup every hour
```

#### PostgreSQL (Production)
```env
# PostgreSQL Configuration
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/trading
DATABASE_ECHO=false
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_SSL_MODE=prefer
DATABASE_TIMEOUT=30
DATABASE_RETRY_ATTEMPTS=3
```

#### Redis Configuration
```env
# Redis Configuration (Optional but recommended)
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_SSL=false
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_HEALTH_CHECK_INTERVAL=30
REDIS_MAX_CONNECTIONS=50
```

### Risk Management Configuration

#### Position and Risk Limits
```env
# Position Limits
MAX_SINGLE_POSITION_PCT=20          # 20% max single position
MAX_SECTOR_EXPOSURE_PCT=40          # 40% max sector exposure  
MAX_EXCHANGE_EXPOSURE_PCT=60        # 60% max on single exchange
MAX_DAILY_TRADES=50                 # Max trades per day
MAX_ORDER_SIZE_USD=10000            # Max $10K per order
MIN_ORDER_SIZE_USD=10               # Min $10 per order

# Risk Limits
DAILY_LOSS_LIMIT_USD=5000           # $5K daily loss limit
WEEKLY_LOSS_LIMIT_USD=15000         # $15K weekly loss limit
MONTHLY_LOSS_LIMIT_USD=50000        # $50K monthly loss limit
MAX_DRAWDOWN_PCT=15                 # 15% max portfolio drawdown
PORTFOLIO_VAR_LIMIT_USD=10000       # $10K daily VaR limit

# Leverage and Margin
MAX_LEVERAGE=2                      # 2x maximum leverage
MARGIN_CALL_THRESHOLD=0.8           # 80% margin call threshold
LIQUIDATION_THRESHOLD=0.9           # 90% liquidation threshold
DEFAULT_LEVERAGE=1                  # Default 1x leverage
```

#### Emergency Controls
```env
# Emergency Settings
EMERGENCY_STOP_ENABLED=true
EMERGENCY_LIQUIDATION_THRESHOLD=20  # 20% portfolio loss
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_THRESHOLD=10        # 10% single asset drop
AUTO_STOP_LOSS_ENABLED=true
DEFAULT_STOP_LOSS_PCT=5             # 5% default stop loss
```

### Trading Configuration

#### Order Management
```env
# Order Configuration
DEFAULT_ORDER_TYPE=market           # market, limit, stop, stop_limit
DEFAULT_TIME_IN_FORCE=GTC           # GTC, IOC, FOK
ORDER_TIMEOUT_SECONDS=300           # 5 minute order timeout
MAX_OPEN_ORDERS=50                  # Max open orders
PARTIAL_FILL_ENABLED=true
CANCEL_ALL_ON_SHUTDOWN=true

# Slippage Protection
MAX_SLIPPAGE_PCT=1                  # 1% max slippage
DYNAMIC_SLIPPAGE=true               # Adjust slippage by volatility
SLIPPAGE_BUFFER_PCT=0.1             # 0.1% slippage buffer

# DCA Settings
DCA_ENABLED=true
DCA_MAX_ORDERS=10                   # Max DCA orders
DCA_DEFAULT_INTERVAL=3600           # 1 hour between DCA orders
DCA_PRICE_DEVIATION_PCT=2           # 2% price deviation for DCA
```

#### Strategy Configuration
```env
# Strategy Settings
STRATEGY_ENABLED=true
DEFAULT_STRATEGY=conservative       # conservative, moderate, aggressive
REBALANCING_ENABLED=true
REBALANCING_THRESHOLD_PCT=5         # 5% deviation triggers rebalance
REBALANCING_FREQUENCY=daily         # daily, weekly, monthly

# AI and Signals
AI_SIGNALS_ENABLED=true
AI_CONFIDENCE_THRESHOLD=0.7         # 70% minimum confidence
SIGNAL_DECAY_HOURS=24               # Signals expire after 24h
SENTIMENT_WEIGHT=0.3                # 30% weight for sentiment
TECHNICAL_WEIGHT=0.7                # 70% weight for technical
```

### Notification Configuration

#### Telegram Bot
```env
# Telegram Configuration
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_RATE_LIMIT=30              # Messages per minute
TELEGRAM_AUTO_DELETE_SECONDS=300    # Auto-delete after 5 min

# Notification Settings
NOTIFY_TRADES=true
NOTIFY_ALERTS=true
NOTIFY_ERRORS=true
NOTIFY_WHALE_ACTIVITY=true
NOTIFY_NEWS=true
NOTIFICATION_QUIET_HOURS=22-07      # Quiet hours (10 PM - 7 AM)
```

#### Email Notifications
```env
# Email Configuration
EMAIL_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=notifications@yourcompany.com
EMAIL_RATE_LIMIT=10                 # Max 10 emails per hour
```

#### Telegram Webhooks
```env
# Telegram Configuration  
TELEGRAM_WEBHOOK_ENABLED=false
TELEGRAM_WEBHOOK_URL=your_telegram_webhook_url
TELEGRAM_BOT_USERNAME=CryptoMCP Bot
TELEGRAM_BOT_AVATAR=https://yourdomain.com/avatar.png
```

### Logging Configuration

#### Log Settings
```env
# Logging Configuration
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=detailed                 # simple, detailed, json
LOG_FILE=./logs/trading.log
LOG_MAX_SIZE=100MB                  # Max log file size
LOG_BACKUP_COUNT=10                 # Keep 10 backup files
LOG_ROTATION=daily                  # daily, weekly, size

# Component-specific logging
LOG_TRADING=INFO
LOG_BLOCKCHAIN=DEBUG
LOG_NEWS=INFO  
LOG_TELEGRAM=INFO
LOG_RISK=WARNING
LOG_PERFORMANCE=INFO

# External service logging
LOG_CCXT=WARNING                    # Exchange library logs
LOG_WEB3=WARNING                    # Blockchain library logs
LOG_REQUESTS=WARNING                # HTTP request logs
```

#### Audit Logging
```env
# Audit Configuration
AUDIT_ENABLED=true
AUDIT_LOG_FILE=./logs/audit.log
AUDIT_LOG_TRADES=true
AUDIT_LOG_ADMIN_ACTIONS=true
AUDIT_LOG_API_CALLS=true
AUDIT_RETENTION_DAYS=365            # Keep audit logs for 1 year
```

### Performance Configuration

#### Caching
```env
# Cache Configuration
CACHE_ENABLED=true
CACHE_TYPE=redis                    # memory, redis, memcached
CACHE_DEFAULT_TTL=300               # 5 minutes default TTL
CACHE_PRICE_TTL=10                  # 10 seconds for prices
CACHE_NEWS_TTL=300                  # 5 minutes for news
CACHE_MARKET_DATA_TTL=60            # 1 minute for market data
CACHE_MAX_SIZE=1000                 # Max cache entries (memory cache)
```

#### API Rate Limiting
```env
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STRATEGY=token_bucket    # fixed_window, sliding_window, token_bucket
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_BURST_SIZE=100
RATE_LIMIT_REDIS_KEY_PREFIX=rate_limit:
```

#### Concurrency
```env
# Concurrency Configuration
MAX_CONCURRENT_REQUESTS=10          # Max concurrent API requests
MAX_CONCURRENT_TRADES=5             # Max concurrent trade executions
THREAD_POOL_SIZE=20                 # Thread pool size
ASYNC_LOOP_POLICY=uvloop            # asyncio, uvloop
```

## 📁 Configuration Files

### YAML Configuration (Optional)

#### Create config.yaml
```yaml
# config.yaml - Advanced configuration options
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  debug: false

trading:
  exchanges:
    binance:
      enabled: true
      testnet: true
      default_leverage: 1
      rate_limit_buffer: 0.9
    coinbase:
      enabled: true
      sandbox: true
      rate_limit_buffer: 0.8
  
  risk_management:
    position_sizing:
      method: "kelly"               # fixed, percentage, kelly, volatility
      base_size: 0.05              # 5% base position size
      kelly_fraction: 0.25         # 25% of Kelly criterion
      max_position: 0.20           # 20% max position size
    
    correlation_limits:
      max_correlation: 0.8         # 80% max correlation
      lookback_period: 60          # 60-day correlation window
    
    var_limits:
      confidence_level: 0.95       # 95% confidence VaR
      holding_period: 1            # 1-day holding period
      method: "historical"         # historical, parametric, monte_carlo

blockchain:
  ethereum:
    gas_strategy: "medium"
    max_gas_price: 100
    gas_multiplier: 1.1
    confirmation_blocks: 3
    retry_attempts: 3
    timeout_seconds: 300
  
  solana:
    commitment: "confirmed"
    skip_preflight: false
    max_retries: 3
    timeout_seconds: 30

ai:
  models:
    price_prediction:
      model_type: "ensemble"
      confidence_threshold: 0.7
      lookback_window: 100
    
    sentiment_analysis:
      model_type: "transformer"
      decay_rate: 0.1
      update_frequency: 300        # 5 minutes
    
    signal_generation:
      ensemble_weight: true
      multi_timeframe: true
      risk_adjustment: true

notifications:
  channels:
    telegram:
      enabled: true
      priority_threshold: "medium"
      quiet_hours: ["22:00", "07:00"]
    
    email:
      enabled: false
      priority_threshold: "high"
      batch_notifications: true
      batch_interval: 300          # 5 minutes
    
    telegram:
      enabled: false
      priority_threshold: "high"
```

### Exchange-Specific Configuration

#### Binance Advanced Settings
```yaml
# binance_config.yaml
binance:
  api:
    recv_window: 5000
    time_offset: 0
    auto_timestamp: true
    
  trading:
    default_type: "spot"           # spot, margin, futures
    reduce_only: false
    post_only: false
    
  websocket:
    enabled: true
    heartbeat_interval: 30
    reconnect_attempts: 5
    
  rate_limiting:
    weight_limit: 1200             # Weight per minute
    order_limit: 100               # Orders per 10 seconds
    raw_request_limit: 6100        # Raw requests per 5 minutes
```

## 🔐 Security Configuration

### Secret Management

#### Generate Secure Keys
```python
# Generate secure secret keys
import secrets
import string

def generate_secret_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Generate keys
secret_key = generate_secret_key(32)
encryption_key = generate_secret_key(32)

print(f"SECRET_KEY={secret_key}")
print(f"ENCRYPTION_KEY={encryption_key}")
```

#### Environment Variable Encryption
```bash
# Use a tool like gpg to encrypt sensitive environment variables
gpg --symmetric --cipher-algo AES256 .env
# This creates .env.gpg

# Decrypt when needed
gpg --decrypt .env.gpg > .env
```

### API Key Security

#### Secure API Key Storage
```env
# Use environment-specific keys
BINANCE_API_KEY_DEV=development_api_key
BINANCE_API_KEY_STAGING=staging_api_key
BINANCE_API_KEY_PROD=production_api_key

# Script to select appropriate key based on environment
# In your shell profile (.bashrc, .zshrc):
if [ "$ENVIRONMENT" = "production" ]; then
    export BINANCE_API_KEY="$BINANCE_API_KEY_PROD"
elif [ "$ENVIRONMENT" = "staging" ]; then
    export BINANCE_API_KEY="$BINANCE_API_KEY_STAGING"
else
    export BINANCE_API_KEY="$BINANCE_API_KEY_DEV"
fi
```

### Network Security

#### Firewall Configuration
```bash
# Ubuntu UFW example
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000/tcp              # MCP server port
sudo ufw enable

# Allow specific IPs only (replace with your IP)
sudo ufw allow from 192.168.1.100 to any port 8000
```

## 📊 Monitoring Configuration

### Health Checks

#### Health Check Configuration
```env
# Health Check Settings
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=60            # Check every minute
HEALTH_CHECK_TIMEOUT=10             # 10 second timeout
HEALTH_CHECK_ENDPOINT=/health
HEALTH_CHECK_ALERT_THRESHOLD=3      # Alert after 3 failures

# Component health checks
HEALTH_CHECK_DATABASE=true
HEALTH_CHECK_REDIS=true
HEALTH_CHECK_EXCHANGES=true
HEALTH_CHECK_BLOCKCHAIN=true
HEALTH_CHECK_NEWS_APIS=true
```

### Metrics and Analytics

#### Metrics Configuration
```env
# Metrics Collection
METRICS_ENABLED=true
METRICS_ENDPOINT=/metrics
METRICS_RETENTION_DAYS=30           # Keep metrics for 30 days

# Prometheus configuration (optional)
PROMETHEUS_ENABLED=false
PROMETHEUS_HOST=localhost
PROMETHEUS_PORT=9090
PROMETHEUS_SCRAPE_INTERVAL=15s

# Performance metrics
TRACK_RESPONSE_TIMES=true
TRACK_ERROR_RATES=true
TRACK_THROUGHPUT=true
TRACK_MEMORY_USAGE=true
TRACK_CPU_USAGE=true
```

## 🧪 Testing Configuration

### Test Environment Setup

#### Test Configuration
```env
# Test Environment Variables
TESTING=true
TEST_DATABASE_URL=sqlite:///./test_data/test.db
TEST_REDIS_URL=redis://localhost:6379/15  # Use different DB
TEST_LOG_LEVEL=DEBUG
TEST_TIMEOUT=30

# Mock external services in tests
MOCK_EXCHANGES=true
MOCK_BLOCKCHAIN=true
MOCK_NEWS_APIS=true
MOCK_AI_SERVICES=true

# Test data configuration
TEST_DATA_PATH=./test_data
TEST_FIXTURES_PATH=./tests/fixtures
RESET_TEST_DATA=true                # Reset test data before each test
```

## 🔄 Configuration Validation

### Validate Configuration

#### Configuration Checker Script
```python
# config_validator.py
import os
from typing import Dict, List, Any

class ConfigValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_required_vars(self, required_vars: List[str]):
        """Validate required environment variables."""
        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Required environment variable {var} is missing")
    
    def validate_api_keys(self):
        """Validate API key format and presence."""
        api_keys = {
            'BINANCE_API_KEY': 64,          # Expected length
            'COINBASE_API_KEY': 32,
            'CRYPTOPANIC_API_KEY': 40,
        }
        
        for key, expected_length in api_keys.items():
            value = os.getenv(key)
            if value and len(value) != expected_length:
                self.warnings.append(f"{key} length ({len(value)}) doesn't match expected length ({expected_length})")
    
    def validate_numeric_ranges(self):
        """Validate numeric configuration ranges."""
        numeric_checks = {
            'MAX_SINGLE_POSITION_PCT': (1, 50),
            'DAILY_LOSS_LIMIT_USD': (100, 1000000),
            'MAX_LEVERAGE': (1, 10),
        }
        
        for var, (min_val, max_val) in numeric_checks.items():
            value = os.getenv(var)
            if value:
                try:
                    num_value = float(value)
                    if not (min_val <= num_value <= max_val):
                        self.warnings.append(f"{var} value {num_value} is outside recommended range [{min_val}, {max_val}]")
                except ValueError:
                    self.errors.append(f"{var} is not a valid number: {value}")
    
    def validate_safety_settings(self):
        """Validate critical safety settings."""
        live = os.getenv('LIVE', 'false').lower()
        am_i_sure = os.getenv('AM_I_SURE', 'false').lower()
        
        if live == 'true' or am_i_sure == 'true':
            self.warnings.append("⚠️  LIVE TRADING IS ENABLED! Ensure you understand the risks.")
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all validation checks."""
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        
        self.validate_required_vars(required_vars)
        self.validate_api_keys()
        self.validate_numeric_ranges()
        self.validate_safety_settings()
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }

# Run validation
if __name__ == "__main__":
    validator = ConfigValidator()
    result = validator.run_validation()
    
    if result['errors']:
        print("❌ Configuration Errors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result['warnings']:
        print("⚠️  Configuration Warnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    if result['valid'] and not result['warnings']:
        print("✅ Configuration is valid!")
```

### Run Configuration Check
```bash
# Create and run the validation script
python config_validator.py

# Or use the built-in configuration checker
allinone-crypto-mcp --check-config
```

## 📞 Support

For configuration help:
- **Configuration Support**: config@cryptomcp.dev
- **Security Questions**: security@cryptomcp.dev
- **Performance Tuning**: performance@cryptomcp.dev
- **General Support**: support@cryptomcp.dev

---

**🎯 Next Steps:** Once your configuration is complete, proceed to [First Trade Guide](first-trade.md) to execute your first trade safely in simulation mode.