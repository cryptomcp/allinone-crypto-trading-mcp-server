"""
Portfolio management and tracking functionality.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.types import Portfolio, Balance, Position, RiskMetrics
from core.exceptions import PortfolioError
from core.utils import cache_result
from cex.trading import get_balances as get_cex_balances
from evm.client import get_evm_client, Blockchain
from solana.client import get_solana_client
from cex.market_data import get_price_data
from env import config

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Portfolio management and tracking."""
    
    def __init__(self):
        self.portfolio_cache = {}
        self.price_cache = {}
    
    async def get_portfolio_summary(
        self,
        include_exchanges: bool = True,
        include_wallets: bool = True,
        include_staking: bool = True
    ) -> Portfolio:
        """
        Get comprehensive portfolio summary.
        
        Args:
            include_exchanges: Include exchange balances
            include_wallets: Include wallet balances
            include_staking: Include staking positions
        
        Returns:
            Complete portfolio data
        """
        try:
            all_balances = []
            all_positions = []
            
            # Get exchange balances
            if include_exchanges:
                exchange_balances = await self._get_exchange_balances()
                all_balances.extend(exchange_balances)
            
            # Get wallet balances
            if include_wallets:
                wallet_balances = await self._get_wallet_balances()
                all_balances.extend(wallet_balances)
            
            # Get staking positions
            if include_staking:
                staking_positions = await self._get_staking_positions()
                all_positions.extend(staking_positions)
            
            # Calculate total portfolio value
            total_value_usd = await self._calculate_total_value(all_balances)
            
            # Calculate P&L
            unrealized_pnl, realized_pnl, daily_pnl = await self._calculate_pnl(
                all_balances, all_positions
            )
            
            return Portfolio(
                total_value_usd=total_value_usd,
                balances=all_balances,
                positions=all_positions,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                daily_pnl=daily_pnl
            )
        
        except Exception as e:
            logger.error(f"Portfolio summary failed: {e}")
            raise PortfolioError(f"Failed to get portfolio summary: {str(e)}")
    
    async def _get_exchange_balances(self) -> List[Balance]:
        """Get balances from all configured exchanges."""
        try:
            all_balances = []
            
            # Get balances from CEX
            cex_balances = await get_cex_balances(include_zero=False)
            
            for balance_data in cex_balances:
                balance = Balance(
                    currency=balance_data['currency'],
                    total=Decimal(str(balance_data['total'])),
                    available=Decimal(str(balance_data['available'])),
                    locked=Decimal(str(balance_data.get('locked', 0))),
                    exchange=balance_data.get('exchange')
                )
                all_balances.append(balance)
            
            return all_balances
        
        except Exception as e:
            logger.error(f"Failed to get exchange balances: {e}")
            return []
    
    async def _get_wallet_balances(self) -> List[Balance]:
        """Get balances from blockchain wallets."""
        try:
            all_balances = []
            
            # EVM wallets
            evm_chains = [
                Blockchain.ETHEREUM, Blockchain.POLYGON, Blockchain.ARBITRUM,
                Blockchain.OPTIMISM, Blockchain.BASE, Blockchain.BSC, Blockchain.AVALANCHE
            ]
            
            for blockchain in evm_chains:
                try:
                    chain_config = config.get_chain_config(blockchain.value)
                    private_key = chain_config.get('private_key')
                    
                    if not private_key:
                        continue
                    
                    evm_client = await get_evm_client(blockchain)
                    
                    # Get account address from private key
                    if hasattr(evm_client, 'account') and evm_client.account:
                        address = evm_client.account.address
                        
                        # Get native token balance
                        native_balance = await evm_client.get_balance(address)
                        
                        if native_balance > 0:
                            balance = Balance(
                                currency=self._get_native_currency(blockchain),
                                total=native_balance,
                                available=native_balance,
                                blockchain=blockchain,
                                address=address
                            )
                            all_balances.append(balance)
                
                except Exception as e:
                    logger.warning(f"Failed to get {blockchain.value} balance: {e}")
                    continue
            
            # Solana wallet
            try:
                if config.SOLANA_PRIVATE_KEY:
                    solana_client = await get_solana_client()
                    
                    if hasattr(solana_client, 'keypair') and solana_client.keypair:
                        address = str(solana_client.keypair.pubkey())
                        sol_balance = await solana_client.get_balance(address)
                        
                        if sol_balance > 0:
                            balance = Balance(
                                currency="SOL",
                                total=sol_balance,
                                available=sol_balance,
                                blockchain=Blockchain.SOLANA,
                                address=address
                            )
                            all_balances.append(balance)
            
            except Exception as e:
                logger.warning(f"Failed to get Solana balance: {e}")
            
            return all_balances
        
        except Exception as e:
            logger.error(f"Failed to get wallet balances: {e}")
            return []
    
    async def _get_staking_positions(self) -> List[Position]:
        """Get staking positions."""
        try:
            # This would be implemented with specific staking providers
            # For now, return empty list
            return []
        
        except Exception as e:
            logger.error(f"Failed to get staking positions: {e}")
            return []
    
    async def _calculate_total_value(self, balances: List[Balance]) -> Decimal:
        """Calculate total portfolio value in USD."""
        try:
            total_value = Decimal('0')
            
            for balance in balances:
                if balance.total <= 0:
                    continue
                
                try:
                    # Get price for the currency
                    price_data = await get_price_data(balance.currency, "USD")
                    price = price_data['price']
                    
                    currency_value = balance.total * price
                    total_value += currency_value
                
                except Exception as e:
                    logger.warning(f"Failed to get price for {balance.currency}: {e}")
                    continue
            
            return total_value
        
        except Exception as e:
            logger.error(f"Failed to calculate total value: {e}")
            return Decimal('0')
    
    async def _calculate_pnl(
        self, 
        balances: List[Balance], 
        positions: List[Position]
    ) -> tuple[Decimal, Decimal, Decimal]:
        """Calculate portfolio P&L."""
        try:
            # Simplified P&L calculation
            # In a real implementation, this would track historical data
            
            unrealized_pnl = Decimal('0')
            realized_pnl = Decimal('0')
            daily_pnl = Decimal('0')
            
            # Calculate unrealized P&L from positions
            for position in positions:
                unrealized_pnl += position.unrealized_pnl
                realized_pnl += position.realized_pnl
            
            # Daily P&L would need historical tracking
            # For now, use a placeholder
            daily_pnl = unrealized_pnl * Decimal('0.1')  # Rough estimate
            
            return unrealized_pnl, realized_pnl, daily_pnl
        
        except Exception as e:
            logger.error(f"Failed to calculate P&L: {e}")
            return Decimal('0'), Decimal('0'), Decimal('0')
    
    def _get_native_currency(self, blockchain: Blockchain) -> str:
        """Get native currency symbol for blockchain."""
        currency_map = {
            Blockchain.ETHEREUM: "ETH",
            Blockchain.POLYGON: "MATIC",
            Blockchain.ARBITRUM: "ETH",
            Blockchain.OPTIMISM: "ETH",
            Blockchain.BASE: "ETH",
            Blockchain.BSC: "BNB",
            Blockchain.AVALANCHE: "AVAX",
            Blockchain.SOLANA: "SOL"
        }
        return currency_map.get(blockchain, "ETH")
    
    async def get_asset_allocation(self) -> Dict[str, Any]:
        """Get portfolio asset allocation."""
        try:
            portfolio = await self.get_portfolio_summary()
            
            if portfolio.total_value_usd <= 0:
                return {
                    'total_value': Decimal('0'),
                    'allocation': {},
                    'top_holdings': []
                }
            
            # Calculate allocation by currency
            allocation = {}
            for balance in portfolio.balances:
                if balance.total <= 0:
                    continue
                
                try:
                    price_data = await get_price_data(balance.currency, "USD")
                    value = balance.total * price_data['price']
                    percentage = (value / portfolio.total_value_usd) * 100
                    
                    allocation[balance.currency] = {
                        'amount': balance.total,
                        'value_usd': value,
                        'percentage': percentage,
                        'exchange': balance.exchange,
                        'blockchain': balance.blockchain.value if balance.blockchain else None
                    }
                
                except Exception as e:
                    logger.warning(f"Failed to calculate allocation for {balance.currency}: {e}")
                    continue
            
            # Get top holdings
            top_holdings = sorted(
                allocation.items(),
                key=lambda x: x[1]['value_usd'],
                reverse=True
            )[:10]
            
            return {
                'total_value': portfolio.total_value_usd,
                'allocation': allocation,
                'top_holdings': dict(top_holdings)
            }
        
        except Exception as e:
            logger.error(f"Failed to get asset allocation: {e}")
            raise PortfolioError(f"Asset allocation calculation failed: {str(e)}")


# Global portfolio manager instance
_portfolio_manager = PortfolioManager()


async def get_portfolio_summary(
    include_exchanges: bool = True,
    include_wallets: bool = True,
    include_staking: bool = True
) -> Portfolio:
    """Get portfolio summary."""
    return await _portfolio_manager.get_portfolio_summary(
        include_exchanges, include_wallets, include_staking
    )


async def get_balances(
    exchange: Optional[str] = None,
    currency: Optional[str] = None,
    include_zero: bool = False
) -> List[Balance]:
    """Get portfolio balances with filtering."""
    try:
        portfolio = await get_portfolio_summary()
        balances = portfolio.balances
        
        # Apply filters
        if exchange:
            balances = [b for b in balances if b.exchange and b.exchange.value == exchange]
        
        if currency:
            balances = [b for b in balances if b.currency.upper() == currency.upper()]
        
        if not include_zero:
            balances = [b for b in balances if b.total > 0]
        
        return balances
    
    except Exception as e:
        logger.error(f"Failed to get filtered balances: {e}")
        raise PortfolioError(f"Balance retrieval failed: {str(e)}")


async def get_asset_allocation() -> Dict[str, Any]:
    """Get portfolio asset allocation."""
    return await _portfolio_manager.get_asset_allocation()