"""
Tests for the validators module.
"""

import pytest
from pydantic import BaseModel

from yield_analysis_sdk.exceptions import ValidationError
from yield_analysis_sdk.type import Chain
from yield_analysis_sdk.validators import (
    ChainMixin,
    UnderlyingTokenValidatorMixin,
    AddressValidatorMixin,
    normalize_address,
    validate_address_value,
    validate_chain_value,
)


class TestValidators:
    """Test cases for validator functionality."""

    def test_validate_chain_value_valid(self) -> None:
        """Test validating valid chain values."""
        assert validate_chain_value("ethereum") == Chain.ETHEREUM
        assert validate_chain_value("base") == Chain.BASE
        assert validate_chain_value("arbitrum") == Chain.ARBITRUM

    def test_validate_chain_value_invalid(self) -> None:
        """Test validating invalid chain values."""
        assert validate_chain_value("invalid_chain") == Chain.OTHER
        assert validate_chain_value("unknown") == Chain.OTHER

    def test_validate_chain_value_already_enum(self) -> None:
        """Test validating chain values that are already enums."""
        assert validate_chain_value(Chain.ETHEREUM) == Chain.ETHEREUM
        assert validate_chain_value(Chain.BASE) == Chain.BASE

    def test_chain_validator_mixin(self) -> None:
        """Test the ChainMixin."""

        class TestModel(ChainMixin, BaseModel):
            chain: Chain

        # Test with string
        model = TestModel(chain="ethereum")
        assert model.chain == Chain.ETHEREUM.value

        # Test with invalid string
        model = TestModel(chain="invalid")
        assert model.chain == Chain.OTHER.value

        # Test with enum
        model = TestModel(chain=Chain.BASE)
        assert model.chain == Chain.BASE.value

    def test_normalize_address_valid(self) -> None:
        """Test normalizing valid addresses."""
        # Test with 0x prefix
        assert (
            normalize_address("0x1234567890abcdef1234567890abcdef12345678")
            == "0x1234567890abcdef1234567890abcdef12345678"
        )

        # Test without 0x prefix
        assert (
            normalize_address("1234567890abcdef1234567890abcdef12345678")
            == "0x1234567890abcdef1234567890abcdef12345678"
        )

        # Test with uppercase
        assert (
            normalize_address("0xABCDEF1234567890ABCDEF1234567890ABCDEF12")
            == "0xabcdef1234567890abcdef1234567890abcdef12"
        )

        # Test with mixed case
        assert (
            normalize_address("0xAbCdEf1234567890AbCdEf1234567890AbCdEf12")
            == "0xabcdef1234567890abcdef1234567890abcdef12"
        )

    def test_normalize_address_invalid(self) -> None:
        """Test normalizing invalid addresses."""
        # Test empty address
        with pytest.raises(ValidationError, match="Address cannot be empty"):
            normalize_address("")

        # Test None address
        with pytest.raises(ValidationError, match="Address cannot be empty"):
            normalize_address(None)

        # Test too short address
        with pytest.raises(ValidationError, match="Invalid address format"):
            normalize_address("0x1234567890abcdef")

        # Test too long address
        with pytest.raises(ValidationError, match="Invalid address format"):
            normalize_address("0x1234567890abcdef1234567890abcdef1234567890abcdef")

        # Test invalid characters
        with pytest.raises(ValidationError, match="Invalid address format"):
            normalize_address("0x1234567890abcdef1234567890abcdef1234567g")

    def test_validate_address_value(self) -> None:
        """Test the validate_address_value function."""
        # Test valid address
        result = validate_address_value("0x1234567890abcdef1234567890abcdef12345678")
        assert result == "0x1234567890abcdef1234567890abcdef12345678"

        # Test address without 0x prefix
        result = validate_address_value("1234567890abcdef1234567890abcdef12345678")
        assert result == "0x1234567890abcdef1234567890abcdef12345678"

        # Test invalid address
        with pytest.raises(ValidationError, match="Invalid address format"):
            validate_address_value("0x1234567890abcdef")

    def test_address_validator_mixin(self) -> None:
        """Test the AddressValidatorMixin."""

        class TestModel(AddressValidatorMixin, BaseModel):
            address: str

        # Test with valid address
        model = TestModel(address="0x1234567890abcdef1234567890abcdef12345678")
        assert model.address == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with address without 0x prefix
        model = TestModel(address="1234567890abcdef1234567890abcdef12345678")
        assert model.address == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with invalid address
        with pytest.raises(ValidationError, match="Invalid address format"):
            TestModel(address="0x1234567890abcdef")

    def test_token_address_validator_mixin(self) -> None:
        """Test the UnderlyingTokenValidatorMixin."""

        class TestModel(UnderlyingTokenValidatorMixin, BaseModel):
            underlying_token: str

        # Test with valid address
        model = TestModel(underlying_token="0x1234567890abcdef1234567890abcdef12345678")
        assert model.underlying_token == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with address without 0x prefix
        model = TestModel(underlying_token="1234567890abcdef1234567890abcdef12345678")
        assert model.underlying_token == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with invalid address
        with pytest.raises(ValidationError, match="Invalid address format"):
            TestModel(underlying_token="0x1234567890abcdef")

    def test_combined_validators(self) -> None:
        """Test combining multiple validators."""

        class TestModel(UnderlyingTokenValidatorMixin, ChainMixin, BaseModel):
            chain: Chain
            underlying_token: str

        # Test with valid data
        model = TestModel(
            chain="ethereum",
            underlying_token="0x1234567890abcdef1234567890abcdef12345678",
        )
        assert model.chain == Chain.ETHEREUM.value
        assert model.underlying_token == "0x1234567890abcdef1234567890abcdef12345678"

        # Test with invalid chain and valid address
        model = TestModel(
            chain="invalid_chain",
            underlying_token="0x1234567890abcdef1234567890abcdef12345678",
        )
        assert model.chain == Chain.OTHER
        assert model.underlying_token == "0x1234567890abcdef1234567890abcdef12345678"
