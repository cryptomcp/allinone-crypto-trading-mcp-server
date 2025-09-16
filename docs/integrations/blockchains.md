# Blockchain Integration Guide

Complete guide for integrating and configuring blockchain networks with the All-in-One Crypto Trading MCP Server.

## 🌐 Supported Blockchain Networks

### EVM-Compatible Networks

#### Ethereum (ETH)
- **Network ID**: 1 (Mainnet), 5 (Goerli Testnet)
- **Native Token**: ETH
- **Block Time**: ~12 seconds
- **Features**: Smart contracts, DeFi, NFTs, ENS
- **Use Cases**: Primary DeFi hub, institutional adoption

#### Polygon (MATIC)
- **Network ID**: 137 (Mainnet), 80001 (Mumbai Testnet)
- **Native Token**: MATIC
- **Block Time**: ~2 seconds
- **Features**: Low fees, fast transactions, Ethereum compatibility
- **Use Cases**: Gaming, DeFi, enterprise applications

#### Arbitrum (ARB)
- **Network ID**: 42161 (One), 421613 (Goerli)
- **Native Token**: ETH
- **Block Time**: ~1 second
- **Features**: Optimistic rollup, low fees, Ethereum security
- **Use Cases**: DeFi scaling, institutional trading

#### Optimism (OP)
- **Network ID**: 10 (Mainnet), 420 (Goerli)
- **Native Token**: ETH
- **Block Time**: ~2 seconds
- **Features**: Optimistic rollup, public goods funding
- **Use Cases**: DeFi, social applications

#### Base (BASE)
- **Network ID**: 8453 (Mainnet), 84531 (Goerli)
- **Native Token**: ETH
- **Block Time**: ~2 seconds
- **Features**: Coinbase L2, enterprise-ready
- **Use Cases**: Institutional DeFi, payments

#### BNB Smart Chain (BSC)
- **Network ID**: 56 (Mainnet), 97 (Testnet)
- **Native Token**: BNB
- **Block Time**: ~3 seconds
- **Features**: High throughput, Binance ecosystem
- **Use Cases**: Trading, yield farming

#### Avalanche (AVAX)
- **Network ID**: 43114 (C-Chain), 43113 (Fuji Testnet)
- **Native Token**: AVAX
- **Block Time**: ~2 seconds
- **Features**: Subnet technology, high performance
- **Use Cases**: Enterprise blockchain, gaming

### Non-EVM Networks

#### Solana (SOL)
- **Network**: Mainnet-beta, Devnet, Testnet
- **Native Token**: SOL
- **Block Time**: ~400ms
- **Features**: High throughput, low fees, parallel processing
- **Use Cases**: DeFi, NFTs, high-frequency applications

## 🔧 Network Configuration

### Ethereum Configuration

#### Basic Setup
```env
# Ethereum Mainnet
ETH_ENABLED=true
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETH_RPC_URL_BACKUP=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETH_CHAIN_ID=1
ETH_NETWORK_NAME=mainnet

# Private Key Management
ETH_PRIVATE_KEY=your_ethereum_private_key
ETH_WALLET_ADDRESS=0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C

# Gas Configuration
ETH_GAS_STRATEGY=medium             # slow, medium, fast, aggressive
ETH_MAX_GAS_PRICE=100              # Maximum gas price in gwei
ETH_GAS_MULTIPLIER=1.1             # Gas estimate multiplier
ETH_PRIORITY_FEE=2                 # Priority fee in gwei

# Transaction Settings
ETH_CONFIRMATION_BLOCKS=3          # Required confirmations
ETH_TRANSACTION_TIMEOUT=300        # Transaction timeout in seconds
ETH_NONCE_MANAGEMENT=auto          # auto, manual
ETH_RETRY_ATTEMPTS=3               # Failed transaction retries
```

#### Advanced Configuration
```python
# Advanced Ethereum configuration
eth_config = {
    "rpc_endpoints": {
        "primary": "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
        "backup": ["https://mainnet.infura.io/v3/YOUR_PROJECT_ID"],
        "archive": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ARCHIVE_KEY"
    },
    "gas_optimization": {
        "strategy": "eip1559",         # legacy, eip1559
        "max_fee_per_gas": 100,        # gwei
        "max_priority_fee_per_gas": 2, # gwei
        "gas_limit_buffer": 1.2,       # 20% buffer
        "dynamic_pricing": True
    },
    "transaction_pool": {
        "max_pending": 100,
        "replacement_gas_bump": 1.125,  # 12.5% increase for replacement
        "stuck_transaction_timeout": 600
    },
    "contract_settings": {
        "default_gas_limit": 200000,
        "multicall_enabled": True,
        "batch_size": 10
    }
}

await configure_ethereum_advanced(eth_config)
```

