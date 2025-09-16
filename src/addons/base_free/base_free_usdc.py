"""
Free USDC transfer service on Base network using MPC wallets.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx

from core.types import Blockchain, Transaction
from core.exceptions import BlockchainError
from core.utils import retry_with_backoff, validate_address
from env import config

logger = logging.getLogger(__name__)


class BaseFreeUSDC:
    """Free USDC transfer service on Base network."""
    
    def __init__(self):
        self.base_url = config.FREE_USDC_MCP_URL
        self.usdc_contract = config.BASE_USDC_CONTRACT
        self.client = httpx.AsyncClient(timeout=60.0)
    
    @retry_with_backoff(max_retries=3)
    async def transfer_free_usdc(
        self,
        to_address: str,
        amount: Decimal,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Transfer USDC on Base network with free gas.
        
        Args:
            to_address: Recipient address
            amount: USDC amount to transfer
            dry_run: Whether to simulate the transfer
        
        Returns:
            Transfer result
        """
        try:
            # Validate recipient address
            if not validate_address(to_address, "ethereum"):
                raise BlockchainError(f"Invalid Base address: {to_address}")
            
            # Check minimum/maximum limits
            if amount < Decimal('1'):
                raise BlockchainError("Minimum transfer amount is 1 USDC")
            
            if amount > Decimal('10000'):
                raise BlockchainError("Maximum transfer amount is 10,000 USDC")
            
            # Check transfer eligibility
            eligibility = await self.check_transfer_eligibility(to_address, amount)
            if not eligibility['eligible']:
                raise BlockchainError(f"Transfer not eligible: {eligibility['reason']}")
            
            if dry_run:
                return {
                    'success': True,
                    'transaction_hash': f"0x{'0' * 64}",  # Dummy hash
                    'amount': amount,
                    'recipient': to_address,
                    'network': 'base',
                    'gas_cost': Decimal('0'),
                    'simulated': True,
                    'message': 'Free USDC transfer simulation successful'
                }
            
            # Execute real transfer via MCP proxy
            transfer_data = {
                'to_address': to_address,
                'amount': str(amount),
                'token_contract': self.usdc_contract,
                'network': 'base'
            }
            
            response = await self.client.post(
                f"{self.base_url}/transfer",
                json=transfer_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': result.get('success', False),
                'transaction_hash': result.get('transaction_hash'),
                'amount': amount,
                'recipient': to_address,
                'network': 'base',
                'gas_cost': Decimal('0'),  # Free gas
                'simulated': False,
                'message': result.get('message', 'Transfer completed')
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Free USDC transfer request failed: {e}")
            raise BlockchainError(f"Transfer request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Free USDC transfer failed: {e}")
            raise BlockchainError(f"Transfer failed: {str(e)}")
    
    async def check_transfer_eligibility(
        self,
        to_address: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Check if a transfer is eligible for free gas.
        
        Args:
            to_address: Recipient address
            amount: Transfer amount
        
        Returns:
            Eligibility status and details
        """
        try:
            # Basic eligibility checks
            eligibility_checks = []
            
            # Address validation
            if not validate_address(to_address, "ethereum"):
                return {
                    'eligible': False,
                    'reason': 'Invalid recipient address',
                    'checks': eligibility_checks
                }
            
            eligibility_checks.append({
                'check': 'address_validation',
                'passed': True,
                'details': 'Valid Base network address'
            })
            
            # Amount limits
            if amount < Decimal('1') or amount > Decimal('10000'):
                return {
                    'eligible': False,
                    'reason': 'Amount outside allowed range (1-10,000 USDC)',
                    'checks': eligibility_checks
                }
            
            eligibility_checks.append({
                'check': 'amount_limits',
                'passed': True,
                'details': f'Amount {amount} USDC within limits'
            })
            
            # Check daily limits (simplified)
            daily_limit_check = await self._check_daily_limits(to_address, amount)
            eligibility_checks.append(daily_limit_check)
            
            if not daily_limit_check['passed']:
                return {
                    'eligible': False,
                    'reason': daily_limit_check['details'],
                    'checks': eligibility_checks
                }
            
            # Check MPC wallet balance
            balance_check = await self._check_mpc_balance(amount)
            eligibility_checks.append(balance_check)
            
            if not balance_check['passed']:
                return {
                    'eligible': False,
                    'reason': balance_check['details'],
                    'checks': eligibility_checks
                }
            
            return {
                'eligible': True,
                'reason': 'All eligibility checks passed',
                'checks': eligibility_checks,
                'estimated_gas_savings': Decimal('0.002')  # ~$0.50 in ETH
            }
        
        except Exception as e:
            logger.error(f"Eligibility check failed: {e}")
            return {
                'eligible': False,
                'reason': f'Eligibility check error: {str(e)}',
                'checks': []
            }
    
    async def _check_daily_limits(
        self,
        address: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Check daily transfer limits for address."""
        try:
            # In a real implementation, this would check a database
            # For now, return a simple check
            daily_limit = Decimal('5000')  # $5,000 daily limit
            
            return {
                'check': 'daily_limits',
                'passed': amount <= daily_limit,
                'details': f'Daily limit: {daily_limit} USDC, requested: {amount} USDC'
            }
        
        except Exception as e:
            return {
                'check': 'daily_limits',
                'passed': False,
                'details': f'Daily limit check failed: {str(e)}'
            }
    
    async def _check_mpc_balance(self, amount: Decimal) -> Dict[str, Any]:
        """Check MPC wallet has sufficient USDC balance."""
        try:
            # Query MPC wallet balance
            balance = await self.get_mpc_wallet_balance()
            
            if balance >= amount:
                return {
                    'check': 'mpc_balance',
                    'passed': True,
                    'details': f'MPC wallet balance: {balance} USDC, required: {amount} USDC'
                }
            else:
                return {
                    'check': 'mpc_balance',
                    'passed': False,
                    'details': f'Insufficient MPC wallet balance: {balance} USDC, required: {amount} USDC'
                }
        
        except Exception as e:
            return {
                'check': 'mpc_balance',
                'passed': False,
                'details': f'Balance check failed: {str(e)}'
            }
    
    async def get_mpc_wallet_balance(self) -> Decimal:
        """Get current MPC wallet USDC balance."""
        try:
            response = await self.client.get(f"{self.base_url}/balance")
            response.raise_for_status()
            
            data = response.json()
            return Decimal(str(data.get('usdc_balance', '0')))
        
        except Exception as e:
            logger.error(f"Failed to get MPC wallet balance: {e}")
            return Decimal('0')
    
    async def estimate_transfer_cost(self, amount: Decimal) -> Dict[str, Any]:
        """Estimate the cost savings of using free transfer."""
        try:
            # Typical Base network gas costs
            typical_gas_cost = Decimal('0.002')  # ~$0.50
            
            return {
                'amount': amount,
                'typical_gas_cost_eth': typical_gas_cost,
                'typical_gas_cost_usd': typical_gas_cost * Decimal('2500'),  # Rough ETH price
                'free_transfer_savings': typical_gas_cost,
                'percentage_saved': '100%',
                'network': 'base'
            }
        
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return {
                'amount': amount,
                'error': str(e)
            }
    
    async def get_transfer_history(
        self,
        address: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get transfer history for an address or all transfers."""
        try:
            params = {'limit': limit}
            if address:
                params['address'] = address
            
            response = await self.client.get(
                f"{self.base_url}/history",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('transfers', [])
        
        except Exception as e:
            logger.error(f"Failed to get transfer history: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_base_free_usdc = BaseFreeUSDC()


async def transfer_free_usdc(
    to_address: str,
    amount: Decimal,
    dry_run: bool = True
) -> Dict[str, Any]:
    """Transfer USDC on Base with free gas."""
    return await _base_free_usdc.transfer_free_usdc(to_address, amount, dry_run)


async def check_transfer_eligibility(
    to_address: str,
    amount: Decimal
) -> Dict[str, Any]:
    """Check transfer eligibility."""
    return await _base_free_usdc.check_transfer_eligibility(to_address, amount)


async def get_mpc_wallet_balance() -> Decimal:
    """Get MPC wallet USDC balance."""
    return await _base_free_usdc.get_mpc_wallet_balance()


async def estimate_transfer_cost(amount: Decimal) -> Dict[str, Any]:
    """Estimate transfer cost savings."""
    return await _base_free_usdc.estimate_transfer_cost(amount)