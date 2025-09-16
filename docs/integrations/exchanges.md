# Exchange Integration Guide

Complete guide for integrating and configuring cryptocurrency exchanges with the All-in-One Crypto Trading MCP Server.

## 🏛️ Supported Exchanges

### Tier 1 Exchanges (Fully Supported)

#### Binance
- **Market Coverage**: Spot, Futures, Options, Margin
- **Pairs**: 600+ trading pairs
- **Features**: Advanced order types, WebSocket streams, sub-accounts
- **Rate Limits**: 1200 weight/minute, 100 orders/10s
- **Fees**: 0.1% spot, volume discounts available

#### Coinbase Pro
- **Market Coverage**: Spot trading
- **Pairs**: 200+ trading pairs
- **Features**: Advanced order types, FIX API, prime brokerage
- **Rate Limits**: 10 requests/second public, 5/second private
- **Fees**: 0.5% taker, 0.5% maker (volume tiers available)

#### Kraken
- **Market Coverage**: Spot, Futures, Margin
- **Pairs**: 200+ trading pairs
- **Features**: Advanced order types, dark pool, OTC
- **Rate Limits**: Tier-based (1-4), up to 20 calls/second
- **Fees**: 0.26% taker, 0.16% maker

### Tier 2 Exchanges (Standard Support)

#### Bybit
- **Market Coverage**: Spot, Derivatives, Copy Trading
- **Pairs**: 300+ trading pairs
- **Features**: Unified trading account, WebSocket
- **Rate Limits**: 120 requests/minute
- **Fees**: 0.1% spot trading

#### OKX
- **Market Coverage**: Spot, Futures, Options, DEX
- **Pairs**: 400+ trading pairs
- **Features**: Unified account, copy trading
- **Rate Limits**: 60 requests/second
- **Fees**: 0.1% spot, 0.02% futures

## 🔧 Exchange Configuration

### Binance Integration

#### API Setup
```env
# Binance Configuration
BINANCE_ENABLED=true
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Environment Selection
BINANCE_TESTNET=true                # Start with testnet!
BINANCE_SANDBOX=false               # Use testnet instead

# Rate Limiting
BINANCE_RATE_LIMIT=1200            # Requests per minute
BINANCE_ORDER_RATE_LIMIT=100       # Orders per 10 seconds
BINANCE_RATE_LIMIT_BUFFER=0.9      # Use 90% of limits

# Advanced Settings
BINANCE_RECV_WINDOW=5000           # API receive window (ms)
BINANCE_TIME_OFFSET=0              # Time synchronization offset
BINANCE_AUTO_TIMESTAMP=true        # Auto timestamp requests
BINANCE_ENABLE_WEBSOCKET=true      # Enable WebSocket streams
```

#### Creating Binance API Keys
```bash
# Steps to create Binance API keys:
# 1. Log into Binance account
# 2. Go to API Management
# 3. Create API Key
# 4. Configure permissions:
#    - Enable Reading
#    - Enable Spot & Margin Trading
#    - Enable Futures Trading (if needed)
#    - DO NOT enable withdrawals initially
# 5. Set IP restrictions (recommended)
# 6. Save API key and secret securely
```

#### Binance-Specific Features
```python
# Advanced Binance configuration
binance_config = {
    "order_types": [
        "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT",
        "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "LIMIT_MAKER"
    ],
    "time_in_force": ["GTC", "IOC", "FOK"],
    "margin_trading": True,
    "futures_trading": True,
    "sub_accounts": True,
    "auto_borrow": False,  # For margin trading
    "isolated_margin": False
}

await configure_binance_advanced(binance_config)
```

### Coinbase Pro Integration

#### API Setup
```env
# Coinbase Pro Configuration
COINBASE_ENABLED=true
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key
COINBASE_PASSPHRASE=your_coinbase_passphrase

# Environment Selection
COINBASE_SANDBOX=true              # Start with sandbox!
COINBASE_PRODUCTION=false

# Rate Limiting
COINBASE_RATE_LIMIT=10             # Requests per second
COINBASE_BURST_LIMIT=10            # Burst requests

# Advanced Settings
COINBASE_AUTO_PAGINATION=true      # Auto-paginate results
COINBASE_DEFAULT_PRODUCT_ID=BTC-USD
COINBASE_ENABLE_WEBSOCKET=true
```

#### Creating Coinbase Pro API Keys
```bash
# Steps to create Coinbase Pro API keys:
# 1. Log into Coinbase Pro
# 2. Go to Portfolio > API
# 3. Create API Key
# 4. Set permissions:
#    - View
#    - Trade
#    - Transfer (optional, not recommended initially)
# 5. Whitelist IP addresses
# 6. Save all three credentials: key, secret, passphrase
```

