"""
Whale transaction tracking and analysis.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import httpx

from core.types import WhaleTransaction, Blockchain
from core.exceptions import WhaleError
from core.utils import retry_with_backoff, cache_result
from env import config

logger = logging.getLogger(__name__)


class WhaleTracker:
    """Whale transaction tracker using Whale Alert API."""
    
    def __init__(self):
        self.base_url = config.WHALE_ALERT_BASE_URL
        self.api_key = config.WHALE_ALERT_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry_with_backoff(max_retries=3)
    @cache_result(ttl=60)  # Cache for 1 minute
    async def get_transactions(
        self,
        blockchain: Optional[Blockchain] = None,
        min_value_usd: Decimal = Decimal('1000000'),
        limit: int = 50,
        hours_back: int = 24
    ) -> List[WhaleTransaction]:
        """
        Get whale transactions from Whale Alert API.
        
        Args:
            blockchain: Filter by specific blockchain
            min_value_usd: Minimum transaction value in USD
            limit: Maximum number of transactions
            hours_back: Hours to look back
        
        Returns:
            List of whale transactions
        """
        try:
            if not self.api_key:
                raise WhaleError("Whale Alert API key not configured")
            
            # Calculate time range
            start_time = int((datetime.utcnow() - timedelta(hours=hours_back)).timestamp())
            
            params = {
                'api_key': self.api_key,
                'min_value': int(min_value_usd),
                'start': start_time,
                'limit': min(limit, 100)  # API limit
            }
            
            if blockchain:
                # Map blockchain names to Whale Alert format
                blockchain_map = {
                    Blockchain.ETHEREUM: 'ethereum',
                    Blockchain.BITCOIN: 'bitcoin',
                    Blockchain.BSC: 'binance-smart-chain',
                    Blockchain.POLYGON: 'polygon',
                    Blockchain.ARBITRUM: 'arbitrum',
                    Blockchain.OPTIMISM: 'optimism',
                    Blockchain.AVALANCHE: 'avalanche'
                }
                
                if blockchain in blockchain_map:
                    params['blockchain'] = blockchain_map[blockchain]
            
            response = await self.client.get(f"{self.base_url}/transactions", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('result') == 'success':
                raise WhaleError(f"Whale Alert API error: {data.get('message', 'Unknown error')}")
            
            transactions = []
            
            for tx_data in data.get('transactions', []):
                try:
                    transaction = self._parse_transaction(tx_data)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    logger.warning(f"Failed to parse whale transaction: {e}")
                    continue
            
            return transactions
        
        except httpx.HTTPError as e:
            logger.error(f"Whale Alert API request failed: {e}")
            raise WhaleError(f"Failed to fetch whale transactions: {str(e)}")
        except Exception as e:
            logger.error(f"Whale tracking failed: {e}")
            raise WhaleError(f"Whale tracking error: {str(e)}")
    
    def _parse_transaction(self, tx_data: Dict[str, Any]) -> Optional[WhaleTransaction]:
        """Parse whale transaction from API response."""
        try:
            # Map blockchain names
            blockchain_map = {
                'ethereum': Blockchain.ETHEREUM,
                'bitcoin': Blockchain.BITCOIN,
                'binance-smart-chain': Blockchain.BSC,
                'polygon': Blockchain.POLYGON,
                'arbitrum': Blockchain.ARBITRUM,
                'optimism': Blockchain.OPTIMISM,
                'avalanche': Blockchain.AVALANCHE
            }
            
            blockchain_name = tx_data.get('blockchain', '').lower()
            blockchain = blockchain_map.get(blockchain_name)
            
            if not blockchain:
                return None
            
            # Extract transaction details
            transaction = WhaleTransaction(
                transaction_id=tx_data.get('hash', ''),
                blockchain=blockchain,
                from_address=tx_data.get('from', {}).get('address', ''),
                to_address=tx_data.get('to', {}).get('address', ''),
                token_symbol=tx_data.get('symbol', ''),
                amount=Decimal(str(tx_data.get('amount', 0))),
                amount_usd=Decimal(str(tx_data.get('amount_usd', 0))),
                timestamp=datetime.fromtimestamp(tx_data.get('timestamp', 0)),
                transaction_type=tx_data.get('transaction_type', 'transfer')
            )
            
            # Add exchange information if available
            from_owner = tx_data.get('from', {}).get('owner', '')
            to_owner = tx_data.get('to', {}).get('owner', '')
            
            if from_owner or to_owner:
                transaction.exchange = from_owner or to_owner
            
            return transaction
        
        except Exception as e:
            logger.error(f"Failed to parse transaction: {e}")
            return None
    
    @retry_with_backoff(max_retries=3)
    async def get_status(self) -> Dict[str, Any]:
        """Get Whale Alert API status and remaining credits."""
        try:
            if not self.api_key:
                raise WhaleError("Whale Alert API key not configured")
            
            params = {'api_key': self.api_key}
            response = await self.client.get(f"{self.base_url}/status", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'status': data.get('result', 'unknown'),
                'requests_left': data.get('requests_left', 0),
                'requests_limit': data.get('requests_limit', 0),
                'reset_time': datetime.fromtimestamp(data.get('reset_time', 0)) if data.get('reset_time') else None
            }
        
        except Exception as e:
            logger.error(f"Failed to get Whale Alert status: {e}")
            raise WhaleError(f"Status check failed: {str(e)}")
    
    async def analyze_patterns(
        self,
        transactions: List[WhaleTransaction],
        timeframe_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze patterns in whale transactions.
        
        Args:
            transactions: List of whale transactions
            timeframe_hours: Timeframe for analysis
        
        Returns:
            Pattern analysis results
        """
        try:
            if not transactions:
                return {
                    'total_transactions': 0,
                    'total_value_usd': Decimal('0'),
                    'analysis': 'No transactions to analyze'
                }
            
            # Basic statistics
            total_value = sum(tx.amount_usd for tx in transactions)
            avg_value = total_value / len(transactions)
            
            # Analyze by blockchain
            blockchain_stats = {}
            for tx in transactions:
                blockchain = tx.blockchain.value
                if blockchain not in blockchain_stats:
                    blockchain_stats[blockchain] = {
                        'count': 0,
                        'total_value': Decimal('0'),
                        'tokens': set()
                    }
                
                blockchain_stats[blockchain]['count'] += 1
                blockchain_stats[blockchain]['total_value'] += tx.amount_usd
                blockchain_stats[blockchain]['tokens'].add(tx.token_symbol)
            
            # Convert sets to lists for JSON serialization
            for stats in blockchain_stats.values():
                stats['tokens'] = list(stats['tokens'])
            
            # Analyze transaction types
            type_stats = {}
            for tx in transactions:
                tx_type = tx.transaction_type
                if tx_type not in type_stats:
                    type_stats[tx_type] = {'count': 0, 'total_value': Decimal('0')}
                
                type_stats[tx_type]['count'] += 1
                type_stats[tx_type]['total_value'] += tx.amount_usd
            
            # Find top tokens by transaction value
            token_stats = {}
            for tx in transactions:
                token = tx.token_symbol
                if token not in token_stats:
                    token_stats[token] = {'count': 0, 'total_value': Decimal('0')}
                
                token_stats[token]['count'] += 1
                token_stats[token]['total_value'] += tx.amount_usd
            
            # Sort tokens by value
            top_tokens = sorted(
                token_stats.items(),
                key=lambda x: x[1]['total_value'],
                reverse=True
            )[:10]
            
            # Generate insights
            insights = []
            
            if len(transactions) > 10:
                insights.append(f"High whale activity detected: {len(transactions)} large transactions")
            
            if total_value > Decimal('100000000'):  # $100M
                insights.append(f"Significant capital movement: ${total_value:,.0f} in whale transactions")
            
            most_active_blockchain = max(blockchain_stats.keys(), key=lambda x: blockchain_stats[x]['count'])
            insights.append(f"Most active blockchain: {most_active_blockchain}")
            
            if top_tokens:
                top_token = top_tokens[0]
                insights.append(f"Top token by value: {top_token[0]} (${top_token[1]['total_value']:,.0f})")
            
            return {
                'total_transactions': len(transactions),
                'total_value_usd': total_value,
                'average_value_usd': avg_value,
                'blockchain_distribution': blockchain_stats,
                'transaction_types': type_stats,
                'top_tokens': dict(top_tokens),
                'insights': insights,
                'timeframe_hours': timeframe_hours,
                'analysis_timestamp': datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze whale patterns: {e}")
            raise WhaleError(f"Pattern analysis failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global tracker instance
_whale_tracker = WhaleTracker()


async def get_whale_transactions(
    blockchain: Optional[Blockchain] = None,
    min_value_usd: Decimal = Decimal('1000000'),
    limit: int = 50,
    hours_back: int = 24
) -> List[WhaleTransaction]:
    """Get whale transactions."""
    return await _whale_tracker.get_transactions(blockchain, min_value_usd, limit, hours_back)


async def get_recent_whale_transactions(limit: int = 20) -> List[WhaleTransaction]:
    """Get recent whale transactions with default settings."""
    return await _whale_tracker.get_transactions(
        min_value_usd=config.WHALE_THRESHOLD_USD,
        limit=limit,
        hours_back=1
    )


async def analyze_whale_patterns(
    blockchain: Optional[Blockchain] = None,
    hours_back: int = 24
) -> Dict[str, Any]:
    """Analyze whale transaction patterns."""
    transactions = await get_whale_transactions(blockchain=blockchain, hours_back=hours_back, limit=100)
    return await _whale_tracker.analyze_patterns(transactions, hours_back)


async def get_whale_alerts() -> Dict[str, Any]:
    """Get whale alert summary and status."""
    try:
        status = await _whale_tracker.get_status()
        recent_transactions = await get_recent_whale_transactions(10)
        
        return {
            'api_status': status,
            'recent_transactions': [tx.dict() for tx in recent_transactions],
            'alert_count': len(recent_transactions),
            'timestamp': datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to get whale alerts: {e}")
        raise WhaleError(f"Whale alerts failed: {str(e)}")