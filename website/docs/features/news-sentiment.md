# News & Sentiment Analysis

Real-time cryptocurrency news aggregation with AI-powered sentiment analysis and market intelligence.

## 🔍 Overview

The news and sentiment analysis system integrates multiple data sources to provide comprehensive market intelligence:

- **Multi-Source Aggregation**: CryptoPanic, Dappier AI, social media
- **AI-Powered Analysis**: Advanced NLP for sentiment scoring
- **Real-Time Updates**: Live news feeds with instant notifications
- **Historical Tracking**: Sentiment trends and correlation analysis
- **Trading Signals**: News-based trading recommendations

## 📰 News Sources

### CryptoPanic Integration

#### Real-Time News Feed
```python
# Get latest crypto news with sentiment
news = await get_cryptopanic_news(
    coins=["BTC", "ETH"],
    filter_type="hot",  # hot, trending, latest
    limit=20,
    sentiment_filter="positive"
)

for article in news:
    print(f"{article.title}")
    print(f"Sentiment: {article.sentiment} ({article.sentiment_score})")
    print(f"Impact: {article.market_impact}/10")
```

#### News Categories
- **Breaking News**: Major market-moving events
- **Regulatory Updates**: Government and regulatory changes
- **Technology Updates**: Protocol upgrades and developments
- **Market Analysis**: Expert opinions and analysis
- **Social Sentiment**: Community discussions and trends

#### Sentiment Scoring
```python
# Detailed sentiment analysis
sentiment_data = await analyze_news_sentiment(
    article_text="Bitcoin reaches new all-time high...",
    include_metrics=True
)

print(f"Overall Sentiment: {sentiment_data.overall}")
print(f"Confidence: {sentiment_data.confidence}")
print(f"Keywords: {sentiment_data.keywords}")
print(f"Market Impact: {sentiment_data.market_impact}")
```

### Dappier AI Integration

#### AI-Powered Insights
```python
# Get AI analysis and recommendations
insights = await get_dappier_insights(
    query="Bitcoin price analysis",
    include_predictions=True,
    timeframe="24h"
)

print(f"AI Summary: {insights.summary}")
print(f"Price Prediction: {insights.price_prediction}")
print(f"Confidence: {insights.confidence_score}")
```

#### Market Intelligence
- **Trend Analysis**: Identify emerging trends and narratives
- **Correlation Detection**: Find relationships between news and price
- **Anomaly Detection**: Identify unusual market activity
- **Prediction Models**: AI-generated price and trend predictions

### Fear & Greed Index

#### Market Sentiment Indicator
```python
# Get current market sentiment
fng_data = await get_fear_greed_index(
    include_history=True,
    days_back=30
)

print(f"Current Index: {fng_data.value}/100")
print(f"Classification: {fng_data.classification}")
print(f"Trading Suggestion: {fng_data.trading_suggestion}")

# Historical sentiment analysis
for historical in fng_data.history:
    print(f"{historical.date}: {historical.value} - {historical.classification}")
```

#### Sentiment Classifications
- **Extreme Fear (0-24)**: Market oversold, potential buying opportunity
- **Fear (25-49)**: Cautious sentiment, risk-off behavior
- **Neutral (50)**: Balanced market sentiment
- **Greed (51-74)**: Risk-on behavior, potential profit-taking
- **Extreme Greed (75-100)**: Market overbought, potential selling opportunity

## 📊 Sentiment Analysis Features

### Multi-Dimensional Scoring

#### Sentiment Components
```python
# Comprehensive sentiment breakdown
sentiment = await analyze_comprehensive_sentiment(
    symbol="BTC",
    timeframe="24h",
    include_social=True
)

components = sentiment.components
print(f"News Sentiment: {components.news}")
print(f"Social Sentiment: {components.social}")
print(f"Market Sentiment: {components.market}")
print(f"Technical Sentiment: {components.technical}")
print(f"Composite Score: {sentiment.composite_score}")
```

#### Sentiment Sources
- **News Articles**: Traditional crypto news outlets
- **Social Media**: Twitter, Reddit, Telegram sentiment
- **Market Data**: Price action and volume analysis
- **Technical Indicators**: RSI, MACD sentiment signals

