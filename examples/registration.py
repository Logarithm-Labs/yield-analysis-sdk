import logging
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from virtuals_acp.client import VirtualsACP
from virtuals_acp.contract_clients.contract_client_v2 import ACPContractClientV2
from virtuals_acp.env import EnvSettings
from virtuals_acp.job import ACPJob
from virtuals_acp.models import ACPJobPhase

from yield_analysis_sdk import Chain, Contract, RegistrationRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("BuyerAgent")

load_dotenv(override=True)

VAULT_USDC_MORPHO_SPARK = "0x236919F11ff9eA9550A4287696C2FC9e18E6e890"
BIOS_AGENT_ADDRESS = "0xA908B2A981ae1106e5B047ef44604CCaA1E1c7F9"

# --- Configuration for the job polling interval ---
POLL_INTERVAL_SECONDS = 20


# --------------------------------------------------


def buyer():
    env = EnvSettings()
    acp = VirtualsACP(
        acp_contract_clients=ACPContractClientV2(
            wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
            agent_wallet_address=env.BUYER_AGENT_WALLET_ADDRESS,
            entity_id=env.BUYER_ENTITY_ID,
        ),
    )
    print(f"Buyer ACP Initialized. Agent: {acp.agent_address}")

    # # Browse available agents based on a keyword and cluster name
    # relevant_agents = acp.browse_agents(
    #     keyword="<your_filter_agent_keyword>",
    #     cluster="<your_cluster_name>",
    #     graduated=False,
    # )
    # print(f"Relevant agents: {relevant_agents}")

    # # Pick one of the agents based on your criteria (in this example we just pick the first one)
    # chosen_agent = relevant_agents[0]

    chosen_agent = acp.get_agent(wallet_address=BIOS_AGENT_ADDRESS)

    # Pick one of the service offerings based on your criteria (in this example we just pick the first one)
    chosen_job_offering = chosen_agent.job_offerings[0]

    print(chosen_job_offering)

    # 1. Initiate Job
    print(
        f"\nInitiating job with Seller: {chosen_agent.wallet_address}, Evaluator: {env.EVALUATOR_AGENT_WALLET_ADDRESS}"
    )

    job_id = chosen_job_offering.initiate_job(
        # <your_schema_field> can be found in your ACP Visualiser's "Edit Service" pop-up.
        # Reference: (./images/specify_requirement_toggle_switch.png)
        service_requirement=RegistrationRequest(
            vault=Contract(
                chain=Chain.BASE,
                address=VAULT_USDC_MORPHO_SPARK,
            ),
            contracts=[],
            github_repo_url="https://github.com/yield-analysis/yield-analysis-sdk",
        ).model_dump_json(),
        evaluator_address=env.BUYER_AGENT_WALLET_ADDRESS,
        expired_at=datetime.now() + timedelta(days=1),
    )

    print(f"Job {job_id} initiated")
    # 2. Wait for Seller's acceptance memo (which sets next_phase to TRANSACTION)
    print(f"\nWaiting for Seller to accept job {job_id}...")

    while True:
        # wait for some time before checking job again
        time.sleep(POLL_INTERVAL_SECONDS)
        job: ACPJob = acp.get_job_by_onchain_id(job_id)
        print(f"Polling Job {job_id}: Current Phase: {job.phase.name}")
        memo_to_sign = job.latest_memo

        if (
            job.phase == ACPJobPhase.NEGOTIATION
            and memo_to_sign is not None
            and memo_to_sign.next_phase == ACPJobPhase.TRANSACTION
        ):
            logger.info(f"Paying for job {job.id}")
            job.pay_and_accept_requirement()
            logger.info(f"Job {job.id} paid")

        elif (
            job.phase == ACPJobPhase.TRANSACTION
            and memo_to_sign is not None
            and memo_to_sign.next_phase == ACPJobPhase.REJECTED
        ):
            logger.info(
                f"Signing job {job.id} rejection memo, rejection reason: {memo_to_sign.content}"
            )
            memo_to_sign.sign(True, "Accepts job rejection")
            logger.info(f"Job {job.id} rejection memo signed")

        elif job.phase == ACPJobPhase.EVALUATION:
            print(f"Job {job_id} is in EVALUATION.")
            job.evaluate(True)
            print(f"Job {job_id} evaluated")

        elif job.phase == ACPJobPhase.COMPLETED:
            logger.info(
                f"Job {job.id} completed, received deliverable: {job.deliverable}"
            )

        elif job.phase == ACPJobPhase.REJECTED:
            logger.info(f"Job {job.id} rejected by seller")


if __name__ == "__main__":
    buyer()
