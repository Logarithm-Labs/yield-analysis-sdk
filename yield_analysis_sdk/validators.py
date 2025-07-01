"""
Common validators and mixins for the yield analysis SDK.
"""

import re
from typing import Any, TYPE_CHECKING
from pydantic import field_validator

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
        return v


class VaultAddressValidatorMixin:
    """Mixin class that provides vault address validation functionality."""

    @field_validator("vault_address", mode="before")
    @classmethod
    def validate_vault_address(cls, v: Any) -> str:
        """Validate vault address format and normalize it."""
        if isinstance(v, str):
            return normalize_vault_address(v)
        return v


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
    return value


def normalize_vault_address(address: str) -> str:
    """
    Normalize vault address format.

    Args:
        address: The vault address to normalize

    Returns:
        Normalized vault address (lowercase, with 0x prefix)
    """
    if not address:
        raise ValueError("Vault address cannot be empty")

    # Remove whitespace
    address = address.strip()

    # Ensure it starts with 0x
    if not address.startswith("0x"):
        address = "0x" + address

    # Convert to lowercase
    address = address.lower()

    # Validate format (0x followed by 40 hex characters)
    if not re.match(r"^0x[a-f0-9]{40}$", address):
        raise ValueError(f"Invalid vault address format: {address}")

    return address


def validate_vault_address_value(address: str) -> str:
    """
    Standalone function to validate vault address values.

    Args:
        address: The vault address to validate

    Returns:
        Normalized vault address

    Raises:
        ValueError: If the address format is invalid
    """
    return normalize_vault_address(address)
