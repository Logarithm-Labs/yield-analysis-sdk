"""
Yield Analysis SDK

A Python SDK for analyzing DeFi vault performance and yield metrics.
"""

__version__ = "0.4.0"
__author__ = "Logarithm Labs"
__email__ = "dev@logarithm.fi"

from .analysis import analyze_yield_with_daily_share_price
from .exceptions import (
    ConfigurationError,
    ConnectionError,
    DataError,
    ValidationError,
    YieldAnalysisError,
)
from .subgraph import get_daily_share_price_history_from_subgraph

# Import main classes and functions for public API
from .type import (
    AnalysisRequest,
    AnalysisResponse,
    AuditStatus,
    Chain,
    PerformanceAnalysis,
    SharePriceHistory,
    Strategy,
    StrategyType,
    VaultInfo,
    AnalysisResult,
    RegistrationRequest,
    RegistrationResponse,
)
from .validators import normalize_address

__all__ = [
    # Types and enums
    "Chain",
    "StrategyType",
    "AuditStatus",
    "AnalysisRequest",
    "Strategy",
    "VaultInfo",
    "PerformanceAnalysis",
    "AnalysisResult",
    "AnalysisResponse",
    "SharePriceHistory",
    "RegistrationRequest",
    "RegistrationResponse",
    # Main functions
    "get_daily_share_price_history_from_subgraph",
    "analyze_yield_with_daily_share_price",
    "normalize_address",
    # Exceptions
    "YieldAnalysisError",
    "DataError",
    "ConfigurationError",
    "ConnectionError",
    "ValidationError",
]