#### Coinbase-Specific Features
```python
# Coinbase Pro advanced configuration
coinbase_config = {
    "order_types": ["market", "limit", "stop"],
    "time_in_force": ["GTC", "GTT", "IOC", "FOK"],
    "post_only": True,     # Maker-only orders
    "self_trade_prevention": "decrementAndCancel",
    "sandbox_mode": True,
    "auto_cancel_after": "min"  # Auto-cancel orders
}

await configure_coinbase_advanced(coinbase_config)
```

### Kraken Integration

#### API Setup
```env
# Kraken Configuration
KRAKEN_ENABLED=true
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET_KEY=your_kraken_secret_key

# Rate Limiting (Tier-based)
KRAKEN_API_TIER=2                  # Your Kraken tier (1-4)
KRAKEN_RATE_LIMIT=15               # Calls per minute for tier 2
KRAKEN_RATE_COUNTER_DECAY=2        # Counter decay rate

# Advanced Settings
KRAKEN_OTP=your_2fa_code          # If 2FA enabled
KRAKEN_NONCE_WINDOW=30            # Nonce validation window
KRAKEN_ENABLE_WEBSOCKET=true
```

#### Kraken-Specific Features
```python
# Kraken advanced configuration
kraken_config = {
    "order_types": [
        "market", "limit", "stop-loss", "take-profit",
        "stop-loss-limit", "take-profit-limit", "settle-position"
    ],
    "leverage": [2, 3, 4, 5],  # Available leverage levels
    "margin_trading": True,
    "futures_trading": True,
    "dark_pool": False,        # Dark pool access
    "conditional_close": True   # Conditional close orders
}

await configure_kraken_advanced(kraken_config)
```

### Bybit Integration

#### API Setup
```env
# Bybit Configuration
BYBIT_ENABLED=true
BYBIT_API_KEY=your_bybit_api_key
BYBIT_SECRET_KEY=your_bybit_secret_key

# Environment Selection
BYBIT_TESTNET=true                # Start with testnet!
BYBIT_PRODUCTION=false

# Rate Limiting
BYBIT_RATE_LIMIT=120              # Requests per minute
BYBIT_RATE_LIMIT_BUFFER=0.8       # Use 80% of limits

# Advanced Settings
BYBIT_RECV_WINDOW=5000            # API receive window
BYBIT_UNIFIED_TRADING=true        # Use unified trading account
BYBIT_ENABLE_WEBSOCKET=true
```

### OKX Integration

#### API Setup
```env
# OKX Configuration
OKX_ENABLED=true
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase

# Environment Selection
OKX_SIMULATION=true               # Start with simulation!
OKX_PRODUCTION=false

# Rate Limiting
OKX_RATE_LIMIT=60                 # Requests per second
OKX_BURST_LIMIT=120               # Burst requests

# Advanced Settings
OKX_TRADING_MODE=cash             # cash, cross, isolated
OKX_MARGIN_MODE=cross             # cross, isolated
OKX_POSITION_SIDE=net             # net, long_short_mode
```

## 🔌 Multi-Exchange Management

### Exchange Routing

#### Smart Order Routing
```python
# Configure intelligent order routing
routing_config = {
    "default_exchange": "binance",
    "routing_strategy": "best_price",  # best_price, lowest_fees, fastest_execution
    "price_comparison": True,
    "fee_comparison": True,
    "liquidity_check": True,
    "latency_optimization": True
}

# Set exchange preferences by trading pair
pair_preferences = {
    "BTC/USDT": {
        "preferred_exchanges": ["binance", "coinbase", "kraken"],
        "min_liquidity_usd": 1000000,
        "max_spread_bps": 10
    },
    "ETH/USDT": {
        "preferred_exchanges": ["binance", "coinbase"],
        "min_liquidity_usd": 500000,
        "max_spread_bps": 15
    }
}

await configure_exchange_routing(routing_config, pair_preferences)
```

#### Cross-Exchange Arbitrage
```python
# Set up arbitrage detection
arbitrage_config = {
    "enabled": True,
    "min_profit_bps": 50,           # Minimum 0.5% profit
    "max_position_size": 10000,     # Max $10k position
    "exchanges": ["binance", "coinbase", "kraken"],
    "pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    "include_fees": True,
    "execution_timeout": 30         # 30 seconds max execution
}

await setup_arbitrage_monitoring(arbitrage_config)
```

### Portfolio Distribution

