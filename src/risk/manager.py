"""
Risk management module for trading operations.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.types import Portfolio, RiskMetrics, Order
from core.exceptions import RiskManagementError
from core.utils import calculate_percentage_change
from env import config

logger = logging.getLogger(__name__)


class RiskManager:
    """Risk management system for trading operations."""
    
    def __init__(self):
        self.daily_losses: Dict[str, Decimal] = {}  # Track daily losses by date
        self.position_limits: Dict[str, Decimal] = {}  # Position limits by symbol
        self.max_correlation = Decimal('0.8')  # Maximum correlation between positions
    
    def check_trade_risk(
        self,
        symbol: str,
        amount: Decimal,
        price: Decimal,
        side: str,
        portfolio: Optional[Portfolio] = None
    ) -> Dict[str, Any]:
        """
        Check if a trade violates risk management rules.
        
        Args:
            symbol: Trading symbol
            amount: Trade amount
            price: Trade price
            side: Trade side (buy/sell)
            portfolio: Current portfolio
        
        Returns:
            Risk check results
        """
        try:
            risks = []
            warnings = []
            
            # Calculate trade value
            trade_value = amount * price
            
            # Check maximum order size
            if trade_value > config.MAX_ORDER_USD:
                risks.append(f"Trade value ${trade_value:,.2f} exceeds maximum order size ${config.MAX_ORDER_USD:,.2f}")
            
            # Check daily loss limits
            today = datetime.utcnow().date().isoformat()
            daily_loss = self.daily_losses.get(today, Decimal('0'))
            
            if daily_loss + trade_value > config.DAILY_LOSS_LIMIT_USD:
                risks.append(f"Trade would exceed daily loss limit: ${daily_loss + trade_value:,.2f} > ${config.DAILY_LOSS_LIMIT_USD:,.2f}")
            
            # Check position concentration if portfolio provided
            if portfolio:
                concentration_risk = self._check_concentration_risk(symbol, trade_value, portfolio)
                if concentration_risk:
                    warnings.extend(concentration_risk)
            
            # Check correlation risk
            correlation_warnings = self._check_correlation_risk(symbol, trade_value, portfolio)
            if correlation_warnings:
                warnings.extend(correlation_warnings)
            
            # Check volatility risk
            volatility_warnings = self._check_volatility_risk(symbol, amount)
            if volatility_warnings:
                warnings.extend(volatility_warnings)
            
            return {
                'approved': len(risks) == 0,
                'risks': risks,
                'warnings': warnings,
                'trade_value': trade_value,
                'risk_score': self._calculate_risk_score(risks, warnings),
                'recommendation': self._get_risk_recommendation(risks, warnings)
            }
        
        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            raise RiskManagementError(f"Risk assessment failed: {str(e)}")
    
    def _check_concentration_risk(
        self, 
        symbol: str, 
        trade_value: Decimal, 
        portfolio: Portfolio
    ) -> List[str]:
        """Check for position concentration risk."""
        warnings = []
        
        if portfolio.total_value_usd > 0:
            # Check if single position would be too large
            concentration = trade_value / portfolio.total_value_usd
            
            if concentration > Decimal('0.3'):  # 30% threshold
                warnings.append(f"High concentration risk: {symbol} would be {concentration*100:.1f}% of portfolio")
            elif concentration > Decimal('0.2'):  # 20% warning
                warnings.append(f"Moderate concentration risk: {symbol} would be {concentration*100:.1f}% of portfolio")
        
        return warnings
    
    def _check_correlation_risk(
        self, 
        symbol: str, 
        trade_value: Decimal, 
        portfolio: Optional[Portfolio]
    ) -> List[str]:
        """Check for correlation risk between positions."""
        warnings = []
        
        # Simplified correlation check - in reality, would need price correlation data
        if portfolio and portfolio.positions:
            related_positions = []
            
            # Simple check for similar assets (e.g., BTC/ETH, stablecoins)
            base_asset = symbol.split('/')[0] if '/' in symbol else symbol
            
            for position in portfolio.positions:
                pos_base = position.symbol.split('/')[0] if '/' in position.symbol else position.symbol
                
                # Check for crypto pairs or similar assets
                if (base_asset in ['BTC', 'ETH'] and pos_base in ['BTC', 'ETH']) or \
                   (base_asset in ['USDT', 'USDC', 'DAI'] and pos_base in ['USDT', 'USDC', 'DAI']):
                    related_positions.append(position.symbol)
            
            if len(related_positions) > 2:
                warnings.append(f"High correlation risk: Multiple related positions {related_positions}")
        
        return warnings
    
    def _check_volatility_risk(self, symbol: str, amount: Decimal) -> List[str]:
        """Check for volatility-based risk."""
        warnings = []
        
        # Simplified volatility check - would need historical price data
        high_volatility_assets = ['DOGE', 'SHIB', 'PEPE', 'MEME']
        
        base_asset = symbol.split('/')[0] if '/' in symbol else symbol
        
        if base_asset.upper() in high_volatility_assets:
            warnings.append(f"High volatility asset: {base_asset} - consider smaller position size")
        
        return warnings
    
    def _calculate_risk_score(self, risks: List[str], warnings: List[str]) -> float:
        """Calculate overall risk score (0-1, higher is riskier)."""
        risk_score = len(risks) * 0.3 + len(warnings) * 0.1
        return min(1.0, risk_score)
    
    def _get_risk_recommendation(self, risks: List[str], warnings: List[str]) -> str:
        """Get risk-based recommendation."""
        if risks:
            return "REJECT - Risk limits violated"
        elif len(warnings) >= 3:
            return "HIGH RISK - Consider reducing position size"
        elif len(warnings) >= 2:
            return "MODERATE RISK - Monitor closely"
        elif warnings:
            return "LOW RISK - Proceed with caution"
        else:
            return "APPROVED - Risk within limits"
    
    def record_trade_outcome(
        self,
        symbol: str,
        trade_value: Decimal,
        pnl: Decimal,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Record trade outcome for risk tracking."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        date_key = timestamp.date().isoformat()
        
        # Track daily losses (only record if it's a loss)
        if pnl < 0:
            if date_key not in self.daily_losses:
                self.daily_losses[date_key] = Decimal('0')
            self.daily_losses[date_key] += abs(pnl)
    
    def get_risk_metrics(self, portfolio: Portfolio) -> RiskMetrics:
        """Calculate comprehensive risk metrics for portfolio."""
        try:
            # Calculate basic metrics
            total_value = portfolio.total_value_usd
            unrealized_pnl = portfolio.unrealized_pnl
            daily_pnl = portfolio.daily_pnl
            
            # Calculate maximum drawdown (simplified)
            max_drawdown = min(Decimal('0'), daily_pnl / total_value * 100) if total_value > 0 else Decimal('0')
            
            # Calculate portfolio concentration
            exposure_by_asset = {}
            for position in portfolio.positions:
                asset = position.symbol.split('/')[0]
                position_value = position.size * position.current_price
                
                if asset not in exposure_by_asset:
                    exposure_by_asset[asset] = Decimal('0')
                exposure_by_asset[asset] += position_value
            
            # Calculate concentration risk
            if total_value > 0:
                concentrations = [exp / total_value for exp in exposure_by_asset.values()]
                concentration_risk = max(concentrations) if concentrations else Decimal('0')
            else:
                concentration_risk = Decimal('0')
            
            # Simplified VaR calculation (5% of portfolio value)
            var_95 = total_value * Decimal('0.05')
            
            # Calculate volatility (simplified)
            volatility = abs(daily_pnl / total_value * 100) if total_value > 0 else Decimal('0')
            
            return RiskMetrics(
                portfolio_value=total_value,
                max_drawdown=max_drawdown,
                var_95=var_95,
                volatility=volatility,
                daily_pnl=daily_pnl,
                exposure_by_asset=exposure_by_asset,
                concentration_risk=concentration_risk,
                liquidity_risk=Decimal('0.1')  # Placeholder
            )
        
        except Exception as e:
            logger.error(f"Risk metrics calculation failed: {e}")
            raise RiskManagementError(f"Risk metrics calculation failed: {str(e)}")
    
    def emergency_stop_check(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Check if emergency stop conditions are met."""
        try:
            metrics = self.get_risk_metrics(portfolio)
            
            emergency_conditions = []
            
            # Check daily loss limit
            if abs(metrics.daily_pnl) > config.DAILY_LOSS_LIMIT_USD:
                emergency_conditions.append(f"Daily loss limit exceeded: ${abs(metrics.daily_pnl):,.2f}")
            
            # Check maximum drawdown
            if metrics.max_drawdown < -20:  # 20% drawdown
                emergency_conditions.append(f"Excessive drawdown: {metrics.max_drawdown:.1f}%")
            
            # Check concentration risk
            if metrics.concentration_risk > Decimal('0.5'):  # 50% in single asset
                emergency_conditions.append(f"Excessive concentration: {metrics.concentration_risk*100:.1f}%")
            
            return {
                'emergency_stop_required': len(emergency_conditions) > 0,
                'conditions': emergency_conditions,
                'metrics': metrics.dict(),
                'timestamp': datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Emergency stop check failed: {e}")
            return {
                'emergency_stop_required': True,
                'conditions': [f"Risk check system error: {str(e)}"],
                'timestamp': datetime.utcnow()
            }


# Global risk manager instance
_risk_manager = RiskManager()


def check_trade_risk(
    symbol: str,
    amount: Decimal,
    price: Decimal,
    side: str,
    portfolio: Optional[Portfolio] = None
) -> Dict[str, Any]:
    """Check trade risk using the global risk manager."""
    return _risk_manager.check_trade_risk(symbol, amount, price, side, portfolio)


def get_portfolio_risk_metrics(portfolio: Portfolio) -> RiskMetrics:
    """Get risk metrics for a portfolio."""
    return _risk_manager.get_risk_metrics(portfolio)


def emergency_stop_check(portfolio: Portfolio) -> Dict[str, Any]:
    """Check emergency stop conditions."""
    return _risk_manager.emergency_stop_check(portfolio)