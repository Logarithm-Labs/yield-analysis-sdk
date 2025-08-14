import time
import json
import threading
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from virtuals_acp import ACPJob, ACPJobPhase, ACPMemo, VirtualsACP

load_dotenv(override=True)

from virtuals_acp.env import EnvSettings

from yield_analysis_sdk import (
    normalize_address,
)
from yield_analysis_sdk import analyze_yield_with_daily_share_price
from yield_analysis_sdk import get_daily_share_price_history_from_subgraph
from yield_analysis_sdk import (
    AnalysisRequest,
    AnalysisResponse,
    Chain,
    SharePriceHistory,
    VaultInfo,
    AnalysisResult,
)


class CustomEnvSettings(EnvSettings):
    SUBGRAPH_API_KEY: Optional[str] = None


USDC_TOKEN_ADDRESS = {
    Chain.BASE: "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
}

USDC_VAULT_ADDRESSES = {
    Chain.BASE: [
        "0xc1256Ae5FF1cf2719D4937adb3bbCCab2E00A2Ca",
        "0x616a4E1db48e22028f6bbf20444Cd3b8e3273738",
    ]
}

ID_TO_CHAIN = {
    1: Chain.ETHEREUM,
    8453: Chain.BASE,
    42161: Chain.ARBITRUM,
    10: Chain.OPTIMISM,
    137: Chain.POLYGON,
    56: Chain.BSC,
    33139: Chain.GNOS,
}


def seller():
    env = CustomEnvSettings()

    def on_new_task(job: ACPJob):
        # Convert job.phase to ACPJobPhase enum if it's an integer
        if job.phase == ACPJobPhase.REQUEST:
            # Check if there's a memo that indicates next phase is NEGOTIATION
            for memo in job.memos:
                if memo.next_phase == ACPJobPhase.NEGOTIATION:
                    try:
                        AnalysisRequest.model_validate_json(memo.content)
                        job.respond(True)
                    except ValidationError as e:
                        job.respond(False, "Invalid request format")
                    finally:
                        break
        elif job.phase == ACPJobPhase.TRANSACTION:

            for memo in job.memos:
                if memo.next_phase == ACPJobPhase.EVALUATION:
                    # Check if there's a memo that indicates next phase is EVALUATION
                    analysis_request = AnalysisRequest.model_validate_json(
                        job.service_requirement
                    )

                    # for test purpose, only support strategies with same chainId
                    # fetch price history
                    price_histories = get_daily_share_price_history_from_subgraph(
                        ID_TO_CHAIN[analysis_request.strategies[0].chainId],
                        [
                            strategy.address.lower()
                            for strategy in analysis_request.strategies
                        ],
                        6,
                        90,
                        env.SUBGRAPH_API_KEY,
                    )

                    # analyze yield
                    result: AnalysisResponse = AnalysisResponse(analyses=[])
                    for price_history in price_histories:
                        result.analyses.append(
                            AnalysisResult(
                                vault_info=VaultInfo(
                                    chain=analysis_request.chain,
                                    vault_address=price_history.vault_address,
                                    vault_name=price_history.vault_name,
                                    protocol="Morpho Meta Vault",
                                    last_updated_timestamp=int(time.time()),
                                ),
                                performance=analyze_yield_with_daily_share_price(
                                    price_history,
                                ),
                            )
                        )

                    print(f"Delivering analysis result: {result.model_dump_json()}")
                    delivery_data = {"type": "text", "value": result.model_dump_json()}

                    # deliver job
                    job.deliver(json.dumps(delivery_data))
                    break

    if env.WHITELISTED_WALLET_PRIVATE_KEY is None:
        raise ValueError("WHITELISTED_WALLET_PRIVATE_KEY is not set")
    if env.SELLER_ENTITY_ID is None:
        raise ValueError("SELLER_ENTITY_ID is not set")

    # Initialize the ACP client
    VirtualsACP(
        wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
        agent_wallet_address=env.SELLER_AGENT_WALLET_ADDRESS,
        on_new_task=on_new_task,
        entity_id=env.SELLER_ENTITY_ID,
    )

    print("Waiting for new task...")
    # Keep the script running to listen for new tasks
    threading.Event().wait()


if __name__ == "__main__":
    seller()
