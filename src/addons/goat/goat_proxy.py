"""
GOAT SDK proxy for enhanced EVM operations.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any

import httpx

from core.types import Blockchain
from core.exceptions import NetworkError
from core.utils import retry_with_backoff
from env import config

logger = logging.getLogger(__name__)


class GOATProxy:
    """Proxy for GOAT SDK operations."""
    
    def __init__(self):
        self.base_url = config.GOAT_MCP_URL
        self.enabled = config.GOAT_PROXY_ENABLED
        self.client = httpx.AsyncClient(timeout=60.0)
    
    @retry_with_backoff(max_retries=3)
    async def execute_goat_command(
        self,
        command: str,
        parameters: Dict[str, Any],
        blockchain: Blockchain = Blockchain.ETHEREUM,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a GOAT SDK command.
        
        Args:
            command: GOAT command to execute
            parameters: Command parameters
            blockchain: Target blockchain
            dry_run: Whether to simulate the operation
        
        Returns:
            Command execution result
        """
        try:
            if not self.enabled:
                raise NetworkError("GOAT proxy is disabled")
            
            request_data = {
                'command': command,
                'parameters': parameters,
                'blockchain': blockchain.value,
                'dry_run': dry_run
            }
            
            response = await self.client.post(
                f"{self.base_url}/execute",
                json=request_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': result.get('success', False),
                'data': result.get('data'),
                'message': result.get('message'),
                'command': command,
                'blockchain': blockchain.value,
                'dry_run': dry_run
            }
        
        except httpx.HTTPError as e:
            logger.error(f"GOAT command execution failed: {e}")
            raise NetworkError(f"GOAT proxy request failed: {str(e)}")
        except Exception as e:
            logger.error(f"GOAT command failed: {e}")
            raise NetworkError(f"GOAT command execution failed: {str(e)}")
    
    async def proxy_evm_operation(
        self,
        operation_type: str,
        contract_address: str,
        function_name: str,
        parameters: List[Any],
        blockchain: Blockchain = Blockchain.ETHEREUM,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Proxy EVM contract operation through GOAT.
        
        Args:
            operation_type: Type of operation (read/write)
            contract_address: Contract address
            function_name: Function to call
            parameters: Function parameters
            blockchain: Target blockchain
            dry_run: Whether to simulate
        
        Returns:
            Operation result
        """
        try:
            command_params = {
                'operation_type': operation_type,
                'contract_address': contract_address,
                'function_name': function_name,
                'parameters': parameters
            }
            
            return await self.execute_goat_command(
                'evm_operation',
                command_params,
                blockchain,
                dry_run
            )
        
        except Exception as e:
            logger.error(f"EVM operation proxy failed: {e}")
            raise NetworkError(f"EVM operation failed: {str(e)}")
    
    async def get_goat_capabilities(self) -> Dict[str, Any]:
        """Get available GOAT SDK capabilities."""
        try:
            response = await self.client.get(f"{self.base_url}/capabilities")
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Failed to get GOAT capabilities: {e}")
            return {
                'available': False,
                'error': str(e)
            }
    
    async def get_goat_status(self) -> Dict[str, Any]:
        """Get GOAT proxy status."""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            
            status = response.json()
            
            return {
                'enabled': self.enabled,
                'available': status.get('available', False),
                'version': status.get('version'),
                'supported_chains': status.get('supported_chains', []),
                'features': status.get('features', [])
            }
        
        except Exception as e:
            logger.error(f"Failed to get GOAT status: {e}")
            return {
                'enabled': self.enabled,
                'available': False,
                'error': str(e)
            }
    
    async def send_eth(
        self,
        to_address: str,
        amount: Decimal,
        blockchain: Blockchain = Blockchain.ETHEREUM,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """Send ETH using GOAT proxy."""
        try:
            params = {
                'to_address': to_address,
                'amount': str(amount)
            }
            
            return await self.execute_goat_command(
                'send_eth',
                params,
                blockchain,
                dry_run
            )
        
        except Exception as e:
            logger.error(f"GOAT ETH transfer failed: {e}")
            raise NetworkError(f"ETH transfer failed: {str(e)}")
    
    async def swap_tokens(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal,
        min_amount_out: Optional[Decimal] = None,
        blockchain: Blockchain = Blockchain.ETHEREUM,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """Swap tokens using GOAT proxy."""
        try:
            params = {
                'token_in': token_in,
                'token_out': token_out,
                'amount_in': str(amount_in)
            }
            
            if min_amount_out:
                params['min_amount_out'] = str(min_amount_out)
            
            return await self.execute_goat_command(
                'swap_tokens',
                params,
                blockchain,
                dry_run
            )
        
        except Exception as e:
            logger.error(f"GOAT token swap failed: {e}")
            raise NetworkError(f"Token swap failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global proxy instance
_goat_proxy = GOATProxy()


async def execute_goat_command(
    command: str,
    parameters: Dict[str, Any],
    blockchain: Blockchain = Blockchain.ETHEREUM,
    dry_run: bool = True
) -> Dict[str, Any]:
    """Execute GOAT command."""
    return await _goat_proxy.execute_goat_command(command, parameters, blockchain, dry_run)


async def proxy_evm_operation(
    operation_type: str,
    contract_address: str,
    function_name: str,
    parameters: List[Any],
    blockchain: Blockchain = Blockchain.ETHEREUM,
    dry_run: bool = True
) -> Dict[str, Any]:
    """Proxy EVM operation."""
    return await _goat_proxy.proxy_evm_operation(
        operation_type, contract_address, function_name, parameters, blockchain, dry_run
    )


async def get_goat_capabilities() -> Dict[str, Any]:
    """Get GOAT capabilities."""
    return await _goat_proxy.get_goat_capabilities()


async def get_goat_status() -> Dict[str, Any]:
    """Get GOAT status."""
    return await _goat_proxy.get_goat_status()