### Polygon Configuration

#### Setup
```env
# Polygon Mainnet
POLYGON_ENABLED=true
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_CHAIN_ID=137
POLYGON_NETWORK_NAME=polygon

# Private Key (can be same as ETH or different)
POLYGON_PRIVATE_KEY=your_polygon_private_key
POLYGON_WALLET_ADDRESS=0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C

# Gas Configuration (MATIC)
POLYGON_GAS_STRATEGY=fast          # Polygon is fast and cheap
POLYGON_MAX_GAS_PRICE=500          # Higher limit in gwei (MATIC is cheaper)
POLYGON_GAS_MULTIPLIER=1.2
POLYGON_PRIORITY_FEE=30            # 30 gwei priority fee

# Polygon-specific settings
POLYGON_CONFIRMATION_BLOCKS=5      # More blocks due to faster finality
POLYGON_HEIMDALL_REST_URL=https://heimdall-api.polygon.technology
```

### Arbitrum Configuration

#### Setup
```env
# Arbitrum One
ARBITRUM_ENABLED=true
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ARBITRUM_CHAIN_ID=42161
ARBITRUM_NETWORK_NAME=arbitrum-one

# Arbitrum uses ETH
ARBITRUM_PRIVATE_KEY=your_arbitrum_private_key
ARBITRUM_WALLET_ADDRESS=0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C

# Gas Configuration (very low fees)
ARBITRUM_GAS_STRATEGY=medium
ARBITRUM_MAX_GAS_PRICE=10          # Much lower than mainnet
ARBITRUM_GAS_MULTIPLIER=1.1
ARBITRUM_PRIORITY_FEE=0.01         # Very small priority fee

# Arbitrum-specific
ARBITRUM_CONFIRMATION_BLOCKS=1     # Fast finality
ARBITRUM_SEQUENCER_FEED=https://arb1.arbitrum.io/rpc
```

### Solana Configuration

#### Setup
```env
# Solana Mainnet
SOLANA_ENABLED=true
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_RPC_URL_BACKUP=https://solana-api.projectserum.com
SOLANA_NETWORK=mainnet-beta

# Private Key Management
SOLANA_PRIVATE_KEY=your_solana_private_key_base58
SOLANA_WALLET_ADDRESS=9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM

# Transaction Settings
SOLANA_COMMITMENT=confirmed        # processed, confirmed, finalized
SOLANA_SKIP_PREFLIGHT=false       # Skip transaction simulation
SOLANA_MAX_RETRIES=3              # Transaction retry attempts
SOLANA_RECENT_BLOCKHASH_CACHE=150  # Cache size for blockhashes

# Fee Configuration
SOLANA_PRIORITY_FEE=5000          # Microlamports priority fee
SOLANA_COMPUTE_UNIT_LIMIT=200000  # Compute unit limit
SOLANA_COMPUTE_UNIT_PRICE=1       # Microlamports per compute unit
```

#### Advanced Solana Configuration
```python
# Advanced Solana configuration
solana_config = {
    "rpc_endpoints": {
        "primary": "https://api.mainnet-beta.solana.com",
        "backup": [
            "https://solana-api.projectserum.com",
            "https://api.rpcpool.com"
        ],
        "websocket": "wss://api.mainnet-beta.solana.com"
    },
    "transaction_settings": {
        "commitment": "confirmed",
        "encoding": "base64",
        "max_supported_transaction_version": 0,
        "skip_preflight": False
    },
    "fee_settings": {
        "priority_fee_strategy": "dynamic",  # fixed, dynamic
        "base_priority_fee": 5000,
        "max_priority_fee": 50000,
        "compute_unit_limit": 200000
    },
    "program_settings": {
        "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "associated_token_program": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
        "system_program": "11111111111111111111111111111112"
    }
}

await configure_solana_advanced(solana_config)
```

## 🔗 RPC Provider Setup

### Alchemy Configuration

