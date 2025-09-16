"""
EVM (Ethereum Virtual Machine) blockchain module initialization.
"""

from .client import *
from .tokens import *
from .contracts import *
from .defi import *
from .nft import *
from .ens import *

__all__ = [
    "EVMClient", "get_evm_client", "MultiChainRouter",
    "ERC20Token", "ERC721Token", "ERC1155Token", "TokenManager",
    "SmartContract", "ContractInteraction", "deploy_contract",
    "UniswapV2", "UniswapV3", "SushiSwap", "PancakeSwap",
    "ENSResolver", "resolve_ens_name", "reverse_resolve_ens"
]