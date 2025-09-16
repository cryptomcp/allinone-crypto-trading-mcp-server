# Trading API Reference

Complete API reference for trading operations including order management, portfolio tracking, and execution controls.

## 🔄 Trade Execution

### execute_trade

Execute a cryptocurrency trade on a specified exchange.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair symbol (e.g., "BTC/USDT") |
| `side` | OrderSide | Yes | Order side ("buy" or "sell") |
| `amount` | Decimal | Yes | Order amount in base currency |
| `order_type` | OrderType | Yes | Order type ("market", "limit", "stop_loss", etc.) |
| `price` | Decimal | No | Limit price for limit orders |
| `stop_price` | Decimal | No | Stop price for stop orders |
| `exchange` | Exchange | Yes | Exchange to trade on |
| `dry_run` | boolean | No | Simulate trade execution (default: true) |
| `time_in_force` | string | No | Time in force ("GTC", "IOC", "FOK") |
| `reduce_only` | boolean | No | Reduce-only order flag |

#### Response

```json
{
  "success": true,
  "data": {
    "order_id": "12345678",
    "symbol": "BTC/USDT",
    "side": "buy",
    "amount": 0.001,
    "price": 45230.50,
    "cost": 45.23,
    "fees": 0.045,
    "status": "filled",
    "timestamp": "2024-03-15T10:30:00Z",
    "exchange": "binance"
  },
  "message": "Trade executed successfully",
  "timestamp": "2024-03-15T10:30:00Z"
}
```

#### Examples

**Market Buy Order:**
```python
result = await execute_trade(
    symbol="BTC/USDT",
    side="buy",
    amount=0.001,
    order_type="market",
    exchange="binance",
    dry_run=True
)
```

**Limit Sell Order:**
```python
result = await execute_trade(
    symbol="ETH/USDT",
    side="sell", 
    amount=1.0,
    order_type="limit",
    price=2500.00,
    exchange="coinbase",
    time_in_force="GTC"
)
```

**Stop Loss Order:**
```python
result = await execute_trade(
    symbol="SOL/USDT",
    side="sell",
    amount=10.0,
    order_type="stop_loss",
    stop_price=90.00,
    exchange="binance"
)
```

### batch_execute_trades

Execute multiple trades simultaneously.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `trades` | array | Yes | Array of trade objects |
| `execution_strategy` | string | No | "parallel", "sequential", "smart" |
| `dry_run` | boolean | No | Simulate all trades (default: true) |

#### Response

```json
{
  "success": true,
  "data": {
    "executed_count": 3,
    "failed_count": 0,
    "total_cost": 1523.45,
    "total_fees": 1.52,
    "execution_time": 2.34,
    "trades": [
      {
        "order_id": "12345678",
        "symbol": "BTC/USDT",
        "status": "filled"
      }
    ]
  },
  "message": "Batch execution completed"
}
```

## 📊 Portfolio Management

### get_portfolio_balance

Get comprehensive portfolio balances across exchanges and wallets.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | Exchange | No | Filter by specific exchange |
| `currency` | string | No | Filter by specific currency |
| `include_zero` | boolean | No | Include zero balances (default: false) |
| `include_estimated` | boolean | No | Include estimated values (default: true) |

#### Response

```json
{
  "success": true,
  "data": {
    "total_usd": 10000.00,
    "total_btc": 0.22,
    "assets": [
      {
        "symbol": "BTC",
        "amount": 0.22,
        "usd_value": 9950.60,
        "percentage": 99.51,
        "exchange": "binance",
        "available": 0.22,
        "locked": 0.0
      },
      {
        "symbol": "USDT", 
        "amount": 49.40,
        "usd_value": 49.40,
        "percentage": 0.49,
        "exchange": "binance",
        "available": 49.40,
        "locked": 0.0
      }
    ],
    "by_exchange": {
      "binance": 10000.00,
      "coinbase": 0.00
    }
  },
  "message": "Portfolio balance retrieved"
}
```

### get_portfolio_performance

Get portfolio performance metrics and analytics.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | No | Time period ("1h", "24h", "7d", "30d", "1y") |
| `benchmark` | string | No | Benchmark symbol for comparison |
| `include_breakdown` | boolean | No | Include asset breakdown (default: true) |

#### Response

```json
{
  "success": true,
  "data": {
    "total_return": 12.5,
    "total_return_usd": 1250.00,
    "realized_pnl": 850.00,
    "unrealized_pnl": 400.00,
    "best_performer": {
      "symbol": "SOL",
      "return": 45.2
    },
    "worst_performer": {
      "symbol": "ADA", 
      "return": -8.3
    },
    "sharpe_ratio": 1.85,
    "max_drawdown": 15.2,
    "win_rate": 68.5,
    "profit_factor": 2.1,
    "benchmark_comparison": {
      "symbol": "BTC",
      "outperformance": 3.2
    }
  },
  "message": "Performance metrics calculated"
}
```

## 📋 Order Management

### get_orders

