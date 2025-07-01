from typing import Optional
from virtuals_acp import VirtualsACP, ACPJob, ACPJobPhase, ACPMemo  # type: ignore
from .type import (
    AnalysisRequest,
    AnalysisResponse,
    VaultRegistrationRequest,
    VaultRegistrationResponse,
)


def extract_analysis_request(memos: list[ACPMemo]) -> Optional[AnalysisRequest]:
    """
    Extract AnalysisRequest from memos by trying each negotiation memo until one works.

    Args:
        memos: List of ACP memos to process

    Returns:
        AnalysisRequest if a valid one is found, otherwise None
    """
    if not memos:
        return None

    for memo in memos:
        if memo.next_phase == ACPJobPhase.NEGOTIATION:
            if memo.content:
                try:
                    return AnalysisRequest.model_validate_json(memo.content)
                except Exception:
                    # Continue to next memo if this one fails to parse
                    continue
            else:
                # Skip empty memos
                continue

    # No valid memo found
    return None


def extract_analysis_response(memos: list[ACPMemo]) -> Optional[AnalysisResponse]:
    """
    Extract AnalysisResponse from memos by trying each negotiation memo until one works.

    Args:
        memos: List of ACP memos to process

    Returns:
        AnalysisResponse if a valid one is found, otherwise None
    """
    if not memos:
        return None

    for memo in memos:
        if memo.next_phase == ACPJobPhase.COMPLETED:
            if memo.content:
                try:
                    return AnalysisResponse.model_validate_json(memo.content)
                except Exception:
                    # Continue to next memo if this one fails to parse
                    continue
            else:
                # Skip empty memos
                continue

    # No valid memo found
    return None


def extract_vault_registration_request(
    memos: list[ACPMemo],
) -> Optional[VaultRegistrationRequest]:
    """
    Extract VaultRegistrationRequest from memos by trying each negotiation memo until one works.

    Args:
        memos: List of ACP memos to process

    Returns:
        VaultRegistrationRequest if a valid one is found, otherwise None
    """
    if not memos:
        return None

    for memo in memos:
        if memo.next_phase == ACPJobPhase.NEGOTIATION:
            if memo.content:
                try:
                    return VaultRegistrationRequest.model_validate_json(memo.content)
                except Exception:
                    # Continue to next memo if this one fails to parse
                    continue
            else:
                # Skip empty memos
                continue

    # No valid memo found
    return None


def extract_vault_registration_response(
    memos: list[ACPMemo],
) -> Optional[VaultRegistrationResponse]:
    """
    Extract VaultRegistrationResponse from memos by trying each negotiation memo until one works.

    Args:
        memos: List of ACP memos to process

    Returns:
        VaultRegistrationResponse if a valid one is found, otherwise None
    """

    if not memos:
        return None

    for memo in memos:
        if memo.next_phase == ACPJobPhase.COMPLETED:
            if memo.content:
                try:
                    return VaultRegistrationResponse.model_validate_json(memo.content)
                except Exception:
                    # Continue to next memo if this one fails to parse
                    continue
            else:
                # Skip empty memos
                continue

    # No valid memo found
    return None
