# Blockchain Features

Comprehensive blockchain operations across 8 major networks with advanced DeFi capabilities.

## 🌐 Supported Blockchains

### EVM-Compatible Networks

#### Ethereum (ETH)
- **Network ID**: 1 (Mainnet)
- **Native Token**: ETH
- **Gas Token**: ETH
- **Block Time**: ~12 seconds
- **Features**: Full smart contract support, ENS, NFTs
- **DeFi Ecosystem**: Uniswap, Compound, Aave, MakerDAO

#### Polygon (MATIC)
- **Network ID**: 137
- **Native Token**: MATIC  
- **Gas Token**: MATIC
- **Block Time**: ~2 seconds
- **Features**: Low fees, fast transactions
- **DeFi Ecosystem**: QuickSwap, Aave Polygon, Curve

#### Arbitrum (ARB)
- **Network ID**: 42161
- **Native Token**: ETH
- **Gas Token**: ETH
- **Block Time**: ~1 second
- **Features**: Ethereum L2, optimistic rollups
- **DeFi Ecosystem**: GMX, Camelot, Radiant Capital

#### Optimism (OP)
- **Network ID**: 10
- **Native Token**: ETH
- **Gas Token**: ETH  
- **Block Time**: ~2 seconds
- **Features**: Ethereum L2, optimistic rollups
- **DeFi Ecosystem**: Velodrome, Beethoven X, Kwenta

#### Base (BASE)
- **Network ID**: 8453
- **Native Token**: ETH
- **Gas Token**: ETH
- **Block Time**: ~2 seconds
- **Features**: Coinbase L2, free USDC transfers
- **DeFi Ecosystem**: BaseSwap, Moonwell, Aerodrome

#### BNB Smart Chain (BSC)
- **Network ID**: 56
- **Native Token**: BNB
- **Gas Token**: BNB
- **Block Time**: ~3 seconds
- **Features**: Fast, low-cost transactions
- **DeFi Ecosystem**: PancakeSwap, Venus, Alpaca Finance

#### Avalanche (AVAX)
- **Network ID**: 43114
- **Native Token**: AVAX
- **Gas Token**: AVAX
- **Block Time**: ~2 seconds
- **Features**: High throughput, subnets
- **DeFi Ecosystem**: Trader Joe, Platypus, Benqi

### Non-EVM Networks

#### Solana (SOL)
- **Network**: Mainnet-beta
- **Native Token**: SOL
- **Block Time**: ~400ms
- **Features**: High speed, low fees, parallel processing
- **DeFi Ecosystem**: Jupiter, Raydium, Orca, Mango Markets

## 🔧 Core Operations

### Wallet Management

#### Create New Wallet
```python
# Generate new wallet for any supported blockchain
wallet = await create_wallet(
    blockchain="ethereum",
    save_to_keystore=True,
    password="secure_password"
)

print(f"Address: {wallet.address}")
print(f"Private Key: {wallet.private_key}")  # Keep secure!
```

#### Import Existing Wallet
```python
# Import wallet from private key or mnemonic
wallet = await import_wallet(
    blockchain="solana",
    private_key="your_private_key_here",
    # or use mnemonic
    # mnemonic="your twelve word recovery phrase here"
)
```

#### Multi-Chain Wallet Support
```python
# Generate addresses for all supported chains
addresses = await generate_multi_chain_addresses(
    seed="your_seed_phrase_here"
)

for blockchain, address in addresses.items():
    print(f"{blockchain}: {address}")
```

### Token Operations

#### ERC20 Token Management
```python
# Get ERC20 token balance
balance = await get_token_balance(
    address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    token_address="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",  # USDC
    blockchain="ethereum"
)

# Transfer ERC20 tokens
result = await transfer_tokens(
    token_address="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",
    to_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    amount=100.0,  # 100 USDC
    blockchain="ethereum",
    dry_run=True
)
```

#### ERC721 NFT Operations
```python
# Check NFT ownership
nfts = await get_nft_balance(
    address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    contract_address="0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",  # BAYC
    blockchain="ethereum"
)

# Transfer NFT
await transfer_nft(
    contract_address="0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
    token_id=1234,
    to_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    blockchain="ethereum"
)
```

#### ERC1155 Multi-Token Operations
```python
# Get ERC1155 token balances
balances = await get_erc1155_balances(
    address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    contract_address="0x495f947276749Ce646f68AC8c248420045cb7b5e",  # OpenSea
    token_ids=[1, 2, 3, 4, 5],
    blockchain="ethereum"
)

# Batch transfer ERC1155 tokens
await batch_transfer_erc1155(
    contract_address="0x495f947276749Ce646f68AC8c248420045cb7b5e",
    to_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    token_ids=[1, 2, 3],
    amounts=[10, 5, 1],
    blockchain="ethereum"
)
```

#### SPL Token Operations (Solana)
```python
# Get SPL token balance
balance = await get_spl_token_balance(
    address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    token_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    blockchain="solana"
)

# Transfer SPL tokens
result = await transfer_spl_tokens(
    token_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    to_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    amount=50.0,  # 50 USDC
    blockchain="solana"
)
```

