"""
Tests for the validators module.
"""

import pytest
from pydantic import BaseModel

from yield_analysis_sdk.exceptions import ValidationError
from yield_analysis_sdk.validators import AddressValidatorMixin, normalize_address


class TestValidators:
    """Test cases for validator functionality."""

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
