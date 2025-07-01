"""
Tests for the subgraph module.
"""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from yield_analysis_sdk.subgraph import (
    _format_price_history_response,
    _format_vault_addresses,
    get_daily_share_price_history_from_subgraph,
)
from yield_analysis_sdk.type import Chain, SharePriceHistory


class TestSubgraph:
    """Test cases for subgraph functionality."""

    def test_format_vault_addresses(self) -> None:
        """Test vault address formatting."""
        addresses = ["0x1234567890abcdef", "0xABCDEF1234567890"]
        formatted = _format_vault_addresses(addresses)
        expected = ["0x1234567890abcdef", "0xabcdef1234567890"]
        assert formatted == expected

    def test_format_price_history_response_valid_data(self) -> None:
        """Test formatting valid price history response."""
        mock_response = {
            "data": {
                "vaultStats_collection": [
                    {
                        "timestamp": "1640995200000000",  # microseconds
                        "pricePerShare": "1.05",
                        "vault": {
                            "address": "0x1234567890abcdef",
                            "name": "Test Vault",
                        },
                    },
                    {
                        "timestamp": "1640908800000000",
                        "pricePerShare": "1.04",
                        "vault": {
                            "address": "0x1234567890abcdef",
                            "name": "Test Vault",
                        },
                    },
                ]
            }
        }

        result = _format_price_history_response(mock_response)

        assert len(result) == 1
        assert result[0].vault_address == "0x1234567890abcdef"
        assert result[0].vault_name == "Test Vault"
        assert len(result[0].price_history) == 2
        assert result[0].price_history[0][0] == 1640908800  # seconds
        assert result[0].price_history[0][1] == 1.04

    def test_format_price_history_response_no_data(self) -> None:
        """Test formatting response with no data."""
        mock_response: Dict[str, Any] = {"data": {"vaultStats_collection": []}}
        result = _format_price_history_response(mock_response)
        assert result == []  # Should return empty list

    @patch("yield_analysis_sdk.subgraph._send_graphql_query_to_subgraph")
    def test_get_daily_share_price_history_from_subgraph(
        self, mock_send_query: Mock
    ) -> None:
        """Test getting daily share price history."""
        mock_response = {
            "data": {
                "vaultStats_collection": [
                    {
                        "timestamp": "1640995200000000",
                        "pricePerShare": "1.05",
                        "vault": {
                            "address": "0x1234567890abcdef",
                            "name": "Test Vault",
                        },
                    }
                ]
            }
        }
        mock_send_query.return_value = mock_response

        vault_addresses = ["0x1234567890abcdef"]
        result = get_daily_share_price_history_from_subgraph(
            Chain.BASE, vault_addresses, 7, "test_api_key"
        )

        assert len(result) == 1
        assert result[0].vault_address == "0x1234567890abcdef"
        mock_send_query.assert_called_once()