### Smart Contract Interactions

#### Read Contract Data
```python
# Read from smart contract
result = await read_contract(
    contract_address="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",
    function_name="balanceOf",
    parameters=["0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C"],
    blockchain="ethereum"
)

print(f"Balance: {result}")
```

#### Write to Contract
```python
# Execute contract function
result = await write_contract(
    contract_address="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",
    function_name="transfer",
    parameters=[
        "0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",  # to address
        "1000000000000000000"  # 1 token (18 decimals)
    ],
    blockchain="ethereum",
    gas_limit=100000,
    dry_run=True
)
```

#### Deploy New Contract
```python
# Deploy smart contract
deployment = await deploy_contract(
    bytecode="0x608060405234801561001057600080fd5b50...",
    constructor_args=["MyToken", "MTK", 18, 1000000],
    blockchain="polygon",
    gas_limit=2000000
)

print(f"Contract deployed at: {deployment.contract_address}")
print(f"Transaction hash: {deployment.transaction_hash}")
```

## 🌉 Cross-Chain Operations

### Bridge Assets

#### Wormhole Bridge
```python
# Bridge tokens using Wormhole
result = await bridge_tokens(
    from_chain="ethereum",
    to_chain="solana",
    token="USDC",
    amount=1000.0,
    recipient_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    bridge_provider="wormhole",
    dry_run=True
)

print(f"Bridge fee: ${result['bridge_fee']}")
print(f"Estimated time: {result['estimated_time']}")
```

#### deBridge Integration
```python
# Cross-chain swap via deBridge
result = await cross_chain_swap(
    from_chain="ethereum",
    to_chain="polygon",
    from_token="ETH",
    to_token="MATIC",
    amount=1.0,
    recipient_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    bridge_provider="debridge"
)
```

### Multi-Chain Portfolio
```python
# View assets across all chains
multi_chain_portfolio = await get_multi_chain_portfolio(
    address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C"
)

total_value = 0
for chain, assets in multi_chain_portfolio.items():
    chain_value = sum(asset['value_usd'] for asset in assets)
    total_value += chain_value
    print(f"{chain}: ${chain_value:,.2f}")

print(f"Total across all chains: ${total_value:,.2f}")
```

## 🏛️ DeFi Operations

### Decentralized Exchanges

#### Uniswap V3 (Ethereum)
```python
# Swap tokens on Uniswap V3
swap_result = await uniswap_v3_swap(
    token_in="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",  # USDC
    token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    amount_in=1000.0,  # 1000 USDC
    slippage_tolerance=0.5,  # 0.5%
    deadline_minutes=20
)

# Add liquidity to Uniswap V3 pool
liquidity_result = await add_uniswap_v3_liquidity(
    token_a="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",  # USDC
    token_b="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    amount_a=1000.0,
    amount_b=0.5,
    fee_tier=3000,  # 0.3%
    price_range_lower=1800,
    price_range_upper=2200
)
```

#### Jupiter Aggregator (Solana)
```python
# Swap tokens using Jupiter
jupiter_swap = await jupiter_swap(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",  # SOL
    amount=500.0,  # 500 USDC
    slippage_bps=50  # 0.5%
)

print(f"Expected output: {jupiter_swap['output_amount']} SOL")
print(f"Price impact: {jupiter_swap['price_impact_pct']}%")
```

#### PancakeSwap (BSC)
```python
# Trade on PancakeSwap
pancake_swap = await pancakeswap_swap(
    token_in="0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",  # USDC
    token_out="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
    amount_in=200.0,
    slippage_tolerance=1.0,  # 1%
    blockchain="bsc"
)
```

### Lending & Borrowing

#### Aave Protocol
```python
# Supply assets to Aave
supply_result = await aave_supply(
    asset="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",  # USDC
    amount=5000.0,
    blockchain="ethereum",
    enable_as_collateral=True
)

# Borrow from Aave
borrow_result = await aave_borrow(
    asset="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    amount=1.0,
    interest_rate_mode="variable",  # or "stable"
    blockchain="ethereum"
)

# Check health factor
health_factor = await aave_health_factor(
    user_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    blockchain="ethereum"
)
print(f"Health factor: {health_factor}")
```

#### Compound Finance
```python
# Supply to Compound
compound_supply = await compound_supply(
    token="USDC",
    amount=1000.0,
    blockchain="ethereum"
)

# Get APY rates
rates = await compound_get_rates()
for token, rate_info in rates.items():
    print(f"{token} Supply APY: {rate_info['supply_apy']:.2f}%")
    print(f"{token} Borrow APY: {rate_info['borrow_apy']:.2f}%")
```

### Staking Operations

#### Ethereum 2.0 Staking
```python
# Stake ETH for ETH 2.0
staking_result = await stake_eth2(
    amount=32.0,  # 32 ETH for validator
    validator_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    withdrawal_credentials="0x010000000000000000000000742d35cc..."
)

# Check staking rewards
rewards = await get_eth2_rewards(
    validator_index=123456
)
print(f"Total rewards: {rewards['total_rewards']} ETH")
```