#### Multi-Exchange Balancing
```python
# Configure portfolio distribution across exchanges
distribution_config = {
    "strategy": "risk_weighted",    # equal, risk_weighted, custom
    "rebalancing_frequency": "daily",
    "target_allocations": {
        "binance": 0.40,           # 40% of portfolio
        "coinbase": 0.30,          # 30% of portfolio
        "kraken": 0.20,            # 20% of portfolio
        "cash_reserve": 0.10       # 10% cash reserve
    },
    "rebalancing_threshold": 0.05,  # Rebalance if >5% deviation
    "max_transfer_size": 50000      # Max $50k per transfer
}

await configure_portfolio_distribution(distribution_config)
```

## 🔐 Security Configuration

### API Key Security

#### Key Rotation
```python
# Implement automatic API key rotation
key_rotation_config = {
    "enabled": True,
    "rotation_interval": "90days",   # Rotate every 90 days
    "overlap_period": "7days",       # 7-day overlap for transition
    "notification_advance": "14days", # Notify 14 days before rotation
    "auto_create_new_keys": False,   # Manual approval required
    "backup_old_keys": True          # Keep old keys as backup
}

await setup_api_key_rotation(key_rotation_config)
```

#### Permission Management
```python
# Configure minimal permissions per exchange
permissions_config = {
    "binance": {
        "reading": True,
        "spot_margin_trading": True,
        "futures_trading": False,     # Disable if not needed
        "withdrawals": False,         # Never enable initially
        "internal_transfer": True,
        "sub_account": False
    },
    "coinbase": {
        "view": True,
        "trade": True,
        "transfer": False,            # Disable transfers
        "bypass_two_factor": False    # Always require 2FA
    }
}

await configure_exchange_permissions(permissions_config)
```

### Network Security

#### IP Whitelisting
```python
# Configure IP restrictions
ip_config = {
    "enforce_ip_restrictions": True,
    "allowed_ips": [
        "192.168.1.100",             # Development machine
        "203.0.113.10",              # Production server
        "198.51.100.0/24"            # Office network
    ],
    "allow_dynamic_ip": False,       # Disable for production
    "geo_restrictions": {
        "allowed_countries": ["US", "EU"],
        "blocked_countries": []
    }
}

await configure_ip_restrictions(ip_config)
```

## 📊 Exchange-Specific Features

### Binance Advanced Features

#### Margin Trading
```python
# Configure Binance margin trading
margin_config = {
    "enabled": False,                # Start disabled
    "max_leverage": 3,               # Conservative leverage
    "auto_borrow": False,            # Manual borrow only
    "isolated_margin": True,         # Prefer isolated margin
    "cross_margin": False,
    "interest_rate_threshold": 0.1,  # 10% annual interest max
    "liquidation_buffer": 0.2        # 20% buffer before liquidation
}

await configure_binance_margin(margin_config)
```

#### Futures Trading
```python
# Configure Binance futures (if needed)
futures_config = {
    "enabled": False,                # Start disabled
    "max_leverage": 5,               # Very conservative
    "position_mode": "OneWay",       # OneWay or Hedge
    "margin_type": "ISOLATED",       # ISOLATED or CROSSED
    "auto_add_margin": False,
    "reduce_only": True              # Reduce-only orders
}

await configure_binance_futures(futures_config)
```

### Coinbase Advanced Features

#### Professional Trading
```python
# Configure Coinbase Pro advanced features
pro_config = {
    "post_only_default": True,       # Default to maker orders
    "time_in_force_default": "GTC",  # Good Till Cancelled
    "self_trade_prevention": "decrementAndCancel",
    "stop_orders": True,
    "sandbox_mode": True,            # Start with sandbox
    "fee_tier": "taker"              # Current fee tier
}

await configure_coinbase_pro(pro_config)
```

### Kraken Advanced Features

#### Dark Pool Access
```python
# Configure Kraken dark pool (if eligible)
dark_pool_config = {
    "enabled": False,                # Requires approval
    "min_order_size": 50000,         # $50k minimum
    "iceberg_orders": True,
    "hidden_orders": True,
    "price_improvement": True
}

await configure_kraken_dark_pool(dark_pool_config)
```

## 📈 Performance Optimization

### Connection Management

#### Connection Pooling
```python
# Configure connection pooling for exchanges
connection_config = {
    "pool_size": 10,                 # Connections per exchange
    "max_overflow": 20,              # Additional connections
    "pool_timeout": 30,              # Connection timeout
    "pool_recycle": 3600,            # Recycle every hour
    "retry_attempts": 3,
    "retry_delay": 1.0,              # Exponential backoff
    "keep_alive": True
}

await configure_connection_pooling(connection_config)
```

