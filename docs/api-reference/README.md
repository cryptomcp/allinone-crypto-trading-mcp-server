# API Reference

This document provides a comprehensive reference for all available MCP tools in the All-in-One Crypto Trading MCP Server.

## Core Trading Tools

### execute_trade

Execute a cryptocurrency trade on a specified exchange.

**Parameters:**
- `symbol` (string): Trading pair symbol (e.g., "BTC/USDT")
- `side` (OrderSide): Order side ("buy" or "sell")
- `amount` (Decimal): Order amount
- `order_type` (OrderType): Order type ("market", "limit", "stop_loss", etc.)
- `price` (Decimal, optional): Limit price for limit orders
- `stop_price` (Decimal, optional): Stop price for stop orders
- `exchange` (Exchange): Exchange to trade on ("binance", "coinbase", etc.)
- `dry_run` (boolean): Whether to simulate the trade (default: true)

**Returns:**
- `success` (boolean): Whether the operation was successful
- `data` (object): Trade execution results
- `message` (string): Status message

**Example:**
```json
{
  "symbol": "BTC/USDT",
  "side": "buy",
  "amount": 0.001,
  "order_type": "market",
  "exchange": "binance",
  "dry_run": true
}
```

### get_portfolio_balance

Get portfolio balances across exchanges and wallets.

**Parameters:**
- `exchange` (Exchange, optional): Specific exchange filter
- `currency` (string, optional): Specific currency filter
- `include_zero` (boolean): Include zero balances (default: false)

**Returns:**
- `success` (boolean): Operation status
- `data` (array): List of balance objects
- `message` (string): Status message

**Example:**
```json
{
  "exchange": "binance",
  "currency": "BTC",
  "include_zero": false
}
```

### get_crypto_price

Get current cryptocurrency prices and market data.

**Parameters:**
- `symbol` (string): Asset symbol or trading pair
- `vs_currency` (string): Quote currency (default: "USD")
- `include_24h_data` (boolean): Include 24h change data (default: true)

**Returns:**
- `success` (boolean): Operation status
- `data` (object): Price data with 24h metrics
- `message` (string): Status message

## News and Sentiment Tools

### get_crypto_news

Get latest cryptocurrency news with sentiment analysis.

**Parameters:**
- `coins` (array, optional): Filter by specific coins
- `sentiment` (NewsSentiment, optional): Filter by sentiment
- `limit` (integer): Maximum number of news items (default: 20)
- `hours_back` (integer): Hours to look back (default: 24)

**Returns:**
- `success` (boolean): Operation status
- `data` (array): List of news items with sentiment scores
- `message` (string): Status message

**Example:**
```json
{
  "coins": ["BTC", "ETH"],
  "sentiment": "positive",
  "limit": 10,
  "hours_back": 12
}
```

### get_fear_greed_index

Get the current Fear & Greed Index for cryptocurrency markets.

**Parameters:** None

**Returns:**
- `success` (boolean): Operation status
- `data` (object): Fear & Greed Index data
  - `value` (integer): Index value (0-100)
  - `classification` (string): Classification text
  - `sentiment` (string): Market sentiment
  - `trading_suggestion` (string): Trading recommendation
- `message` (string): Status message

## Whale Tracking Tools

### track_whale_transactions

Track large cryptocurrency transactions (whale movements).

**Parameters:**
- `blockchain` (Blockchain, optional): Filter by blockchain
- `min_value_usd` (Decimal): Minimum transaction value (default: 1000000)
- `limit` (integer): Maximum number of transactions (default: 50)
- `hours_back` (integer): Hours to look back (default: 24)

**Returns:**
- `success` (boolean): Operation status
- `data` (object): Whale transaction data
  - `transactions` (array): List of whale transactions
  - `total_value_usd` (Decimal): Total transaction value
  - `unique_addresses` (integer): Number of unique addresses
- `message` (string): Status message

**Example:**
```json
{
  "blockchain": "ethereum",
  "min_value_usd": 5000000,
  "limit": 20,
  "hours_back": 6
}
```

## DEX Analytics Tools

### analyze_dex_pools

Analyze DEX liquidity pools and trading metrics.

**Parameters:**
- `token` (string): Token symbol or address
- `blockchain` (Blockchain): Blockchain network (default: "ethereum")
- `include_pools` (boolean): Include pool data (default: true)
- `include_volume` (boolean): Include volume metrics (default: true)

