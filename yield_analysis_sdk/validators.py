"""
Common validators and mixins for the yield analysis SDK.
"""

import re
from typing import Any, TYPE_CHECKING, Union
from pydantic import field_validator
from .exceptions import ValidationError

if TYPE_CHECKING:
    from .type import Chain


class ChainValidatorMixin:
    """Mixin class that provides chain validation functionality."""

    @field_validator("chain", mode="before")
    @classmethod
    def validate_chain(cls, v: Any) -> "Chain":
        """Validate chain and return OTHER if not found."""
        from .type import Chain  # Import here to avoid circular import

        if isinstance(v, str):
            try:
                return Chain(v)
            except ValueError:
                return Chain.OTHER
        elif isinstance(v, Chain):
            return v
        else:
            return Chain.OTHER


class VaultAddressValidatorMixin:
    """Mixin class that provides vault address validation functionality."""

    @field_validator("vault_address", mode="before")
    @classmethod
    def validate_vault_address(cls, v: Any) -> str:
        """Validate vault address format and normalize it."""
        if isinstance(v, str):
            return normalize_address(v)
        elif v is None:
            raise ValidationError("Vault address cannot be None")
        else:
            return str(v)


class UnderlyingTokenValidatorMixin:
    """Mixin class that provides token address validation functionality."""

    @field_validator("underlying_token", mode="before")
    @classmethod
    def validate_underlying_token(cls, v: Any) -> str:
        """Validate underlying token address format and normalize it."""
        if isinstance(v, str):
            return normalize_address(v)
        elif v is None:
            raise ValidationError("Underlying token cannot be None")
        else:
            return str(v)


def validate_chain_value(value: Any) -> "Chain":
    """
    Standalone function to validate chain values.

    Args:
        value: The value to validate

    Returns:
        Chain enum value, defaults to Chain.OTHER if invalid
    """
    from .type import Chain  # Import here to avoid circular import

    if isinstance(value, str):
        try:
            return Chain(value)
        except ValueError:
            return Chain.OTHER
    elif isinstance(value, Chain):
        return value
    else:
        return Chain.OTHER


def normalize_address(address: str) -> str:
    """
    Normalize address format.

    Args:
        address: The address to normalize

    Returns:
        Normalized address (lowercase, with 0x prefix)
    """
    if not address:
        raise ValidationError("Address cannot be empty")

    # Remove whitespace
    address = address.strip()

    # Ensure it starts with 0x
    if not address.startswith("0x"):
        address = "0x" + address

    # Convert to lowercase
    address = address.lower()

    # Validate format (0x followed by 40 hex characters)
    if not re.match(r"^0x[a-f0-9]{40}$", address):
        raise ValidationError(f"Invalid address format: {address}")

    return address


def validate_address_value(address: str) -> str:
    """
    Standalone function to validate address values.

    Args:
        address: The address to validate

    Returns:
        Normalized address

    Raises:
        ValidationError: If the address format is invalid
    """
    return normalize_address(address)
