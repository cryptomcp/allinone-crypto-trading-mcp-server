"""
EVM blockchain client and multi-chain router.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_utils import to_checksum_address, is_address

from core.types import Blockchain, Transaction, Balance, TokenInfo
from core.exceptions import BlockchainError, ValidationError, NetworkError
from core.utils import retry_with_backoff, validate_address
from env import config

logger = logging.getLogger(__name__)


class EVMClient:
    """EVM blockchain client for interacting with Ethereum-compatible chains."""
    
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.w3: Optional[Web3] = None
        self.account: Optional[Any] = None
        self._chain_config = config.get_chain_config(blockchain.value)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the EVM client."""
        try:
            rpc_url = self._chain_config.get('rpc_url')
            if not rpc_url or 'YOUR_API_KEY' in rpc_url:
                raise BlockchainError(f"Invalid RPC URL for {self.blockchain.value}")
            
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Add POA middleware for chains like BSC
            if self.blockchain in [Blockchain.BSC, Blockchain.POLYGON]:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if not self.w3.is_connected():
                raise NetworkError(f"Failed to connect to {self.blockchain.value} RPC")
            
            # Load account if private key is provided
            private_key = self._chain_config.get('private_key')
            if private_key:
                self.account = Account.from_key(private_key)
            
            self._initialized = True
            logger.info(f"EVM client initialized for {self.blockchain.value}")
        
        except Exception as e:
            logger.error(f"Failed to initialize EVM client: {e}")
            raise BlockchainError(f"EVM client initialization failed: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    async def get_balance(
        self, 
        address: str, 
        token_address: Optional[str] = None,
        block: Union[int, str] = 'latest'
    ) -> Decimal:
        """Get balance for an address."""
        if not self._initialized:
            await self.initialize()
        
        try:
            address = to_checksum_address(address)
            
            if token_address:
                return await self._get_token_balance(address, token_address, block)
            else:
                balance_wei = self.w3.eth.get_balance(address, block)
                return Decimal(self.w3.from_wei(balance_wei, 'ether'))
        
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            raise BlockchainError(f"Failed to get balance: {str(e)}")
    
    async def _get_token_balance(self, address: str, token_address: str, block: Union[int, str] = 'latest') -> Decimal:
        """Get ERC20 token balance."""
        try:
            token_address = to_checksum_address(token_address)
            
            contract = self.w3.eth.contract(
                address=token_address,
                abi=[{
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }, {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }]
            )
            
            balance = contract.functions.balanceOf(address).call(block_identifier=block)
            decimals = contract.functions.decimals().call()
            
            return Decimal(balance) / Decimal(10 ** decimals)
        
        except Exception as e:
            raise BlockchainError(f"Failed to get token balance: {str(e)}")


class MultiChainRouter:
    """Router for managing multiple EVM chains."""
    
    def __init__(self):
        self.clients: Dict[Blockchain, EVMClient] = {}
    
    async def get_client(self, blockchain: Blockchain) -> EVMClient:
        """Get or create an EVM client for the specified blockchain."""
        if blockchain not in self.clients:
            self.clients[blockchain] = EVMClient(blockchain)
            await self.clients[blockchain].initialize()
        return self.clients[blockchain]


# Global router instance
_router = MultiChainRouter()


async def get_evm_client(blockchain: Blockchain) -> EVMClient:
    """Get an EVM client for the specified blockchain."""
    return await _router.get_client(blockchain)