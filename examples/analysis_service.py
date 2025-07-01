import time
import json
import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

from virtuals_acp import VirtualsACP, ACPJob, ACPJobPhase, ACPMemo

from dotenv import load_dotenv

load_dotenv(override=True)

from yield_analysis_sdk.analysis import analyze_yield_with_daily_share_price
from yield_analysis_sdk.subgraph import get_daily_share_price_history_from_subgraph
from yield_analysis_sdk.type import (
    Chain,
    SharePriceHistory,
    AnalysisRequest,
    AnalysisResponse,
)

from .env import CustomEnvSettings


def validate_memo_content(memo_content: str) -> AnalysisRequest:
    if not memo_content or not memo_content.strip():
        raise ValueError("Memo content is empty")

    try:
        # Parse JSON
        parsed_content = json.loads(memo_content)

        if not isinstance(parsed_content, dict):
            raise ValueError("Memo content must be a JSON object")

        # Validate using Pydantic model
        validated_content = AnalysisRequest(**parsed_content)

        return validated_content

    except json.JSONDecodeError as e:
        raise

    except ValidationError as e:
        raise

    except (KeyError, TypeError) as e:
        raise


def extract_request(memos: list[ACPMemo]) -> Optional[AnalysisRequest]:
    if not memos:
        return None

    for memo in memos:
        if memo.next_phase == ACPJobPhase.NEGOTIATION:
            if memo.content:
                return validate_memo_content(memo.content)
            else:
                raise ValueError("Memo content is empty")

    raise ValueError("No negotiation memo found")


def run_analysis_with_event_loop(analyzer: Analyzer, lookback_window_in_days: int):
    """
    Run analysis in a new event loop to handle async operations.

    Args:
        analyzer: Analyzer instance
        lookback_window_in_days: Lookback window for analysis

    Returns:
        Analysis result
    """
    try:
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the analysis
        result = analyzer.run_openai_analysis(lookback_window_in_days)

        return result
    except Exception as e:
        print(f"Error in analysis thread: {e}")
        raise
    finally:
        # Clean up the event loop
        try:
            loop.close()
        except:
            pass


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
            # Extract and validate lookback window from memos
            lookback_window_in_days = extract_request(job.memos, default_lookback=14)

            # Check if there's a memo that indicates next phase is EVALUATION
            for memo in job.memos:
                if memo.next_phase == ACPJobPhase.EVALUATION:
                    try:
                        analyzer = Analyzer(env.SUBGRAPH_API_KEY)
                        # Run analysis in a separate thread with its own event loop
                        analysis_result = run_analysis_with_event_loop(
                            analyzer, lookback_window_in_days
                        )
                        if analysis_result.is_complete:
                            print(
                                f"Delivering job with {analysis_result.summary}\n", job
                            )
                            job.deliver(analysis_result.summary)
                        else:
                            print(
                                f"Analysis is not complete: {analysis_result.summary}"
                            )
                    except Exception as e:
                        print(f"Error during analysis: {e}")
                    finally:
                        break
                    # print("Delivering job", job)
                    # delivery_data = {
                    #     "type": "url",
                    #     "value": "https://example.com"
                    # }
                    # job.deliver(json.dumps(delivery_data))
                    # break

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
