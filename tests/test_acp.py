"""
Tests for the ACP module.
"""

from unittest.mock import Mock

import pytest
from virtuals_acp import ACPJobPhase, ACPMemo

from yield_analysis_sdk.acp import (
    extract_analysis_request,
    extract_vault_registration_request,
)
from yield_analysis_sdk.type import (
    AnalysisRequest,
    AnalysisResponse,
    Chain,
    VaultRegistrationRequest,
)


class TestACP:
    """Test cases for ACP functionality."""

    def test_extract_analysis_request_success(self) -> None:
        """Test successful extraction of AnalysisRequest from memos."""
        # Create mock memos
        valid_memo = Mock(spec=ACPMemo)
        valid_memo.next_phase = ACPJobPhase.NEGOTIATION
        valid_memo.content = '{"chain": "base", "underlying_token": "0x1234567890abcdef1234567890abcdef12345678"}'

        memos = [valid_memo]

        result = extract_analysis_request(memos)

        assert result is not None
        assert isinstance(result, AnalysisRequest)
        assert result.chain == Chain.BASE
        assert result.underlying_token == "0x1234567890abcdef1234567890abcdef12345678"

    def test_extract_analysis_request_multiple_memos(self) -> None:
        """Test extraction with multiple memos, where first fails but second succeeds."""
        # Create mock memos - first one invalid, second one valid
        invalid_memo = Mock(spec=ACPMemo)
        invalid_memo.next_phase = ACPJobPhase.NEGOTIATION
        invalid_memo.content = '{"invalid": "json"}'

        valid_memo = Mock(spec=ACPMemo)
        valid_memo.next_phase = ACPJobPhase.NEGOTIATION
        valid_memo.content = '{"chain": "ethereum", "underlying_token": "0xabcdef1234567890abcdef1234567890abcdef12"}'

        memos = [invalid_memo, valid_memo]

        result = extract_analysis_request(memos)

        assert result is not None
        assert isinstance(result, AnalysisRequest)
        assert result.chain == Chain.ETHEREUM
        assert result.underlying_token == "0xabcdef1234567890abcdef1234567890abcdef12"

    def test_extract_analysis_request_no_negotiation_memos(self) -> None:
        """Test when no memos have NEGOTIATION phase."""
        # Create mock memos with different phases
        memo1 = Mock(spec=ACPMemo)
        memo1.next_phase = ACPJobPhase.TRANSACTION
        memo1.content = '{"chain": "base", "underlying_token": "0x1234567890abcdef1234567890abcdef12345678"}'

        memo2 = Mock(spec=ACPMemo)
        memo2.next_phase = ACPJobPhase.COMPLETED
        memo2.content = '{"chain": "ethereum", "underlying_token": "0xabcdef1234567890abcdef1234567890abcdef12"}'

        memos = [memo1, memo2]

        result = extract_analysis_request(memos)

        assert result is None

    def test_extract_analysis_request_empty_memos(self) -> None:
        """Test with empty memos list."""
        result = extract_analysis_request([])
        assert result is None

    def test_extract_analysis_request_all_invalid(self) -> None:
        """Test when all negotiation memos fail to parse."""
        # Create mock memos that all fail to parse
        memo1 = Mock(spec=ACPMemo)
        memo1.next_phase = ACPJobPhase.NEGOTIATION
        memo1.content = '{"invalid": "json"}'

        memo2 = Mock(spec=ACPMemo)
        memo2.next_phase = ACPJobPhase.NEGOTIATION
        memo2.content = '{"missing": "required_fields"}'

        memos = [memo1, memo2]

        result = extract_analysis_request(memos)

        assert result is None

    def test_extract_analysis_request_empty_content(self) -> None:
        """Test with memos that have empty content."""
        # Create mock memos with empty content
        memo1 = Mock(spec=ACPMemo)
        memo1.next_phase = ACPJobPhase.NEGOTIATION
        memo1.content = ""

        memo2 = Mock(spec=ACPMemo)
        memo2.next_phase = ACPJobPhase.NEGOTIATION
        memo2.content = None

        memos = [memo1, memo2]

        result = extract_analysis_request(memos)

        assert result is None

    def test_extract_analysis_request_unknown_chain(self) -> None:
        """Test with unknown chain value that should default to OTHER."""
        # Create mock memo with unknown chain
        memo = Mock(spec=ACPMemo)
        memo.next_phase = ACPJobPhase.NEGOTIATION
        memo.content = '{"chain": "unknown_chain", "underlying_token": "0x1234567890abcdef1234567890abcdef12345678"}'

        memos = [memo]

        result = extract_analysis_request(memos)

        assert result is not None
        assert isinstance(result, AnalysisRequest)
        assert result.chain == Chain.OTHER
        assert result.underlying_token == "0x1234567890abcdef1234567890abcdef12345678"

    def test_extract_vault_registration_request_success(self) -> None:
        """Test successful extraction of VaultRegistrationRequest from memos."""
        # Create mock memos
        valid_memo = Mock(spec=ACPMemo)
        valid_memo.next_phase = ACPJobPhase.NEGOTIATION
        valid_memo.content = '{"chain": "base", "vault_address": "0x1234567890abcdef1234567890abcdef12345678"}'

        memos = [valid_memo]

        result = extract_vault_registration_request(memos)

        assert result is not None
        assert isinstance(result, VaultRegistrationRequest)
        assert result.chain == Chain.BASE
        assert result.vault_address == "0x1234567890abcdef1234567890abcdef12345678"

    def test_extract_vault_registration_request_invalid_address(self) -> None:
        """Test with invalid vault address that should be normalized."""
        # Create mock memo with address without 0x prefix
        memo = Mock(spec=ACPMemo)
        memo.next_phase = ACPJobPhase.NEGOTIATION
        memo.content = '{"chain": "ethereum", "vault_address": "1234567890abcdef1234567890abcdef12345678"}'

        memos = [memo]

        result = extract_vault_registration_request(memos)

        assert result is not None
        assert isinstance(result, VaultRegistrationRequest)
        assert result.chain == Chain.ETHEREUM
        assert result.vault_address == "0x1234567890abcdef1234567890abcdef12345678"

    def test_all_extractors_with_mixed_memos(self) -> None:
        """Test all extractors with a mix of different memo types."""
        # Create various types of memos
        analysis_request_memo = Mock(spec=ACPMemo)
        analysis_request_memo.next_phase = ACPJobPhase.NEGOTIATION
        analysis_request_memo.content = '{"chain": "base", "underlying_token": "0x1234567890abcdef1234567890abcdef12345678"}'

        vault_reg_request_memo = Mock(spec=ACPMemo)
        vault_reg_request_memo.next_phase = ACPJobPhase.NEGOTIATION
        vault_reg_request_memo.content = '{"chain": "ethereum", "vault_address": "0xabcdef1234567890abcdef1234567890abcdef12"}'

        analysis_response_memo = Mock(spec=ACPMemo)
        analysis_response_memo.next_phase = ACPJobPhase.COMPLETED
        analysis_response_memo.content = '{"analyses": []}'

        vault_reg_response_memo = Mock(spec=ACPMemo)
        vault_reg_response_memo.next_phase = ACPJobPhase.COMPLETED
        vault_reg_response_memo.content = (
            '{"is_registered": true, "message": "Success"}'
        )

        memos = [
            analysis_request_memo,
            vault_reg_request_memo,
            analysis_response_memo,
            vault_reg_response_memo,
        ]

        # Test each extractor
        analysis_request = extract_analysis_request(memos)
        vault_reg_request = extract_vault_registration_request(memos)

        assert analysis_request is not None
        assert vault_reg_request is not None

        assert analysis_request.chain == Chain.BASE
        assert vault_reg_request.chain == Chain.ETHEREUM
