"""
Yield Analysis SDK

A Python SDK for analyzing DeFi vault performance and yield metrics.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .analysis import analyze_yield_with_daily_share_price
from .subgraph import get_daily_share_price_history_from_subgraph

# Import main classes and functions for public API
from .type import (
    AnalysisRequest,
    AnalysisResponse,
    AuditStatus,
    Chain,
    PerformanceAnalysis,
    SharePriceHistory,
    StrategyType,
    VaultInfo,
    VaultPerformanceAnalysis,
)

__all__ = [
    # Types and enums
    "Chain",
    "StrategyType",
    "AuditStatus",
    "AnalysisRequest",
    "VaultInfo",
    "PerformanceAnalysis",
    "VaultPerformanceAnalysis",
    "AnalysisResponse",
    "SharePriceHistory",
    # Main functions
    "get_daily_share_price_history_from_subgraph",
    "analyze_yield_with_daily_share_price",
]
