"""
Tests for the validators module.
"""

import pytest
from pydantic import BaseModel
from yield_analysis_sdk.validators import (
    ChainValidatorMixin,
    VaultAddressValidatorMixin,
    validate_chain_value,
    validate_vault_address_value,
    normalize_vault_address,
)
from yield_analysis_sdk.type import Chain


class TestValidators:
    """Test cases for validators functionality."""

    def test_validate_chain_value_valid(self) -> None:
        """Test validate_chain_value with valid chain values."""
        assert validate_chain_value("base") == Chain.BASE
        assert validate_chain_value("ethereum") == Chain.ETHEREUM
        assert validate_chain_value("arbitrum") == Chain.ARBITRUM

    def test_validate_chain_value_invalid(self) -> None:
        """Test validate_chain_value with invalid chain values."""
        assert validate_chain_value("unknown_chain") == Chain.OTHER
        assert validate_chain_value("invalid_chain") == Chain.OTHER
        assert validate_chain_value("") == Chain.OTHER

    def test_validate_chain_value_already_enum(self) -> None:
        """Test validate_chain_value with already parsed enum values."""
        assert validate_chain_value(Chain.BASE) == Chain.BASE
        assert validate_chain_value(Chain.ETHEREUM) == Chain.ETHEREUM

    def test_chain_validator_mixin(self) -> None:
        """Test ChainValidatorMixin functionality."""

        # Create a test class that uses the mixin
        class TestModel(ChainValidatorMixin, BaseModel):
            chain: Chain

        # Test with valid chain
        model = TestModel(chain="base")
        assert model.chain == Chain.BASE

        # Test with invalid chain
        model2 = TestModel(chain="unknown_chain")
        assert model2.chain == Chain.OTHER

    def test_normalize_vault_address_valid(self) -> None:
        """Test normalize_vault_address with valid addresses."""
        # Test with 0x prefix
        assert (
            normalize_vault_address("0x1234567890abcdef1234567890abcdef12345678")
            == "0x1234567890abcdef1234567890abcdef12345678"
        )

        # Test without 0x prefix
        assert (
            normalize_vault_address("1234567890abcdef1234567890abcdef12345678")
            == "0x1234567890abcdef1234567890abcdef12345678"
        )

        # Test with mixed case
        assert (
            normalize_vault_address("0xABCDEF1234567890abcdef1234567890ABCDEF12")
            == "0xabcdef1234567890abcdef1234567890abcdef12"
        )

        # Test with whitespace
        assert (
            normalize_vault_address("  0x1234567890abcdef1234567890abcdef12345678  ")
            == "0x1234567890abcdef1234567890abcdef12345678"
        )

    def test_normalize_vault_address_invalid(self) -> None:
        """Test normalize_vault_address with invalid addresses."""
        # Test empty address
        with pytest.raises(ValueError, match="Vault address cannot be empty"):
            normalize_vault_address("")

        # Test too short address
        with pytest.raises(ValueError, match="Invalid vault address format"):
            normalize_vault_address("0x1234567890abcdef")

        # Test too long address
        with pytest.raises(ValueError, match="Invalid vault address format"):
            normalize_vault_address(
                "0x1234567890abcdef1234567890abcdef1234567890abcdef"
            )

        # Test invalid characters
        with pytest.raises(ValueError, match="Invalid vault address format"):
            normalize_vault_address("0x1234567890abcdef1234567890abcdef1234567g")

    def test_validate_vault_address_value(self) -> None:
        """Test validate_vault_address_value function."""
        # Test valid address
        result = validate_vault_address_value(
            "0x1234567890abcdef1234567890abcdef12345678"
        )
        assert result == "0x1234567890abcdef1234567890abcdef12345678"

        # Test invalid address
        with pytest.raises(ValueError):
            validate_vault_address_value("invalid_address")

    def test_vault_address_validator_mixin(self) -> None:
        """Test VaultAddressValidatorMixin functionality."""

        # Create a test class that uses the mixin
        class TestModel(VaultAddressValidatorMixin, BaseModel):
            vault_address: str

        # Test with valid address
        model = TestModel(vault_address="0x1234567890abcdef1234567890abcdef12345678")
        assert model.vault_address == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with address without 0x prefix
        model2 = TestModel(vault_address="1234567890abcdef1234567890abcdef12345678")
        assert model2.vault_address == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with invalid address
        with pytest.raises(ValueError):
            TestModel(vault_address="invalid_address")

    def test_combined_validators(self) -> None:
        """Test using both chain and vault address validators together."""

        class TestModel(ChainValidatorMixin, VaultAddressValidatorMixin, BaseModel):
            chain: Chain
            vault_address: str

        # Test with valid values
        model = TestModel(
            chain="base", vault_address="0x1234567890abcdef1234567890abcdef12345678"
        )
        assert model.chain == Chain.BASE
        assert model.vault_address == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with invalid chain but valid address
        model2 = TestModel(
            chain="unknown_chain",
            vault_address="1234567890abcdef1234567890abcdef12345678",
        )
        assert model2.chain == Chain.OTHER
        assert model2.vault_address == "0x1234567890abcdef1234567890abcdef12345678"
