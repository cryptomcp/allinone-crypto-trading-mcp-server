"""
AI-powered trading signal generation.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.types import Signal, SignalType, Blockchain
from core.exceptions import SignalError
from core.utils import cache_result
from cex.market_data import get_price_data, calculate_technical_indicators
from addons.news.aggregator import analyze_sentiment
from addons.news.feargreed_tools import get_fear_greed_data
from env import config

logger = logging.getLogger(__name__)


class AISignalGenerator:
    """AI-powered trading signal generator."""
    
    def __init__(self):
        self.confidence_threshold = 0.6
        self.signal_cache = {}
    
    async def generate_signals(
        self,
        symbols: List[str],
        timeframe: str = "1h",
        analysis_type: str = "technical",
        include_sentiment: bool = True
    ) -> List[Signal]:
        """
        Generate trading signals for given symbols.
        
        Args:
            symbols: List of trading symbols
            timeframe: Analysis timeframe
            analysis_type: Type of analysis (technical, fundamental, combined)
            include_sentiment: Include sentiment analysis
        
        Returns:
            List of generated signals
        """
        try:
            signals = []
            
            for symbol in symbols:
                try:
                    signal = await self._generate_signal_for_symbol(
                        symbol, timeframe, analysis_type, include_sentiment
                    )
                    if signal and signal.confidence >= self.confidence_threshold:
                        signals.append(signal)
                except Exception as e:
                    logger.warning(f"Failed to generate signal for {symbol}: {e}")
                    continue
            
            # Sort by confidence
            signals.sort(key=lambda x: x.confidence, reverse=True)
            return signals
        
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            raise SignalError(f"Failed to generate signals: {str(e)}")
    
    async def _generate_signal_for_symbol(
        self,
        symbol: str,
        timeframe: str,
        analysis_type: str,
        include_sentiment: bool
    ) -> Optional[Signal]:
        """Generate signal for a specific symbol."""
        try:
            # Get technical indicators
            tech_indicators = await calculate_technical_indicators(symbol, timeframe)
            price_data = await get_price_data(symbol)
            
            # Calculate technical score
            tech_score = self._calculate_technical_score(tech_indicators, price_data)
            
            # Get sentiment score if requested
            sentiment_score = 0.0
            if include_sentiment:
                sentiment_score = await self._get_sentiment_score(symbol)
            
            # Combine scores
            if analysis_type == "technical":
                final_score = tech_score
            elif analysis_type == "sentiment":
                final_score = sentiment_score
            else:  # combined
                final_score = (tech_score * 0.7) + (sentiment_score * 0.3)
            
            # Determine signal type and confidence
            if final_score > 0.6:
                signal_type = SignalType.BUY if final_score > 0.8 else SignalType.BUY
                confidence = min(final_score, 0.95)
            elif final_score < -0.6:
                signal_type = SignalType.SELL if final_score < -0.8 else SignalType.SELL
                confidence = min(abs(final_score), 0.95)
            else:
                signal_type = SignalType.HOLD
                confidence = 0.5
            
            # Calculate price targets
            current_price = price_data['price']
            price_target, stop_loss, take_profit = self._calculate_price_targets(
                current_price, signal_type, tech_indicators
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                tech_indicators, sentiment_score, final_score, signal_type
            )
            
            return Signal(
                id=f"{symbol}_{timeframe}_{datetime.utcnow().timestamp()}",
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                price_target=price_target,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timeframe=timeframe,
                reasoning=reasoning,
                sources=['technical_analysis', 'sentiment_analysis'] if include_sentiment else ['technical_analysis'],
                expires_at=datetime.utcnow() + timedelta(hours=4)
            )
        
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {e}")
            return None
    
    def _calculate_technical_score(
        self, 
        indicators: Dict[str, Any], 
        price_data: Dict[str, Any]
    ) -> float:
        """Calculate technical analysis score (-1 to 1)."""
        try:
            score = 0.0
            factors = 0
            
            current_price = float(price_data['price'])
            
            # RSI analysis
            rsi = float(indicators.get('rsi', 50))
            if rsi < 30:  # Oversold
                score += 0.3
            elif rsi > 70:  # Overbought
                score -= 0.3
            elif 40 <= rsi <= 60:  # Neutral
                score += 0.1
            factors += 1
            
            # Moving average analysis
            sma = float(indicators.get('sma', current_price))
            if current_price > sma * 1.02:  # Above SMA
                score += 0.2
            elif current_price < sma * 0.98:  # Below SMA
                score -= 0.2
            factors += 1
            
            # Bollinger Bands analysis
            bb_upper = float(indicators.get('bollinger_upper', current_price))
            bb_lower = float(indicators.get('bollinger_lower', current_price))
            
            if current_price < bb_lower:  # Below lower band
                score += 0.25
            elif current_price > bb_upper:  # Above upper band
                score -= 0.25
            factors += 1
            
            # Support/Resistance analysis
            support = float(indicators.get('support', current_price * 0.95))
            resistance = float(indicators.get('resistance', current_price * 1.05))
            
            if current_price <= support * 1.01:  # Near support
                score += 0.2
            elif current_price >= resistance * 0.99:  # Near resistance
                score -= 0.2
            factors += 1
            
            # Price momentum (24h change)
            change_24h = float(price_data.get('change_24h_percent', 0))
            if change_24h > 5:
                score += 0.15
            elif change_24h < -5:
                score -= 0.15
            factors += 1
            
            return score / factors if factors > 0 else 0.0
        
        except Exception as e:
            logger.error(f"Technical score calculation failed: {e}")
            return 0.0
    
    async def _get_sentiment_score(self, symbol: str) -> float:
        """Get sentiment score for symbol (-1 to 1)."""
        try:
            base_currency = symbol.split('/')[0] if '/' in symbol else symbol
            
            # Get news sentiment
            sentiment_data = await analyze_sentiment(coins=[base_currency])
            
            if sentiment_data['total_articles'] == 0:
                return 0.0
            
            # Calculate sentiment score
            sentiment_dist = sentiment_data['sentiment_percentages']
            positive_pct = sentiment_dist.get('positive', 0) / 100
            negative_pct = sentiment_dist.get('negative', 0) / 100
            
            sentiment_score = positive_pct - negative_pct
            
            # Get Fear & Greed Index
            try:
                fng_data = await get_fear_greed_data()
                fng_value = fng_data['value']
                
                # Normalize F&G to -1 to 1 scale
                fng_score = (fng_value - 50) / 50
                
                # Combine sentiment and F&G
                combined_score = (sentiment_score * 0.7) + (fng_score * 0.3)
                return max(-1.0, min(1.0, combined_score))
            
            except Exception:
                return max(-1.0, min(1.0, sentiment_score))
        
        except Exception as e:
            logger.error(f"Sentiment score calculation failed: {e}")
            return 0.0
    
    def _calculate_price_targets(
        self,
        current_price: Decimal,
        signal_type: SignalType,
        indicators: Dict[str, Any]
    ) -> tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal]]:
        """Calculate price targets based on signal type."""
        try:
            current = float(current_price)
            
            if signal_type == SignalType.BUY:
                # For buy signals
                resistance = float(indicators.get('resistance', current * 1.05))
                support = float(indicators.get('support', current * 0.95))
                
                price_target = Decimal(str(resistance))
                stop_loss = Decimal(str(support))
                take_profit = Decimal(str(current * 1.08))  # 8% profit target
                
            elif signal_type == SignalType.SELL:
                # For sell signals
                resistance = float(indicators.get('resistance', current * 1.05))
                support = float(indicators.get('support', current * 0.95))
                
                price_target = Decimal(str(support))
                stop_loss = Decimal(str(resistance))
                take_profit = Decimal(str(current * 0.92))  # 8% profit target
                
            else:
                # Hold signal
                return None, None, None
            
            return price_target, stop_loss, take_profit
        
        except Exception as e:
            logger.error(f"Price target calculation failed: {e}")
            return None, None, None
    
    def _generate_reasoning(
        self,
        indicators: Dict[str, Any],
        sentiment_score: float,
        final_score: float,
        signal_type: SignalType
    ) -> str:
        """Generate human-readable reasoning for the signal."""
        try:
            reasons = []
            
            # Technical reasons
            rsi = float(indicators.get('rsi', 50))
            if rsi < 30:
                reasons.append("RSI indicates oversold conditions")
            elif rsi > 70:
                reasons.append("RSI indicates overbought conditions")
            
            current_price = float(indicators.get('current_price', 0))
            sma = float(indicators.get('sma', current_price))
            
            if current_price > sma * 1.02:
                reasons.append("Price trading above moving average")
            elif current_price < sma * 0.98:
                reasons.append("Price trading below moving average")
            
            # Sentiment reasons
            if abs(sentiment_score) > 0.3:
                sentiment_desc = "positive" if sentiment_score > 0 else "negative"
                reasons.append(f"Market sentiment is {sentiment_desc}")
            
            # Signal strength
            strength = "strong" if abs(final_score) > 0.8 else "moderate"
            action = signal_type.value.replace('_', ' ')
            
            base_text = f"Generated {strength} {action} signal based on: "
            return base_text + "; ".join(reasons)
        
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            return f"Generated {signal_type.value} signal based on technical and sentiment analysis"


# Global signal generator instance
_signal_generator = AISignalGenerator()


async def generate_signals(
    symbols: List[str],
    timeframe: str = "1h",
    analysis_type: str = "technical",
    include_sentiment: bool = True
) -> List[Signal]:
    """Generate trading signals using AI analysis."""
    return await _signal_generator.generate_signals(
        symbols, timeframe, analysis_type, include_sentiment
    )


@cache_result(ttl=300)  # Cache for 5 minutes
async def get_latest_signals(limit: int = 10) -> List[Signal]:
    """Get latest generated trading signals."""
    try:
        # Common trading pairs
        symbols = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "SOL/USDT",
            "XRP/USDT", "DOT/USDT", "DOGE/USDT", "AVAX/USDT", "MATIC/USDT"
        ]
        
        signals = await generate_signals(symbols[:5])  # Limit to avoid rate limits
        return signals[:limit]
    
    except Exception as e:
        logger.error(f"Failed to get latest signals: {e}")
        return []