#### Multi-Chain Setup
```env
# Alchemy API Keys (recommended provider)
ALCHEMY_API_KEY=your_alchemy_api_key

# Ethereum
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}
ETH_WS_URL=wss://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}

# Polygon
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}
POLYGON_WS_URL=wss://polygon-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}

# Arbitrum
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}
ARBITRUM_WS_URL=wss://arb-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}

# Optimism
OPTIMISM_RPC_URL=https://opt-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}
OPTIMISM_WS_URL=wss://opt-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}

# Base
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}
BASE_WS_URL=wss://base-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}
```

### Infura Configuration

#### Backup Provider Setup
```env
# Infura Project ID (backup provider)
INFURA_PROJECT_ID=your_infura_project_id
INFURA_SECRET=your_infura_secret

# Backup RPC URLs
ETH_RPC_URL_BACKUP=https://mainnet.infura.io/v3/${INFURA_PROJECT_ID}
POLYGON_RPC_URL_BACKUP=https://polygon-mainnet.infura.io/v3/${INFURA_PROJECT_ID}
ARBITRUM_RPC_URL_BACKUP=https://arbitrum-mainnet.infura.io/v3/${INFURA_PROJECT_ID}
OPTIMISM_RPC_URL_BACKUP=https://optimism-mainnet.infura.io/v3/${INFURA_PROJECT_ID}
```

### Public RPC Endpoints

#### Free Alternatives
```env
# Public RPC endpoints (for development/testing)
# Note: These may have rate limits and lower reliability

# Ethereum
ETH_RPC_PUBLIC=https://cloudflare-eth.com
ETH_RPC_PUBLIC_2=https://ethereum.publicnode.com

# Polygon
POLYGON_RPC_PUBLIC=https://polygon-rpc.com
POLYGON_RPC_PUBLIC_2=https://rpc-mainnet.matic.network

# Arbitrum
ARBITRUM_RPC_PUBLIC=https://arb1.arbitrum.io/rpc
ARBITRUM_RPC_PUBLIC_2=https://arbitrum.publicnode.com

# Optimism
OPTIMISM_RPC_PUBLIC=https://mainnet.optimism.io
OPTIMISM_RPC_PUBLIC_2=https://optimism.publicnode.com

# Base
BASE_RPC_PUBLIC=https://mainnet.base.org
BASE_RPC_PUBLIC_2=https://base.publicnode.com

# BSC
BSC_RPC_PUBLIC=https://bsc-dataseed.binance.org/
BSC_RPC_PUBLIC_2=https://rpc.ankr.com/bsc

# Avalanche
AVALANCHE_RPC_PUBLIC=https://api.avax.network/ext/bc/C/rpc
AVALANCHE_RPC_PUBLIC_2=https://rpc.ankr.com/avalanche
```

## 🔐 Wallet Management

### Private Key Security

#### Secure Key Storage
```python
# Secure private key management
from cryptography.fernet import Fernet
import os

class SecureWalletManager:
    def __init__(self):
        self.encryption_key = os.getenv('WALLET_ENCRYPTION_KEY')
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_private_key(self, private_key: str) -> str:
        """Encrypt private key for storage"""
        return self.cipher.encrypt(private_key.encode()).decode()
    
    def decrypt_private_key(self, encrypted_key: str) -> str:
        """Decrypt private key for use"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def store_wallet(self, network: str, private_key: str):
        """Securely store wallet private key"""
        encrypted_key = self.encrypt_private_key(private_key)
        # Store in secure database or key management service
        
    async def get_wallet(self, network: str):
        """Retrieve and decrypt wallet for use"""
        # Retrieve from secure storage
        # Decrypt and return wallet instance
        pass

wallet_manager = SecureWalletManager()
```

### Multi-Signature Wallets

#### Multi-Sig Setup
```python
# Configure multi-signature wallets for enhanced security
multisig_config = {
    "ethereum": {
        "factory_address": "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2",  # Gnosis Safe
        "owners": [
            "0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
            "0x8ba1f109551bD432803012645Hac136c776cc7A90",
            "0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db"
        ],
        "threshold": 2,  # 2 of 3 signatures required
        "daily_limit": 10,  # 10 ETH daily limit for single signatures
    },
    "polygon": {
        "factory_address": "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2",
        "owners": [
            "0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
            "0x8ba1f109551bD432803012645Hac136c776cc7A90"
        ],
        "threshold": 2,  # 2 of 2 for enhanced security
        "daily_limit": 50000,  # 50,000 MATIC daily limit
    }
}

await setup_multisig_wallets(multisig_config)
```

### Hardware Wallet Integration