#### Solana Staking
```python
# Stake SOL
stake_result = await stake_sol(
    amount=100.0,  # 100 SOL
    validator_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    stake_account_address=None  # Auto-generate
)

# Check staking status
stake_status = await get_sol_stake_status(
    stake_account="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
)
print(f"Active stake: {stake_status['active_stake']} SOL")
print(f"Estimated APY: {stake_status['estimated_apy']:.2f}%")
```

## 🔍 Blockchain Analytics

### Transaction Analysis
```python
# Analyze transaction patterns
tx_analysis = await analyze_transaction_patterns(
    address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    blockchain="ethereum",
    timeframe="30d"
)

print(f"Total transactions: {tx_analysis['total_txs']}")
print(f"Average gas used: {tx_analysis['avg_gas_used']}")
print(f"Total fees paid: {tx_analysis['total_fees']} ETH")
```

### Gas Optimization
```python
# Get gas price recommendations
gas_prices = await get_gas_recommendations(
    blockchain="ethereum",
    priority="fast"  # slow, standard, fast
)

print(f"Recommended gas price: {gas_prices['gas_price']} gwei")
print(f"Estimated confirmation time: {gas_prices['est_time']} minutes")

# Estimate gas for transaction
gas_estimate = await estimate_transaction_gas(
    to_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    data="0xa9059cbb...",  # Transaction data
    blockchain="ethereum"
)
```

### Address Analytics
```python
# Comprehensive address analysis
address_info = await analyze_address(
    address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    blockchain="ethereum"
)

print(f"Address type: {address_info['type']}")  # EOA, Contract, etc.
print(f"First seen: {address_info['first_seen']}")
print(f"Transaction count: {address_info['tx_count']}")
print(f"Current balance: {address_info['balance']} ETH")

# Check if address is a smart contract
if address_info['is_contract']:
    contract_info = await get_contract_info(
        address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
        blockchain="ethereum"
    )
    print(f"Contract name: {contract_info['name']}")
    print(f"Is verified: {contract_info['is_verified']}")
```

## 🔐 Security Features

### MEV Protection
```python
# Enable MEV protection for transactions
await enable_mev_protection(
    max_priority_fee=2.0,  # 2 gwei
    use_private_mempool=True,
    flashbots_enabled=True
)

# Send transaction with MEV protection
protected_tx = await send_protected_transaction(
    to_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    value=1.0,  # 1 ETH
    data="0x",
    blockchain="ethereum"
)
```

### Sandwich Attack Protection
```python
# Configure sandwich protection
await configure_sandwich_protection(
    max_slippage=0.5,  # 0.5%
    revert_on_sandwich=True,
    use_commit_reveal=True
)
```

### Multi-Signature Wallets
```python
# Create multi-sig wallet
multisig = await create_multisig_wallet(
    owners=[
        "0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
        "0x8ba1f109551bD432803012645Hac136c776cc7A90",
        "0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db"
    ],
    required_signatures=2,  # 2 of 3 signatures required
    blockchain="ethereum"
)

# Execute multi-sig transaction
multisig_tx = await execute_multisig_transaction(
    multisig_address=multisig.address,
    to_address="0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
    value=10.0,  # 10 ETH
    data="0x",
    blockchain="ethereum"
)
```

## 🏗️ Advanced Features

### Contract Deployment & Management
```python
# Deploy factory pattern contract
factory = await deploy_factory_contract(
    template_bytecode="0x608060405234801561001057600080fd5b50...",
    init_code="0x608060405234801561001057600080fd5b50...",
    blockchain="polygon"
)

# Create instance from factory
instance = await create_from_factory(
    factory_address=factory.address,
    init_params=["Token Name", "TKN", 18, 1000000],
    blockchain="polygon"
)
```

### Event Monitoring
```python
# Monitor contract events
event_filter = await create_event_filter(
    contract_address="0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",
    event_signature="Transfer(address,address,uint256)",
    from_block="latest",
    blockchain="ethereum"
)

# Get event logs
events = await get_event_logs(
    filter_id=event_filter.id,
    max_results=100
)

for event in events:
    print(f"Transfer: {event['from']} -> {event['to']}: {event['value']}")
```

### Batch Operations
```python
# Execute multiple operations in one transaction
batch_operations = [
    {
        "type": "transfer",
        "to": "0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C",
        "amount": 1.0
    },
    {
        "type": "contract_call",
        "contract": "0xA0b86a33E6441C481e8C26d2b4C28A56E5C13477",
        "function": "transfer",
        "params": ["0x742d35Cc7BF1C4C5C7CB4C3E7BC1a77C", "1000000"]
    }
]

batch_result = await execute_batch_operations(
    operations=batch_operations,
    blockchain="ethereum"
)
```

## 📞 Support

For blockchain-related questions:
- **Blockchain Support**: blockchain@cryptomcp.dev
- **DeFi Questions**: defi@cryptomcp.dev
- **Security Issues**: security@cryptomcp.dev
- **Technical Help**: support@cryptomcp.dev

---

**⚠️ Security Warning**: Always verify contract addresses and double-check transaction details before execution. Use testnet for testing new operations.