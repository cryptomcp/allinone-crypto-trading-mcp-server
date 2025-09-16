"""
Custom exceptions for the All-in-One Crypto Trading MCP Server.
"""

from typing import Optional, Any, Dict


class CryptoMCPError(Exception):
    """Base exception for all Crypto MCP errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(CryptoMCPError):
    """Raised when there's a configuration issue."""
    pass


class AuthenticationError(CryptoMCPError):
    """Raised when authentication fails."""
    pass


class InsufficientFundsError(CryptoMCPError):
    """Raised when there are insufficient funds for an operation."""
    pass


class OrderError(CryptoMCPError):
    """Raised when there's an error with order execution."""
    pass


class NetworkError(CryptoMCPError):
    """Raised when there's a network-related error."""
    pass


class RateLimitError(CryptoMCPError):
    """Raised when rate limits are exceeded."""
    pass


class ValidationError(CryptoMCPError):
    """Raised when data validation fails."""
    pass


class RiskManagementError(CryptoMCPError):
    """Raised when risk management rules are violated."""
    pass


class ExchangeError(CryptoMCPError):
    """Raised when there's an exchange-specific error."""
    pass


class BlockchainError(CryptoMCPError):
    """Raised when there's a blockchain-related error."""
    pass


class SignalError(CryptoMCPError):
    """Raised when there's an error with trading signals."""
    pass


class NewsError(CryptoMCPError):
    """Raised when there's an error with news data."""
    pass


class WhaleError(CryptoMCPError):
    """Raised when there's an error with whale tracking."""
    pass


class DexError(CryptoMCPError):
    """Raised when there's an error with DEX operations."""
    pass


class PortfolioError(CryptoMCPError):
    """Raised when there's an error with portfolio operations."""
    pass


class TelegramError(CryptoMCPError):
    """Raised when there's an error with Telegram bot operations."""
    pass