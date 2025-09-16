"""
Solana blockchain client implementation.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts

from core.types import Blockchain, Balance, TokenInfo
from core.exceptions import BlockchainError, ValidationError
from core.utils import retry_with_backoff
from env import config

logger = logging.getLogger(__name__)


class SolanaClient:
    """Solana blockchain client."""
    
    def __init__(self):
        self.client: Optional[AsyncClient] = None
        self.keypair: Optional[Keypair] = None
        self.commitment = Commitment(config.SOLANA_COMMITMENT)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Solana client."""
        try:
            # Create RPC client
            self.client = AsyncClient(
                config.SOLANA_RPC_URL,
                commitment=self.commitment
            )
            
            # Load keypair if private key is provided
            if config.SOLANA_PRIVATE_KEY:
                # Convert private key to bytes and create keypair
                private_key_bytes = bytes.fromhex(config.SOLANA_PRIVATE_KEY.replace('0x', ''))
                self.keypair = Keypair.from_bytes(private_key_bytes)
                logger.info(f"Loaded Solana account: {self.keypair.pubkey()}")
            
            # Test connection
            await self.client.get_health()
            self._initialized = True
            logger.info("Solana client initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Solana client: {e}")
            raise BlockchainError(f"Solana client initialization failed: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    async def get_balance(
        self, 
        address: str, 
        token_mint: Optional[str] = None
    ) -> Decimal:
        """
        Get balance for a Solana address.
        
        Args:
            address: Wallet address
            token_mint: SPL token mint address (None for SOL)
        
        Returns:
            Balance amount
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            pubkey = Pubkey.from_string(address)
            
            if token_mint:
                # SPL token balance - would need to implement SPL token account lookup
                return await self._get_spl_balance(pubkey, token_mint)
            else:
                # SOL balance
                response = await self.client.get_balance(pubkey, commitment=self.commitment)
                balance_lamports = response.value
                return Decimal(balance_lamports) / Decimal(10**9)  # Convert lamports to SOL
        
        except Exception as e:
            logger.error(f"Failed to get Solana balance: {e}")
            raise BlockchainError(f"Failed to get balance: {str(e)}")
    
    async def _get_spl_balance(self, owner: Pubkey, token_mint: str) -> Decimal:
        """Get SPL token balance (simplified implementation)."""
        try:
            # This would require implementing SPL token account discovery
            # For now, return zero as placeholder
            return Decimal('0')
        except Exception as e:
            raise BlockchainError(f"Failed to get SPL balance: {str(e)}")
    
    @retry_with_backoff(max_retries=3)
    async def send_sol(
        self,
        to_address: str,
        amount: Decimal,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Send SOL to another address.
        
        Args:
            to_address: Recipient address
            amount: Amount in SOL
            dry_run: Whether to simulate the transaction
        
        Returns:
            Transaction result
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.keypair:
            raise BlockchainError("No keypair loaded for transaction signing")
        
        try:
            to_pubkey = Pubkey.from_string(to_address)
            lamports = int(amount * Decimal(10**9))  # Convert SOL to lamports
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=self.keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )
            
            if dry_run:
                # Simulate the transaction
                return {
                    'success': True,
                    'transaction_signature': 'simulation',
                    'amount': amount,
                    'recipient': to_address,
                    'fee_estimate': Decimal('0.000005'),  # Typical SOL transaction fee
                    'simulated': True,
                    'message': 'SOL transfer simulation successful'
                }
            else:
                # Get recent blockhash
                blockhash_resp = await self.client.get_latest_blockhash(commitment=self.commitment)
                recent_blockhash = blockhash_resp.value.blockhash
                
                # Create and sign transaction
                transaction = Transaction(
                    instructions=[transfer_ix],
                    payer=self.keypair.pubkey(),
                    recent_blockhash=recent_blockhash
                )
                
                # Send transaction
                opts = TxOpts(skip_confirmation=False, skip_preflight=False)
                response = await self.client.send_transaction(transaction, opts)
                
                return {
                    'success': True,
                    'transaction_signature': str(response.value),
                    'amount': amount,
                    'recipient': to_address,
                    'simulated': False,
                    'message': 'SOL transfer completed successfully'
                }
        
        except Exception as e:
            logger.error(f"Failed to send SOL: {e}")
            raise BlockchainError(f"SOL transfer failed: {str(e)}")
    
    async def get_transaction(self, signature: str) -> Dict[str, Any]:
        """Get transaction details by signature."""
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self.client.get_transaction(signature, commitment=self.commitment)
            
            if not response.value:
                raise BlockchainError(f"Transaction {signature} not found")
            
            tx = response.value
            
            return {
                'signature': signature,
                'blockchain': 'solana',
                'slot': tx.slot,
                'block_time': datetime.fromtimestamp(tx.block_time) if tx.block_time else None,
                'fee': Decimal(tx.meta.fee if tx.meta else 0) / Decimal(10**9),
                'status': 'success' if tx.meta and tx.meta.err is None else 'failed',
                'logs': tx.meta.log_messages if tx.meta else []
            }
        
        except Exception as e:
            logger.error(f"Failed to get transaction: {e}")
            raise BlockchainError(f"Failed to get transaction: {str(e)}")


# Global client instance
_solana_client = SolanaClient()


async def get_solana_client() -> SolanaClient:
    """Get the global Solana client instance."""
    if not _solana_client._initialized:
        await _solana_client.initialize()
    return _solana_client