### Trend Analysis

#### Sentiment Trends
```python
# Track sentiment changes over time
trend_analysis = await get_sentiment_trends(
    symbol="ETH",
    period="7d",
    granularity="1h"
)

for point in trend_analysis.data:
    print(f"{point.timestamp}: {point.sentiment_score}")
    
# Identify trend reversals
reversals = trend_analysis.reversals
for reversal in reversals:
    print(f"Reversal at {reversal.timestamp}: {reversal.description}")
```

#### Correlation Analysis
```python
# Analyze sentiment-price correlation
correlation = await analyze_sentiment_correlation(
    symbol="BTC",
    sentiment_lag_hours=2,  # Check if sentiment leads price
    period="30d"
)

print(f"Correlation Coefficient: {correlation.coefficient}")
print(f"Lead/Lag Analysis: {correlation.lead_lag}")
print(f"Predictive Power: {correlation.predictive_score}")
```

## 🚨 News-Based Alerts

### Real-Time Notifications

#### Alert Configuration
```python
# Set up sentiment-based alerts
await setup_sentiment_alerts(
    symbol="BTC",
    sentiment_threshold=0.8,  # Alert on high positive sentiment
    news_impact_threshold=8,  # Alert on high-impact news
    channels=["telegram", "email", "sms"]
)

# Custom alert conditions
await create_custom_alert(
    name="Bitcoin Regulatory News",
    conditions={
        "keywords": ["regulation", "SEC", "government"],
        "coins": ["BTC"],
        "sentiment_change": ">0.3",  # 30% sentiment increase
        "time_window": "1h"
    }
)
```

#### Alert Types
- **Breaking News**: Major market-moving announcements
- **Sentiment Spikes**: Rapid sentiment changes
- **Volume Surges**: Unusual news volume
- **Keyword Triggers**: Specific term mentions
- **Correlation Alerts**: Price-sentiment divergence

### Smart Filtering

#### Noise Reduction
```python
# Filter out low-quality news
filtered_news = await get_filtered_news(
    min_source_credibility=7,  # 1-10 scale
    min_impact_score=5,
    exclude_spam=True,
    verified_sources_only=True
)

# Custom filtering rules
await create_news_filter(
    name="High Quality Bitcoin News",
    rules={
        "coins": ["BTC"],
        "min_sentiment_confidence": 0.7,
        "exclude_keywords": ["pump", "moon", "scam"],
        "source_whitelist": ["coindesk", "cointelegraph", "bloomberg"]
    }
)
```

## 🤖 Trading Integration

### News-Based Signals

#### Automated Signal Generation
```python
# Generate trading signals from news
signals = await generate_news_signals(
    symbols=["BTC/USDT", "ETH/USDT"],
    signal_strength_threshold=0.7,
    news_lookback_hours=6
)

for signal in signals:
    print(f"Symbol: {signal.symbol}")
    print(f"Direction: {signal.direction}")
    print(f"Strength: {signal.strength}")
    print(f"News Trigger: {signal.news_trigger}")
    print(f"Confidence: {signal.confidence}")
```

#### Signal Types
- **Breakout Signals**: Based on major announcements
- **Sentiment Reversal**: Extreme sentiment changes
- **Event-Driven**: Specific event types (earnings, partnerships)
- **Momentum Signals**: News momentum continuation
- **Contrarian Signals**: Counter-sentiment positions

### Risk Assessment

#### News-Based Risk Analysis
```python
# Assess market risk from news sentiment
risk_assessment = await assess_news_risk(
    portfolio_symbols=["BTC", "ETH", "ADA"],
    risk_timeframe="24h",
    include_correlation_risk=True
)

print(f"Overall Risk Level: {risk_assessment.overall_risk}")
print(f"Sentiment Risk: {risk_assessment.sentiment_risk}")
print(f"News Volume Risk: {risk_assessment.volume_risk}")
print(f"Recommendations: {risk_assessment.recommendations}")
```

## 📈 Analytics Dashboard