**Returns:**
- `success` (boolean): Operation status
- `data` (object): DEX pool analysis
  - `pools` (array): List of liquidity pools
  - `total_liquidity_usd` (Decimal): Total liquidity across pools
  - `volume_24h_usd` (Decimal): 24h trading volume
  - `top_dexes` (array): Top DEXes by volume
- `message` (string): Status message

## Cross-Chain Tools

### bridge_tokens

Bridge tokens across different blockchain networks.

**Parameters:**
- `from_chain` (Blockchain): Source blockchain
- `to_chain` (Blockchain): Destination blockchain
- `token` (string): Token symbol to bridge
- `amount` (Decimal): Amount to bridge
- `recipient_address` (string): Recipient address on destination chain
- `bridge_provider` (string): Bridge protocol ("wormhole", "debridge")
- `dry_run` (boolean): Whether to simulate (default: true)

**Returns:**
- `success` (boolean): Operation status
- `data` (object): Bridge operation results
- `message` (string): Status message

**Example:**
```json
{
  "from_chain": "ethereum",
  "to_chain": "arbitrum",
  "token": "USDC",
  "amount": 1000,
  "recipient_address": "0x...",
  "bridge_provider": "wormhole",
  "dry_run": true
}
```

## AI Analysis Tools

### generate_trading_signals

Generate AI-powered trading signals and market analysis.

**Parameters:**
- `symbols` (array): List of trading symbols to analyze
- `timeframe` (string): Analysis timeframe (default: "1h")
- `analysis_type` (string): Type of analysis (default: "technical")
- `include_sentiment` (boolean): Include sentiment analysis (default: true)

**Returns:**
- `success` (boolean): Operation status
- `data` (object): Trading signals
  - `signals` (array): List of generated signals
  - `summary` (object): Analysis summary
- `message` (string): Status message

**Example:**
```json
{
  "symbols": ["BTC/USDT", "ETH/USDT"],
  "timeframe": "4h",
  "analysis_type": "technical",
  "include_sentiment": true
}
```

## Response Format

All tools return responses in the following standardized format:

```json
{
  "success": boolean,
  "data": object | array,
  "message": string,
  "error": string | null,
  "timestamp": string
}
```

## Error Handling

Errors are returned with appropriate error codes and messages:

```json
{
  "success": false,
  "data": null,
  "message": "Operation failed",
  "error": "Detailed error message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limits

- Most tools implement automatic rate limiting
- Exchange-specific limits apply (e.g., Binance: 1200 requests/minute)
- News APIs: 300 requests/hour
- Whale Alert: 100 requests/hour

## Authentication

- Exchange tools require valid API credentials
- Blockchain tools require RPC endpoints and private keys
- News tools require API keys for premium features

## Data Types

### Enums

**OrderSide:**
- `buy`
- `sell`

**OrderType:**
- `market`
- `limit`
- `stop_loss`
- `take_profit`
- `stop_limit`

**Exchange:**
- `binance`
- `coinbase`
- `kraken`
- `bybit`
- `okx`

**Blockchain:**
- `ethereum`
- `polygon`
- `arbitrum`
- `optimism`
- `base`
- `bsc`
- `avalanche`
- `solana`

**NewsSentiment:**
- `positive`
- `negative`
- `neutral`
- `mixed`

## SDK Examples

### Python Example

```python
import asyncio
from allinone_crypto_mcp import CryptoMCPClient

async def main():
    client = CryptoMCPClient()
    
    # Get Bitcoin price
    price = await client.get_crypto_price("BTC")
    print(f"BTC Price: ${price['data']['price']}")
    
    # Get recent news
    news = await client.get_crypto_news(coins=["BTC"], limit=5)
    for item in news['data']:
        print(f"{item['title']} - {item['sentiment']}")
    
    # Execute a dry run trade
    trade = await client.execute_trade(
        symbol="BTC/USDT",
        side="buy",
        amount=0.001,
        dry_run=True
    )
    print(f"Trade result: {trade['message']}")

asyncio.run(main())
```

### JavaScript Example

```javascript
const { CryptoMCPClient } = require('allinone-crypto-mcp');

async function main() {
  const client = new CryptoMCPClient();
  
  // Get portfolio balance
  const balance = await client.getPortfolioBalance();
  console.log('Portfolio:', balance.data);
  
  // Get whale transactions
  const whales = await client.trackWhaleTransactions({
    minValueUsd: 5000000,
    limit: 10
  });
  console.log('Whale transactions:', whales.data.transactions.length);
}

main();
```

For more examples and detailed documentation, visit [allinonecryptomcp.dev](https://allinonecryptomcp.dev).