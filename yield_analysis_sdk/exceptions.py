"""
Custom exceptions for the yield analysis SDK.
"""

from typing import Any, Dict, List, Optional


class YieldAnalysisError(Exception):
    """Base exception for all yield analysis SDK errors."""
    pass

class DataError(YieldAnalysisError):
    """Exception raised for data-related errors."""
    pass

class ConfigurationError(YieldAnalysisError):
    """Exception raised for configuration errors."""
    pass

class ConnectionError(YieldAnalysisError):
    """Exception raised for connection errors."""
    pass

class ValidationError(YieldAnalysisError):
    """Exception raised for validation errors."""
    pass