#### Rate Limit Management
```python
# Intelligent rate limit management
rate_limit_config = {
    "global_enabled": True,
    "per_exchange_limits": {
        "binance": {
            "requests_per_minute": 1200,
            "orders_per_10_seconds": 100,
            "buffer_factor": 0.9
        },
        "coinbase": {
            "requests_per_second": 10,
            "burst_allowance": 10,
            "buffer_factor": 0.8
        }
    },
    "adaptive_limiting": True,       # Adjust based on response times
    "queue_requests": True,          # Queue requests when limited
    "priority_ordering": True        # Prioritize important requests
}

await configure_rate_limiting(rate_limit_config)
```

### Latency Optimization

#### Geographic Optimization
```python
# Optimize for geographic latency
geo_config = {
    "server_region": "us-east-1",    # Your server region
    "exchange_endpoints": {
        "binance": {
            "primary": "https://api.binance.us",
            "backup": "https://api1.binance.us",
            "latency_check": True
        },
        "coinbase": {
            "primary": "https://api.pro.coinbase.com",
            "backup": "https://api-public.sandbox.pro.coinbase.com",
            "latency_check": True
        }
    },
    "auto_failover": True,
    "latency_threshold": 100         # 100ms threshold
}

await configure_geographic_optimization(geo_config)
```

## 🔄 Data Synchronization

### Real-Time Data Streams

#### WebSocket Configuration
```python
# Configure WebSocket streams for real-time data
websocket_config = {
    "enabled": True,
    "streams": {
        "binance": {
            "price_streams": ["btcusdt@ticker", "ethusdt@ticker"],
            "orderbook_streams": ["btcusdt@depth20"],
            "trade_streams": ["btcusdt@trade"],
            "user_streams": True,        # Account updates
            "reconnect_attempts": 5,
            "heartbeat_interval": 30
        },
        "coinbase": {
            "channels": ["ticker", "level2", "matches"],
            "products": ["BTC-USD", "ETH-USD"],
            "heartbeat": True,
            "reconnect_attempts": 5
        }
    },
    "message_buffering": True,
    "buffer_size": 1000,
    "error_handling": "reconnect"
}

await configure_websocket_streams(websocket_config)
```

### Data Aggregation

#### Multi-Exchange Data
```python
# Aggregate data across exchanges
aggregation_config = {
    "price_aggregation": {
        "method": "weighted_average",    # volume-weighted average
        "exchanges": ["binance", "coinbase", "kraken"],
        "weight_by_volume": True,
        "exclude_outliers": True,
        "outlier_threshold": 0.05        # 5% deviation
    },
    "orderbook_aggregation": {
        "depth_levels": 20,
        "merge_similar_prices": True,
        "price_tolerance": 0.001         # 0.1% price tolerance
    },
    "update_frequency": 1000             # Update every second
}

await configure_data_aggregation(aggregation_config)
```

## 🧪 Testing and Validation

### Exchange Testing

#### Connection Testing
```python
# Test all exchange connections
async def test_all_exchanges():
    exchanges = ["binance", "coinbase", "kraken", "bybit", "okx"]
    results = {}
    
    for exchange in exchanges:
        try:
            # Test basic connectivity
            result = await test_exchange_connection(exchange)
            results[exchange] = {
                "connected": result.success,
                "latency": result.latency_ms,
                "rate_limit": result.rate_limit_remaining,
                "features": result.supported_features
            }
        except Exception as e:
            results[exchange] = {
                "connected": False,
                "error": str(e)
            }
    
    return results

# Run tests
test_results = await test_all_exchanges()
for exchange, result in test_results.items():
    status = "✅" if result.get("connected") else "❌"
    print(f"{status} {exchange}: {result}")
```

#### API Functionality Testing
```python
# Test core API functions
async def test_exchange_functionality(exchange_name):
    tests = [
        ("get_markets", get_markets),
        ("get_balance", get_account_balance),
        ("get_orderbook", lambda: get_orderbook("BTC/USDT")),
        ("place_test_order", lambda: place_order("BTC/USDT", "buy", 0.001, dry_run=True))
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = {"success": True, "data": result}
        except Exception as e:
            results[test_name] = {"success": False, "error": str(e)}
    
    return results
```

## 📞 Support

For exchange integration support:
- **Exchange Setup**: exchanges@cryptomcp.dev
- **API Issues**: api@cryptomcp.dev
- **Trading Support**: trading@cryptomcp.dev
- **Technical Help**: support@cryptomcp.dev

### Exchange-Specific Support
- **Binance Issues**: binance-support@cryptomcp.dev
- **Coinbase Issues**: coinbase-support@cryptomcp.dev
- **Kraken Issues**: kraken-support@cryptomcp.dev
- **Multi-Exchange**: multi-exchange@cryptomcp.dev

---

**⚠️ Security Reminder:**
- Always start with testnet/sandbox environments
- Use minimal permissions for API keys
- Implement IP whitelisting where possible
- Never enable withdrawal permissions initially
- Regularly rotate API keys
- Monitor for unusual activity