Retrieve order history and status.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status ("open", "closed", "cancelled", "all") |
| `symbol` | string | No | Filter by trading pair |
| `exchange` | Exchange | No | Filter by exchange |
| `limit` | integer | No | Maximum number of orders (default: 50) |
| `start_date` | string | No | Start date (ISO format) |
| `end_date` | string | No | End date (ISO format) |

#### Response

```json
{
  "success": true,
  "data": [
    {
      "order_id": "12345678",
      "symbol": "BTC/USDT",
      "side": "buy",
      "amount": 0.001,
      "filled": 0.001,
      "price": 45230.50,
      "average_price": 45225.30,
      "cost": 45.23,
      "fees": 0.045,
      "status": "closed",
      "order_type": "market",
      "timestamp": "2024-03-15T10:30:00Z",
      "exchange": "binance"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 50,
    "has_next": true
  },
  "message": "Orders retrieved successfully"
}
```

### cancel_order

Cancel a specific order.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `order_id` | string | Yes | Order ID to cancel |
| `symbol` | string | Yes | Trading pair symbol |
| `exchange` | Exchange | Yes | Exchange where order exists |

#### Response

```json
{
  "success": true,
  "data": {
    "order_id": "12345678",
    "symbol": "BTC/USDT", 
    "status": "cancelled",
    "remaining_amount": 0.0005,
    "cancelled_at": "2024-03-15T10:35:00Z"
  },
  "message": "Order cancelled successfully"
}
```

### cancel_all_orders

Cancel all open orders.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Cancel orders for specific symbol only |
| `exchange` | Exchange | No | Cancel orders on specific exchange only |
| `side` | OrderSide | No | Cancel only buy or sell orders |

#### Response

```json
{
  "success": true,
  "data": {
    "cancelled_count": 5,
    "failed_count": 0,
    "cancelled_orders": [
      {
        "order_id": "12345678",
        "symbol": "BTC/USDT",
        "status": "cancelled"
      }
    ]
  },
  "message": "All orders cancelled successfully"
}
```

## 🎯 Advanced Trading

### create_dca_strategy

Create a Dollar-Cost Averaging strategy.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair symbol |
| `amount_usd` | Decimal | Yes | USD amount per interval |
| `frequency` | string | Yes | "daily", "weekly", "monthly" |
| `duration_days` | integer | No | Strategy duration in days |
| `start_date` | string | No | Start date (default: now) |
| `price_deviation_trigger` | Decimal | No | Price deviation to trigger buy |
| `dry_run` | boolean | No | Simulate strategy (default: true) |

#### Response

```json
{
  "success": true,
  "data": {
    "strategy_id": "dca_123456",
    "symbol": "BTC/USDT",
    "amount_per_interval": 100.00,
    "frequency": "weekly",
    "total_investment": 1200.00,
    "expected_purchases": 12,
    "next_execution": "2024-03-22T10:00:00Z",
    "status": "active"
  },
  "message": "DCA strategy created successfully"
}
```

### create_grid_strategy

Create a grid trading strategy.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair symbol |
| `grid_range_low` | Decimal | Yes | Lower price bound |
| `grid_range_high` | Decimal | Yes | Upper price bound |
| `grid_levels` | integer | Yes | Number of grid levels |
| `total_investment` | Decimal | Yes | Total investment amount |
| `profit_per_grid` | Decimal | No | Target profit per grid level |
| `dry_run` | boolean | No | Simulate strategy (default: true) |

#### Response

```json
{
  "success": true,
  "data": {
    "strategy_id": "grid_789012",
    "symbol": "ETH/USDT",
    "grid_levels": 20,
    "investment_per_level": 50.00,
    "profit_target_per_grid": 1.0,
    "buy_orders_placed": 10,
    "sell_orders_placed": 10,
    "status": "active"
  },
  "message": "Grid strategy created successfully"
}
```

### modify_order

Modify an existing order.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `order_id` | string | Yes | Order ID to modify |
| `symbol` | string | Yes | Trading pair symbol |
| `new_amount` | Decimal | No | New order amount |
| `new_price` | Decimal | No | New order price |
| `exchange` | Exchange | Yes | Exchange where order exists |

#### Response

```json
{
  "success": true,
  "data": {
    "order_id": "12345678",
    "symbol": "BTC/USDT",
    "old_price": 45000.00,
    "new_price": 44500.00,
    "old_amount": 0.001,
    "new_amount": 0.0015,
    "status": "modified",
    "modified_at": "2024-03-15T10:40:00Z"
  },
  "message": "Order modified successfully"
}
```

## 📊 Trade Analytics

### get_trade_statistics

Get comprehensive trading statistics.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | No | Analysis period ("7d", "30d", "90d", "1y") |
| `symbol` | string | No | Filter by trading pair |
| `exchange` | Exchange | No | Filter by exchange |
| `include_fees` | boolean | No | Include fee analysis (default: true) |

#### Response

