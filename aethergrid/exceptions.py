class AethergridError(Exception):
    """Base exception for all Aethergrid Errors"""
    pass

class NodeError(AethergridError):
    """Base exception for node-related Errors"""
    pass

class InvalidError(NodeError):
    """Raised when node attributes are invalid"""
    pass

class IncompatibleNodeError(NodeError):
    """Raised when two nodes cannot be combined"""
    pass

class RecursionLimitError(AethergridError):
    """Raised when recursion inputs exceed safe limits."""
    pass

class TelemetryError(AethergridError):
    """Raised when telemetry data cannot be processed."""
    pass

class ConfigError(AethergridError):
    """Raised when configuration loading or parsing fails."""
    pass

class AuthenticationError(AethergridError):
    """Raised when security credentials are invalid."""
    pass


class InsufficientFundsError(AethergridError):
    """Raised when a fund operation would overdraw the balance."""
    pass


