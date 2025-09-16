# Getting Started with All-in-One Crypto Trading MCP Server

This guide will help you set up and start using the All-in-One Crypto Trading MCP Server.

## Prerequisites

- Python 3.9 or higher
- Git
- Redis (optional, for caching)
- PostgreSQL (optional, SQLite by default)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cryptomcp/allinone-crypto-trading-mcp-server.git
cd allinone-crypto-trading-mcp-server
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys and preferences:

```bash
nano .env  # or use your preferred editor
```

## Essential Configuration

### Security Settings (Required)

```env
# Production safety switches
LIVE=false                    # Set to true for live trading
AM_I_SURE=false              # Additional confirmation for live trading
MAX_ORDER_USD=1000           # Maximum single order value
DAILY_LOSS_LIMIT_USD=5000    # Daily loss limit
```

### Exchange API Keys (Choose at least one)

```env
# Binance
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=true

# Coinbase Pro
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key
COINBASE_PASSPHRASE=your_coinbase_passphrase
COINBASE_SANDBOX=true
```

### Blockchain RPC Endpoints

```env
# Ethereum
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETH_PRIVATE_KEY=your_ethereum_private_key

# Solana
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key
```

### News and Data APIs

```env
# CryptoPanic News
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key

# Whale Alert
WHALE_ALERT_API_KEY=your_whale_alert_api_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## Running the Server

### 1. Start the MCP Server

```bash
# Using the installed command
allinone-crypto-mcp

# Or using Python module
python -m allinone_crypto_mcp.main
```

### 2. Start the Telegram Bot (Optional)

In a separate terminal:

```bash
python -m allinone_crypto_mcp.telegram.bot
```

## Basic Usage

### MCP Tools

The server provides numerous tools for cryptocurrency operations:

#### Trading Tools
- `execute_trade` - Execute buy/sell orders
- `get_portfolio_balance` - View balances across exchanges
- `get_crypto_price` - Get real-time prices

#### Market Data Tools
- `get_crypto_news` - Latest news with sentiment analysis
- `track_whale_transactions` - Monitor large transactions
- `get_fear_greed_index` - Market sentiment indicator

#### DeFi Tools
- `analyze_dex_pools` - DEX liquidity analysis
- `bridge_tokens` - Cross-chain transfers

### Telegram Commands

Once the Telegram bot is running:

- `/price BTC` - Get Bitcoin price
- `/balance` - View portfolio balances
- `/news BTC` - Get Bitcoin-related news
- `/whales` - Recent whale transactions
- `/fng` - Fear & Greed Index

## Safety Features

### Dry Run Mode

All trading operations default to dry run mode for safety:

```python
# This will simulate the trade
result = await execute_trade(
    symbol="BTC/USDT",
    side="buy",
    amount=0.001,
    dry_run=True  # Default
)
```

### Risk Management

The server includes comprehensive risk management:

- Maximum order size limits
- Daily loss limits
- Position concentration checks
- Correlation analysis
- Emergency stop conditions

### Live Trading Activation

To enable live trading, you must explicitly confirm:

```env
LIVE=true
AM_I_SURE=true
```

## Testing the Setup

### 1. Test Exchange Connection

```python
from cex.trading import get_balances

# This will test your exchange API credentials
balances = await get_balances()
print(balances)
```

### 2. Test Price Data

```python
from cex.market_data import get_price_data

price = await get_price_data("BTC")
print(f"BTC Price: ${price['price']}")
```

### 3. Test News Feed

```python
from addons.news.aggregator import get_news_feed

news = await get_news_feed(coins=["BTC"], limit=5)
for item in news:
    print(f"{item.title} - {item.sentiment}")
```

## Next Steps

1. **Configure Additional Exchanges**: Add API keys for more exchanges
2. **Set Up Blockchain Wallets**: Configure private keys for on-chain operations
3. **Enable Advanced Features**: Configure AI analysis, cross-chain bridges
4. **Monitor and Adjust**: Use risk management tools to monitor performance

## Common Issues

### API Connection Errors

- Verify API keys are correct and have required permissions
- Check if testnet/sandbox mode is enabled
- Ensure IP whitelist includes your server IP

### Module Import Errors

- Verify virtual environment is activated
- Reinstall dependencies: `pip install -e .`
- Check Python version compatibility

### Rate Limiting

- Most APIs have rate limits
- The server includes automatic rate limiting
- Consider upgrading to premium API tiers for higher limits

## Support

- **Documentation**: [docs.cryptomcp.dev](https://docs.cryptomcp.dev)
- **GitHub Issues**: [Report bugs](https://github.com/cryptomcp/allinone-crypto-trading-mcp-server/issues)
- **Telegram**: [@web3botsupport](https://t.me/web3botsupport)
- **Telegram**: [Join community](https://t.me/web3botsupport)

## Security Recommendations

1. **Never commit private keys** to version control
2. **Use testnet/sandbox** for initial testing
3. **Start with small amounts** when going live
4. **Regularly backup** your configuration
5. **Monitor logs** for suspicious activity
6. **Keep dependencies updated** for security patches

Happy trading! 🚀