#### Ledger/Trezor Support
```python
# Hardware wallet integration
hardware_wallet_config = {
    "enabled": True,
    "preferred_provider": "ledger",  # ledger, trezor
    "derivation_paths": {
        "ethereum": "m/44'/60'/0'/0/0",
        "bitcoin": "m/44'/0'/0'/0/0"
    },
    "auto_approval_limit": 1000,  # Auto-approve transactions under $1000
    "confirmation_timeout": 60,   # 60 seconds to confirm on device
    "pin_caching_duration": 900   # 15 minutes PIN cache
}

await configure_hardware_wallets(hardware_wallet_config)
```

## 🛠️ Smart Contract Integration

### Contract Deployment

#### Automated Deployment
```python
# Smart contract deployment configuration
deployment_config = {
    "compiler_version": "0.8.19",
    "optimization": {
        "enabled": True,
        "runs": 200
    },
    "deployment_networks": ["ethereum", "polygon", "arbitrum"],
    "verification": {
        "auto_verify": True,
        "etherscan_api_keys": {
            "ethereum": "your_etherscan_api_key",
            "polygon": "your_polygonscan_api_key",
            "arbitrum": "your_arbiscan_api_key"
        }
    },
    "proxy_pattern": "transparent",  # transparent, uups, beacon
    "access_control": "ownable"      # ownable, roles, multisig
}

await configure_contract_deployment(deployment_config)
```

### Contract Interaction

#### ABI Management
```python
# Contract ABI and interaction setup
contract_config = {
    "uniswap_v3": {
        "networks": {
            "ethereum": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "polygon": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "arbitrum": "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        },
        "abi_source": "etherscan",
        "version": "1.0.0"
    },
    "erc20": {
        "standard_abi": True,
        "common_functions": [
            "balanceOf", "transfer", "transferFrom",
            "approve", "allowance", "decimals", "symbol"
        ]
    },
    "custom_contracts": {
        "trading_vault": {
            "networks": {
                "ethereum": "0x1234567890123456789012345678901234567890"
            },
            "abi_file": "./contracts/TradingVault.json"
        }
    }
}

await configure_contract_integration(contract_config)
```

## 📊 Network Monitoring

### Health Monitoring

#### Network Status Tracking
```python
# Network health monitoring
monitoring_config = {
    "health_checks": {
        "interval": 30,  # Check every 30 seconds
        "timeout": 10,   # 10 second timeout
        "retry_attempts": 3,
        "failure_threshold": 5  # 5 consecutive failures = unhealthy
    },
    "metrics": [
        "block_height",
        "gas_price",
        "peer_count",
        "sync_status",
        "response_time"
    ],
    "alerts": {
        "high_gas_price": 100,      # Alert if gas > 100 gwei
        "slow_response": 5000,       # Alert if response > 5s
        "sync_lag": 10,             # Alert if > 10 blocks behind
        "rpc_failure_rate": 0.1     # Alert if > 10% failure rate
    }
}

await setup_network_monitoring(monitoring_config)
```

### Performance Optimization

#### Connection Optimization
```python
# Network performance optimization
performance_config = {
    "connection_pooling": {
        "max_connections": 50,
        "connection_timeout": 30,
        "read_timeout": 60,
        "pool_timeout": 10
    },
    "request_optimization": {
        "batch_requests": True,
        "max_batch_size": 100,
        "parallel_requests": 10,
        "retry_policy": {
            "max_retries": 3,
            "backoff_factor": 2,
            "backoff_max": 30
        }
    },
    "caching": {
        "block_cache_size": 1000,
        "transaction_cache_ttl": 300,
        "balance_cache_ttl": 60,
        "contract_cache_ttl": 3600
    }
}

await optimize_network_performance(performance_config)
```

## 🔄 Cross-Chain Operations

### Bridge Integration

#### Cross-Chain Bridges
```python
# Configure cross-chain bridge integrations
bridge_config = {
    "wormhole": {
        "enabled": True,
        "networks": ["ethereum", "polygon", "arbitrum", "solana"],
        "guardian_rpc": "https://wormhole-v2-mainnet-api.certus.one",
        "contract_addresses": {
            "ethereum": "0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",
            "polygon": "0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7",
            "solana": "worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth"
        }
    },
    "debridge": {
        "enabled": True,
        "networks": ["ethereum", "polygon", "arbitrum", "avalanche"],
        "api_endpoint": "https://api.debridge.finance/v1.0",
        "contract_addresses": {
            "ethereum": "0x43dE2d77BF8027e25dBD179B491e8d64f38398aA",
            "polygon": "0x43dE2d77BF8027e25dBD179B491e8d64f38398aA"
        }
    },
    "stargate": {
        "enabled": True,
        "networks": ["ethereum", "polygon", "arbitrum", "optimism", "avalanche"],
        "router_addresses": {
            "ethereum": "0x8731d54E9D02c286767d56ac03e8037C07e01e98",
            "polygon": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd"
        }
    }
}

await configure_bridge_integrations(bridge_config)
```

