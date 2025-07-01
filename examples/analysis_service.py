import time
import json
import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

from virtuals_acp import VirtualsACP, ACPJob, ACPJobPhase, ACPMemo

from dotenv import load_dotenv

load_dotenv(override=True)

from yield_analysis_sdk import (
    extract_analysis_request,
    extract_analysis_response,
    extract_vault_registration_request,
    extract_vault_registration_response,
    normalize_address,
)
from yield_analysis_sdk.analysis import analyze_yield_with_daily_share_price
from yield_analysis_sdk.subgraph import get_daily_share_price_history_from_subgraph
from yield_analysis_sdk.type import (
    Chain,
    SharePriceHistory,
    AnalysisRequest,
    AnalysisResponse,
)

from .env import CustomEnvSettings

USDC_TOKEN_ADDRESS = {
    Chain.BASE: "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
}

USDC_VAULT_ADDRESSES = {
    Chain.BASE: [
        "0x1234567890abcdef1234567890abcdef12345678",
        "0xabcdef1234567890abcdef1234567890abcdef12",
    ]
}


def seller():
    env = CustomEnvSettings()

    def on_new_task(job: ACPJob):
        # Convert job.phase to ACPJobPhase enum if it's an integer
        if job.phase == ACPJobPhase.REQUEST:
            # Check if there's a memo that indicates next phase is NEGOTIATION
            for memo in job.memos:
                if memo.next_phase == ACPJobPhase.NEGOTIATION:
                    job.respond(True)
                    break
        elif job.phase == ACPJobPhase.TRANSACTION:
            # Check if there's a memo that indicates next phase is EVALUATION
            analysis_request = extract_analysis_request(job.memos)

            if analysis_request is None:
                return

            if analysis_request.chain != Chain.BASE:
                return

            if analysis_request.underlying_token != normalize_address(
                USDC_TOKEN_ADDRESS[analysis_request.chain]
            ):
                return

            for memo in job.memos:
                if memo.next_phase == ACPJobPhase.EVALUATION:
                    # fetch price history
                    price_history = get_daily_share_price_history_from_subgraph(
                        analysis_request.chain,
                        USDC_VAULT_ADDRESSES[analysis_request.chain],
                        90,
                        env.SUBGRAPH_API_KEY,
                    )

                    # analyze yield
                    analysis_response = analyze_yield_with_daily_share_price(
                        price_history,
                        analysis_request.chain,
                    )

                    # deliver job
                    print(analysis_response)
                    job.deliver(analysis_response.model_dump_json())
                    break

    if env.WHITELISTED_WALLET_PRIVATE_KEY is None:
        raise ValueError("WHITELISTED_WALLET_PRIVATE_KEY is not set")
    if env.SELLER_ENTITY_ID is None:
        raise ValueError("SELLER_ENTITY_ID is not set")

    # Initialize the ACP client
    acp_client = VirtualsACP(
        wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
        agent_wallet_address=env.SELLER_AGENT_WALLET_ADDRESS,
        on_new_task=on_new_task,
        entity_id=env.SELLER_ENTITY_ID,
    )

    # Keep the script running to listen for new tasks
    while True:
        print("Waiting for new task...")
        time.sleep(30)


if __name__ == "__main__":
    seller()
