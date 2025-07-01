"""
Tests for the analysis module.
"""

import pytest

from yield_analysis_sdk.analysis import analyze_yield_with_daily_share_price
from yield_analysis_sdk.type import PerformanceAnalysis, SharePriceHistory


class TestAnalysis:
    """Test cases for yield analysis functionality."""

    def test_analyze_yield_with_daily_share_price_success(self) -> None:
        """Test successful yield analysis with valid data."""
        # Create sample price data (30 days, increasing trend)
        prices = [1.0 + i * 0.001 for i in range(30)]
        # Create timestamps (oldest first)
        timestamps = [1640995200 + i * 86400 for i in range(30)]
        # No reverse here

        # Create SharePriceHistory object
        share_price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=list(zip(timestamps, prices)),
        )

        result = analyze_yield_with_daily_share_price(share_price_history)

        assert isinstance(result, PerformanceAnalysis)
        assert result.apy_7d > 0
        assert result.apy_30d > 0
        assert result.apy_90d == 0.0  # Not enough data for 90d
        assert result.volatility_30d >= 0
        assert result.max_drawdown >= 0
        assert result.current_price == prices[-1]
        assert result.analysis_period_days == 30

    def test_analyze_yield_with_daily_share_price_insufficient_data(self) -> None:
        """Test analysis with insufficient data."""
        # Test with empty price history
        empty_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=[],
        )
        with pytest.raises(
            ValueError, match="At least 2 daily share prices are required"
        ):
            analyze_yield_with_daily_share_price(empty_history)

        # Test with single price
        single_price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=[(1640995200, 1.0)],
        )
        with pytest.raises(
            ValueError, match="At least 2 daily share prices are required"
        ):
            analyze_yield_with_daily_share_price(single_price_history)

    def test_analyze_yield_with_daily_share_price_decreasing_trend(self) -> None:
        """Test analysis with decreasing price trend."""
        prices = [1.0 - i * 0.001 for i in range(30)]
        timestamps = [1640995200 + i * 86400 for i in range(30)]
        # No reverse here

        share_price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=list(zip(timestamps, prices)),
        )

        result = analyze_yield_with_daily_share_price(share_price_history)

        assert result.apy_7d < 0
        assert result.apy_30d < 0
        assert result.current_price == prices[-1]

    def test_analyze_yield_with_daily_share_price_volatile_data(self) -> None:
        """Test analysis with volatile price data."""
        import random

        random.seed(42)  # For reproducible tests

        # Create volatile price data
        prices = [1.0]
        for i in range(30):
            change = random.uniform(-0.02, 0.02)  # ±2% daily change
            prices.append(prices[-1] * (1 + change))

        timestamps = [1640995200 + i * 86400 for i in range(31)]
        # No reverse here

        share_price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=list(zip(timestamps, prices)),
        )

        result = analyze_yield_with_daily_share_price(share_price_history)

        assert result.volatility_30d > 0
        assert result.max_drawdown >= 0
        assert result.sharpe_ratio is not None

    def test_analyze_yield_with_daily_share_price_custom_risk_free_rate(self) -> None:
        """Test analysis with custom risk-free rate."""
        prices = [1.0 + i * 0.001 for i in range(30)]
        timestamps = [1640995200 + i * 86400 for i in range(30)]
        # No reverse here

        share_price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=list(zip(timestamps, prices)),
        )

        result = analyze_yield_with_daily_share_price(
            share_price_history, risk_free_rate=0.03
        )

        assert isinstance(result, PerformanceAnalysis)
        # The Sharpe ratio should be different with different risk-free rate
        result_default = analyze_yield_with_daily_share_price(
            share_price_history, risk_free_rate=0.05
        )
        assert result.sharpe_ratio != result_default.sharpe_ratio

    def test_analyze_yield_with_daily_share_price_90_days_data(self) -> None:
        """Test analysis with 90+ days of data."""
        prices = [1.0 + i * 0.001 for i in range(100)]
        timestamps = [1640995200 + i * 86400 for i in range(100)]
        # No reverse here

        share_price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef",
            price_history=list(zip(timestamps, prices)),
        )

        result = analyze_yield_with_daily_share_price(share_price_history)

        assert result.apy_90d > 0
        assert result.analysis_period_days == 100