```json
{
  "success": true,
  "data": {
    "total_trades": 156,
    "winning_trades": 98,
    "losing_trades": 58,
    "win_rate": 62.8,
    "profit_factor": 1.85,
    "average_win": 125.50,
    "average_loss": 75.30,
    "largest_win": 850.00,
    "largest_loss": 320.00,
    "total_fees": 145.60,
    "net_profit": 2150.40,
    "sharpe_ratio": 1.92,
    "sortino_ratio": 2.45,
    "max_drawdown": 8.5,
    "recovery_factor": 3.2
  },
  "message": "Trade statistics calculated"
}
```

### get_position_analysis

Analyze current positions with risk metrics.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_correlations` | boolean | No | Include correlation analysis |
| `risk_free_rate` | Decimal | No | Risk-free rate for calculations |
| `confidence_level` | Decimal | No | VaR confidence level (default: 0.95) |

#### Response

```json
{
  "success": true,
  "data": {
    "total_positions": 5,
    "total_exposure": 9850.60,
    "leverage_ratio": 1.2,
    "positions": [
      {
        "symbol": "BTC",
        "amount": 0.22,
        "market_value": 9950.60,
        "unrealized_pnl": 450.60,
        "position_size_pct": 99.5,
        "risk_metrics": {
          "var_1d": 795.60,
          "volatility": 65.2,
          "beta": 1.0,
          "correlation_to_portfolio": 0.95
        }
      }
    ],
    "portfolio_risk": {
      "total_var": 825.30,
      "portfolio_volatility": 58.7,
      "sharpe_ratio": 1.85,
      "max_correlation": 0.85
    }
  },
  "message": "Position analysis completed"
}
```

## 🔒 Risk Controls

### set_position_limits

Configure position and risk limits.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `max_position_size_usd` | Decimal | No | Maximum position size in USD |
| `max_position_size_pct` | Decimal | No | Maximum position as % of portfolio |
| `max_daily_loss_usd` | Decimal | No | Maximum daily loss in USD |
| `max_leverage` | Decimal | No | Maximum leverage allowed |
| `stop_loss_pct` | Decimal | No | Default stop loss percentage |

#### Response

```json
{
  "success": true,
  "data": {
    "max_position_size_usd": 5000.00,
    "max_position_size_pct": 20.0,
    "max_daily_loss_usd": 500.00,
    "max_leverage": 2.0,
    "stop_loss_pct": 5.0,
    "effective_date": "2024-03-15T10:45:00Z"
  },
  "message": "Risk limits updated successfully"
}
```

### emergency_stop_trading

Immediately stop all trading activities.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cancel_orders` | boolean | No | Cancel all open orders (default: true) |
| `liquidate_positions` | boolean | No | Liquidate all positions (default: false) |
| `reason` | string | No | Reason for emergency stop |

#### Response

```json
{
  "success": true,
  "data": {
    "emergency_stop_time": "2024-03-15T10:50:00Z",
    "orders_cancelled": 12,
    "positions_liquidated": 0,
    "trading_suspended": true,
    "reason": "Manual emergency stop"
  },
  "message": "Emergency stop executed successfully"
}
```

## 📈 Performance Attribution

### get_performance_attribution

Analyze performance attribution by various factors.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | No | Analysis period |
| `attribution_method` | string | No | "brinson", "factor", "holdings" |
| `benchmark` | string | No | Benchmark for comparison |

#### Response

```json
{
  "success": true,
  "data": {
    "total_return": 15.6,
    "benchmark_return": 12.3,
    "excess_return": 3.3,
    "attribution": {
      "asset_allocation": 1.8,
      "security_selection": 1.2,
      "interaction": 0.3
    },
    "sector_attribution": {
      "crypto_large_cap": 2.1,
      "crypto_mid_cap": 0.8,
      "defi_tokens": 0.4
    }
  },
  "message": "Performance attribution calculated"
}
```

## 🔄 Error Handling

### Common Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `INSUFFICIENT_BALANCE` | Insufficient balance for trade | Not enough funds |
| `INVALID_SYMBOL` | Invalid trading symbol | Symbol not supported |
| `ORDER_NOT_FOUND` | Order not found | Order ID doesn't exist |
| `EXCHANGE_ERROR` | Exchange API error | Exchange-specific error |
| `RISK_LIMIT_EXCEEDED` | Risk limit exceeded | Trade violates risk rules |
| `MARKET_CLOSED` | Market is closed | Trading not available |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | Too many requests |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Insufficient USDT balance for trade",
    "details": {
      "required": 1000.00,
      "available": 850.50,
      "shortfall": 149.50
    }
  },
  "timestamp": "2024-03-15T10:55:00Z"
}
```

## 📞 Support

For trading API support:
- **Trading API**: trading-api@cryptomcp.dev
- **Order Issues**: orders@cryptomcp.dev
- **Performance Questions**: performance@cryptomcp.dev
- **Technical Support**: support@cryptomcp.dev

---

**📊 Ready to trade?** Check out our [First Trade Guide](../tutorials/first-trade.md) to get started safely.