### Sentiment Metrics

#### Key Performance Indicators
```python
# Get comprehensive sentiment KPIs
kpis = await get_sentiment_kpis(
    symbol="BTC",
    period="30d"
)

print(f"Average Sentiment: {kpis.avg_sentiment}")
print(f"Sentiment Volatility: {kpis.sentiment_volatility}")
print(f"News Volume: {kpis.daily_news_count}")
print(f"Source Diversity: {kpis.source_diversity}")
print(f"Prediction Accuracy: {kpis.prediction_accuracy}%")
```

#### Performance Tracking
- **Sentiment Accuracy**: How well sentiment predicts price moves
- **Signal Performance**: P&L from news-based signals
- **Response Time**: Speed of sentiment updates
- **Coverage Quality**: Breadth and depth of news coverage

### Historical Analysis

#### Backtesting News Strategies
```python
# Backtest news-based trading strategies
backtest = await backtest_news_strategy(
    strategy_config={
        "entry_sentiment_threshold": 0.75,
        "exit_sentiment_threshold": 0.25,
        "position_size": 0.1,  # 10% of portfolio
        "holding_period_max": "24h"
    },
    symbol="BTC/USDT",
    start_date="2025-01-01",
    end_date="2025-03-01"
)

print(f"Total Return: {backtest.total_return}%")
print(f"Win Rate: {backtest.win_rate}%")
print(f"Sharpe Ratio: {backtest.sharpe_ratio}")
print(f"Max Drawdown: {backtest.max_drawdown}%")
```

## 🔧 Configuration

### API Setup

#### CryptoPanic Configuration
```env
# CryptoPanic API
CRYPTOPANIC_API_KEY=your_api_key
CRYPTOPANIC_BASE_URL=https://cryptopanic.com/api/free/v1/
CRYPTOPANIC_RATE_LIMIT=300  # requests per hour
```

#### Dappier AI Configuration
```env
# Dappier AI
DAPPIER_API_KEY=your_api_key
DAPPIER_BASE_URL=https://api.dappier.com/v1/
DAPPIER_RATE_LIMIT=1000  # requests per hour
```

### Sentiment Analysis Settings

#### Customization Options
```python
# Configure sentiment analysis parameters
await configure_sentiment_analysis(
    sentiment_model="advanced",  # basic, standard, advanced
    confidence_threshold=0.6,
    update_frequency="5m",  # 1m, 5m, 15m, 1h
    languages=["en", "es", "fr"],
    include_social_media=True,
    social_weight=0.3  # Weight of social vs news sentiment
)
```

## 🔐 Best Practices

### Data Quality

#### Source Verification
- **Verified Sources**: Use only reputable news outlets
- **Cross-Validation**: Confirm news across multiple sources
- **Fact-Checking**: Validate major announcements
- **Spam Detection**: Filter out promotional content

#### Sentiment Reliability
- **Confidence Thresholds**: Only act on high-confidence signals
- **Temporal Analysis**: Consider sentiment persistence
- **Context Awareness**: Account for market conditions
- **Bias Detection**: Identify and correct sentiment biases

### Risk Management

#### News-Based Risk Controls
```python
# Implement news-based position sizing
position_size = await calculate_news_position_size(
    base_position=1000,  # Base position size
    sentiment_confidence=0.8,
    news_impact_score=7,
    market_volatility=0.15,
    max_position_multiplier=2.0
)
```

#### Emergency Protocols
- **Major News Stops**: Auto-stop on significant negative news
- **Sentiment Circuit Breakers**: Pause trading on extreme sentiment
- **Manual Override**: Always allow manual intervention
- **Position Limits**: Cap exposure during news events

## 📞 Support

For news and sentiment analysis questions:
- **News Support**: news@cryptomcp.dev
- **AI Analysis**: ai@cryptomcp.dev
- **Technical Help**: support@cryptomcp.dev
- **Data Issues**: data@cryptomcp.dev

---

**⚠️ Disclaimer**: News sentiment analysis is not guaranteed to be accurate. Always verify important information and use sentiment as one factor in your trading decisions.