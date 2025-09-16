"""
GOAT SDK proxy addon.
"""

from .goat_proxy import *

__all__ = [
    "GOATProxy", "execute_goat_command", "get_goat_capabilities",
    "proxy_evm_operation", "get_goat_status"
]