"""
Tests for the type module.
"""

import json

import pytest

from yield_analysis_sdk.type import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisResult,
    AuditStatus,
    Chain,
    Contract,
    PerformanceAnalysis,
    RegistrationRequest,
    RegistrationResponse,
    SharePriceHistory,
    Strategy,
    StrategyType,
    VaultInfo,
)


class TestTypes:
    """Test cases for type definitions."""

    def test_chain_enum(self) -> None:
        """Test Chain enum values."""
        assert Chain.BASE == "base"
        assert Chain.ETHEREUM == "ethereum"
        assert Chain.ARBITRUM.value == "arbitrum"
        assert Chain.OTHER.value == "other"

    def test_chain_enum_unknown_values(self) -> None:
        """Test Chain enum handling of unknown values."""
        # Test with unknown string values
        assert Chain("unknown_chain") == Chain.OTHER
        assert Chain("invalid_chain") == "other"
        assert Chain("") == Chain.OTHER

        # Test with known values
        assert Chain("base") == "base"
        assert Chain("ethereum") == Chain.ETHEREUM

    def test_strategy_type_enum(self) -> None:
        """Test StrategyType enum values."""
        assert StrategyType.LIQUID_STAKING == "liquid_staking"
        assert StrategyType.LENDING.value == "lending"
        assert StrategyType.YIELD_AGGREGATOR.value == "yield_aggregator"

    def test_audit_status_enum(self) -> None:
        """Test AuditStatus enum values."""
        assert AuditStatus.AUDITED.value == "audited"
        assert AuditStatus.NOT_AUDITED.value == "not_audited"

    def test_analysis_request_creation(self) -> None:
        """Test AnalysisRequest model creation."""
        request = AnalysisRequest(
            strategies=[
                Strategy(
                    chainId=1, address="0xabcdef1234567890abcdef1234567890abcdef12"
                ),
            ]
        )

        assert request.strategies[0].chainId == 1
        assert (
            request.strategies[0].address
            == "0xabcdef1234567890abcdef1234567890abcdef12"
        )

    def test_vault_info_creation(self) -> None:
        """Test VaultInfo model creation."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            address="0x1234567890abcdef1234567890abcdef12345678",
            name="Test Vault",
            protocol="Test",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_cost_bps=0.0,
            exit_cost_bps=0.0,
            risk_free_rate=0.05,
            current_share_price=1.0,
        )

        assert vault_info.chain == Chain.BASE
        assert vault_info.address == "0x1234567890abcdef1234567890abcdef12345678"
        assert vault_info.name == "Test Vault"
        assert vault_info.protocol == "Test"
        assert vault_info.max_deposit_amount == 1000000.0
        assert vault_info.entry_cost_bps == 0.0  # Default value
        assert vault_info.exit_cost_bps == 0.0  # Default value
        assert vault_info.risk_free_rate == 0.05  # Default value

    def test_vault_info_serialization(self) -> None:
        """Test VaultInfo model serialization."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            address="0x1234567890abcdef1234567890abcdef12345678",
            name="Test Vault",
            protocol="Test",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_cost_bps=0.0,
            exit_cost_bps=0.0,
            risk_free_rate=0.05,
            current_share_price=1.0,
        )
        obj = vault_info.model_dump(mode="json")
        assert obj["chain"] == "base"
        assert obj["address"] == "0x1234567890abcdef1234567890abcdef12345678"
        assert obj["name"] == "Test Vault"
        assert obj["protocol"] == "Test"
        assert obj["max_deposit_amount"] == 1000000.0
        assert obj["last_updated_timestamp"] == 1640995200

    def test_performance_analysis_creation(self) -> None:
        """Test PerformanceAnalysis model creation."""
        performance = PerformanceAnalysis(
            apy_7d=5.2,
            apy_30d=4.8,
            apy_90d=4.5,
            volatility_30d=2.1,
            max_drawdown=1.5,
            sharpe_ratio=1.2,
            analysis_period_days=90,
        )

        assert performance.apy_7d == 5.2
        assert performance.apy_30d == 4.8
        assert performance.apy_90d == 4.5
        assert performance.volatility_30d == 2.1
        assert performance.max_drawdown == 1.5
        assert performance.sharpe_ratio == 1.2
        assert performance.analysis_period_days == 90

    def test_vault_performance_analysis_creation(self) -> None:
        """Test AnalysisResult model creation."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            address="0x1234567890abcdef1234567890abcdef12345678",
            name="Test Vault",
            protocol="Test",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_cost_bps=0.0,
            exit_cost_bps=0.0,
            risk_free_rate=0.05,
            current_share_price=1.0,
        )

        performance = PerformanceAnalysis(
            apy_7d=5.2,
            apy_30d=4.8,
            apy_90d=4.5,
            volatility_30d=2.1,
            max_drawdown=1.5,
            sharpe_ratio=1.2,
            analysis_period_days=90,
        )

        vault_analysis = AnalysisResult(vault_info=vault_info, performance=performance)

        assert vault_analysis.vault_info == vault_info
        assert vault_analysis.performance == performance

    def test_analysis_response_creation(self) -> None:
        """Test AnalysisResponse model creation."""
        vault_info = VaultInfo(
            chain=Chain.BASE,
            address="0x1234567890abcdef1234567890abcdef12345678",
            name="Test Vault",
            protocol="Test",
            max_deposit_amount=1000000.0,
            last_updated_timestamp=1640995200,
            entry_cost_bps=0.0,
            exit_cost_bps=0.0,
            risk_free_rate=0.05,
            current_share_price=1.0,
        )

        performance = PerformanceAnalysis(
            apy_7d=5.2,
            apy_30d=4.8,
            apy_90d=4.5,
            volatility_30d=2.1,
            max_drawdown=1.5,
            sharpe_ratio=1.2,
            analysis_period_days=90,
        )

        vault_analysis = AnalysisResult(vault_info=vault_info, performance=performance)

        response = AnalysisResponse(analyses=[vault_analysis])

        assert len(response.analyses) == 1
        assert response.analyses[0] == vault_analysis
        assert response.analyses[0].vault_info.chain == "base"

    def test_share_price_history_creation(self) -> None:
        """Test SharePriceHistory model creation."""
        price_history = SharePriceHistory(
            name="Test Vault",
            address="0x1234567890abcdef1234567890abcdef12345678",
            price_history=[(1640995200, 1.05), (1640908800, 1.04)],
        )

        assert price_history.name == "Test Vault"
        assert price_history.address == "0x1234567890abcdef1234567890abcdef12345678"
        assert len(price_history.price_history) == 2
        assert price_history.price_history[0] == (1640995200, 1.05)

    def test_registration_request_creation(self) -> None:
        """Test RegistrationRequest model creation."""
        request = RegistrationRequest(
            vault=Contract(
                chain=Chain.BASE,
                address="0x1234567890abcdef1234567890abcdef12345678",
            ),
            contracts=[],
            github_repo_url="",
        )

        assert request.vault.chain == Chain.BASE
        assert request.vault.address == "0x1234567890abcdef1234567890abcdef12345678"

    def test_registration_request_validation(self) -> None:
        """Test RegistrationRequest model validation."""
        request = {
            "vault": {
                "chain": "base",
                "address": "0x1234567890abcdef1234567890abcdef12345678",
            },
            "contracts": [],
            "github_repo_url": "",
        }
        RegistrationRequest.model_validate(request)

    def test_registration_request_json_validation(self) -> None:
        """Test RegistrationRequest model JSON validation."""
        request = {
            "vault": {
                "chain": "base",
                "address": "0x1234567890abcdef1234567890abcdef12345678",
            },
            "contracts": [],
            "github_repo_url": "",
        }
        RegistrationRequest.model_validate_json(json.dumps(request))

    def test_registration_response_creation(self) -> None:
        """Test RegistrationResponse model creation."""
        response = RegistrationResponse(
            is_registered=True,
            message="Vault registered successfully",
            contract_tx_hash="0x1234567890abcdef1234567890abcdef12345678",
        )
        assert response.is_registered
        assert response.message == "Vault registered successfully"
        assert response.contract_tx_hash == "0x1234567890abcdef1234567890abcdef12345678"
