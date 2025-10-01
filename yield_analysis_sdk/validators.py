"""
Common validators and mixins for the yield analysis SDK.
"""

import re
from typing import TYPE_CHECKING, Any, Union

from pydantic import ConfigDict, field_serializer, field_validator

from .exceptions import ValidationError

if TYPE_CHECKING:
    from .type import Chain


class AddressValidatorMixin:
    """Mixin class that provides address validation functionality."""

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, v: Any) -> str:
        """Validate address format and normalize it."""
        if isinstance(v, str):
            return normalize_address(v)
        elif v is None:
            raise ValidationError("Address cannot be None")
        else:
            return str(v)


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
