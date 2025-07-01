"""
Tests for the type module.
"""

import pytest

from yield_analysis_sdk.type import (
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


class TestTypes:
    """Test cases for type definitions."""

    def test_chain_enum(self) -> None:
        """Test Chain enum values."""
        assert Chain.BASE.value == "base"
        assert Chain.ETHEREUM.value == "ethereum"
        assert Chain.ARBITRUM.value == "arbitrum"
        assert Chain.OTHER.value == "other"

    def test_chain_enum_unknown_values(self) -> None:
        """Test Chain enum handling of unknown values."""
        # Test with unknown string values
        assert Chain("unknown_chain") == Chain.OTHER
        assert Chain("invalid_chain") == Chain.OTHER
        assert Chain("") == Chain.OTHER

        # Test with known values
        assert Chain("base") == Chain.BASE
        assert Chain("ethereum") == Chain.ETHEREUM

    def test_strategy_type_enum(self) -> None:
        """Test StrategyType enum values."""
        assert StrategyType.LIQUID_STAKING.value == "liquid_staking"
        assert StrategyType.LENDING.value == "lending"
        assert StrategyType.YIELD_AGGREGATOR.value == "yield_aggregator"

    def test_audit_status_enum(self) -> None:
        """Test AuditStatus enum values."""
        assert AuditStatus.AUDITED.value == "audited"
        assert AuditStatus.NOT_AUDITED.value == "not_audited"

    def test_analysis_request_creation(self) -> None:
        """Test AnalysisRequest model creation."""
        request = AnalysisRequest(
            chain=Chain.BASE, underlying_token="0x1234567890abcdef"
        )

        assert request.chain == Chain.BASE
        assert request.underlying_token == "0x1234567890abcdef"

    def test_analysis_request_with_unknown_chain(self) -> None:
        """Test AnalysisRequest with unknown chain value."""
        # Test with unknown chain string
        request = AnalysisRequest(
            chain="unknown_chain", underlying_token="0x1234567890abcdef"
        )
        assert request.chain == Chain.OTHER

        # Test with invalid chain string
        request2 = AnalysisRequest(
            chain="invalid_chain_name", underlying_token="0x1234567890abcdef"
        )
        assert request2.chain == Chain.OTHER

    def test_vault_info_creation(self) -> None:
        """Test VaultInfo model creation."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            vault_address="0x1234567890abcdef1234567890abcdef12345678",
            vault_name="Test Vault",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_fee_bps=0.0,
            exit_fee_bps=0.0,
            risk_free_rate=0.05,
        )

        assert vault_info.chain == Chain.BASE
        assert vault_info.vault_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert vault_info.vault_name == "Test Vault"
        assert vault_info.max_deposit_amount == 1000000.0
        assert vault_info.entry_fee_bps == 0.0  # Default value
        assert vault_info.exit_fee_bps == 0.0  # Default value
        assert vault_info.risk_free_rate == 0.05  # Default value

    def test_performance_analysis_creation(self) -> None:
        """Test PerformanceAnalysis model creation."""
        performance = PerformanceAnalysis(
            apy_7d=5.2,
            apy_30d=4.8,
            apy_90d=4.5,
            volatility_30d=2.1,
            max_drawdown=1.5,
            sharpe_ratio=1.2,
            current_price=1.05,
            analysis_period_days=90,
        )

        assert performance.apy_7d == 5.2
        assert performance.apy_30d == 4.8
        assert performance.apy_90d == 4.5
        assert performance.volatility_30d == 2.1
        assert performance.max_drawdown == 1.5
        assert performance.sharpe_ratio == 1.2
        assert performance.current_price == 1.05
        assert performance.analysis_period_days == 90

    def test_vault_performance_analysis_creation(self) -> None:
        """Test VaultPerformanceAnalysis model creation."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            vault_address="0x1234567890abcdef1234567890abcdef12345678",
            vault_name="Test Vault",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_fee_bps=0.0,
            exit_fee_bps=0.0,
            risk_free_rate=0.05,
        )

        performance = PerformanceAnalysis(
            apy_7d=5.2,
            apy_30d=4.8,
            apy_90d=4.5,
            volatility_30d=2.1,
            max_drawdown=1.5,
            sharpe_ratio=1.2,
            current_price=1.05,
            analysis_period_days=90,
        )

        vault_analysis = VaultPerformanceAnalysis(
            vault_info=vault_info, performance=performance
        )

        assert vault_analysis.vault_info == vault_info
        assert vault_analysis.performance == performance

    def test_analysis_response_creation(self) -> None:
        """Test AnalysisResponse model creation."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            vault_address="0x1234567890abcdef1234567890abcdef12345678",
            vault_name="Test Vault",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_fee_bps=0.0,
            exit_fee_bps=0.0,
            risk_free_rate=0.05,
        )

        performance = PerformanceAnalysis(
            apy_7d=5.2,
            apy_30d=4.8,
            apy_90d=4.5,
            volatility_30d=2.1,
            max_drawdown=1.5,
            sharpe_ratio=1.2,
            current_price=1.05,
            analysis_period_days=90,
        )

        vault_analysis = VaultPerformanceAnalysis(
            vault_info=vault_info, performance=performance
        )

        response = AnalysisResponse(analyses=[vault_analysis])

        assert len(response.analyses) == 1
        assert response.analyses[0] == vault_analysis

    def test_share_price_history_creation(self) -> None:
        """Test SharePriceHistory model creation."""
        price_history = SharePriceHistory(
            vault_name="Test Vault",
            vault_address="0x1234567890abcdef1234567890abcdef12345678",
            price_history=[(1640995200, 1.05), (1640908800, 1.04)],
        )

        assert price_history.vault_name == "Test Vault"
        assert (
            price_history.vault_address == "0x1234567890abcdef1234567890abcdef12345678"
        )
        assert len(price_history.price_history) == 2
        assert price_history.price_history[0] == (1640995200, 1.05)