### Asset Bridging

#### Automated Bridging
```python
# Set up automated cross-chain asset bridging
bridging_strategy = {
    "auto_bridging": {
        "enabled": True,
        "trigger_conditions": {
            "gas_price_difference": 50,    # Bridge if gas 50+ gwei cheaper
            "yield_difference": 5,         # Bridge for 5%+ better yield
            "liquidity_requirement": True  # Bridge for better liquidity
        },
        "max_bridge_amount": 100000,       # Max $100k per bridge
        "min_bridge_amount": 1000,         # Min $1k per bridge
        "preferred_bridges": ["wormhole", "stargate", "debridge"]
    },
    "cost_optimization": {
        "calculate_total_cost": True,      # Include gas + bridge fees
        "wait_for_low_gas": True,         # Wait for lower gas if not urgent
        "batch_small_transfers": True,     # Batch small transfers
        "route_optimization": True         # Find cheapest route
    }
}

await setup_automated_bridging(bridging_strategy)
```

## 🧪 Testing and Validation

### Testnet Configuration

#### Multi-Network Testing
```env
# Testnet configurations for safe testing
# Ethereum Goerli
ETH_TESTNET_ENABLED=true
ETH_TESTNET_RPC_URL=https://eth-goerli.g.alchemy.com/v2/YOUR_API_KEY
ETH_TESTNET_CHAIN_ID=5
ETH_TESTNET_PRIVATE_KEY=your_testnet_private_key

# Polygon Mumbai
POLYGON_TESTNET_ENABLED=true
POLYGON_TESTNET_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_TESTNET_CHAIN_ID=80001

# Arbitrum Goerli
ARBITRUM_TESTNET_ENABLED=true
ARBITRUM_TESTNET_RPC_URL=https://arb-goerli.g.alchemy.com/v2/YOUR_API_KEY
ARBITRUM_TESTNET_CHAIN_ID=421613

# Solana Devnet
SOLANA_TESTNET_ENABLED=true
SOLANA_TESTNET_RPC_URL=https://api.devnet.solana.com
SOLANA_TESTNET_NETWORK=devnet
```

### Integration Testing

#### Comprehensive Testing Suite
```python
# Blockchain integration testing
async def test_blockchain_integrations():
    test_suites = {
        "connectivity": test_network_connectivity,
        "wallet_operations": test_wallet_operations,
        "token_transfers": test_token_transfers,
        "contract_interactions": test_contract_interactions,
        "cross_chain": test_cross_chain_operations,
        "gas_estimation": test_gas_estimation,
        "transaction_monitoring": test_transaction_monitoring
    }
    
    results = {}
    for test_name, test_func in test_suites.items():
        try:
            result = await test_func()
            results[test_name] = {
                "success": True,
                "details": result
            }
        except Exception as e:
            results[test_name] = {
                "success": False,
                "error": str(e)
            }
    
    return results

# Run comprehensive tests
test_results = await test_blockchain_integrations()
```

## 📞 Support

For blockchain integration support:
- **Blockchain Setup**: blockchain@cryptomcp.dev
- **Network Issues**: networks@cryptomcp.dev
- **Smart Contracts**: contracts@cryptomcp.dev
- **Cross-Chain**: bridges@cryptomcp.dev

### Network-Specific Support
- **Ethereum**: ethereum@cryptomcp.dev
- **Polygon**: polygon@cryptomcp.dev
- **Arbitrum**: arbitrum@cryptomcp.dev
- **Solana**: solana@cryptomcp.dev
- **Multi-Chain**: multichain@cryptomcp.dev

---

**⚠️ Security Best Practices:**
- Always test on testnets first
- Use hardware wallets for large amounts
- Implement multi-signature for institutional use
- Regular security audits for smart contracts
- Monitor network health continuously
- Keep private keys encrypted and secure
- Use reputable RPC providers with backups