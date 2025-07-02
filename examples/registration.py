import threading
from datetime import datetime, timedelta

from dotenv import load_dotenv
from virtuals_acp.client import VirtualsACP
from virtuals_acp.env import EnvSettings
from virtuals_acp.job import ACPJob
from virtuals_acp.models import ACPAgentSort, ACPJobPhase

from yield_analysis_sdk import (
    Chain,
    VaultRegistrationRequest,
    VaultRegistrationResponse,
    extract_vault_registration_response,
)

load_dotenv(override=True)

VAULT_USDC_MORPHO_SPARK = "0x7BfA7C4f149E7415b73bdeDfe609237e29CBF34A"


def buyer():
    env = EnvSettings()

    def on_new_task(job: ACPJob):
        if job.phase == ACPJobPhase.NEGOTIATION:
            # Check if there's a memo that indicates next phase is TRANSACTION
            for memo in job.memos:
                if memo.next_phase == ACPJobPhase.TRANSACTION:
                    print("Paying job", job.id)
                    job.pay(job.price)
                    break
        elif job.phase == ACPJobPhase.COMPLETED:
            print("Job completed", job.deliverable)
        elif job.phase == ACPJobPhase.REJECTED:
            print("Job rejected", job)

    def on_evaluate(job: ACPJob):
        print("Evaluation function called", job.memos)
        # Find the deliverable memo
        for memo in job.memos:
            if memo.next_phase == ACPJobPhase.COMPLETED:
                # Evaluate the deliverable by accepting it
                job.evaluate(True)
                break

    if env.WHITELISTED_WALLET_PRIVATE_KEY is None:
        raise ValueError("WHITELISTED_WALLET_PRIVATE_KEY is not set")
    if env.BUYER_AGENT_WALLET_ADDRESS is None:
        raise ValueError("BUYER_AGENT_WALLET_ADDRESS is not set")
    if env.BUYER_ENTITY_ID is None:
        raise ValueError("BUYER_ENTITY_ID is not set")

    acp = VirtualsACP(
        wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
        agent_wallet_address=env.BUYER_AGENT_WALLET_ADDRESS,
        on_new_task=on_new_task,
        on_evaluate=on_evaluate,
        entity_id=env.BUYER_ENTITY_ID,
    )

    # Browse available agents based on a keyword and cluster name
    relevant_agents = acp.browse_agents(keyword="bios")
    print(f"Relevant agents: {relevant_agents}")

    # Pick one of the agents based on your criteria (in this example we just pick the first one)
    chosen_agent = relevant_agents[0]

    # Pick the registration service offering
    chosen_job_offering = chosen_agent.offerings[0]

    job_id = chosen_job_offering.initiate_job(
        # <your_schema_field> can be found in your ACP Visualiser's "Edit Service" pop-up.
        # Reference: (./images/specify_requirement_toggle_switch.png)
        service_requirement=VaultRegistrationRequest(
            chain=Chain.BASE, vault_address=VAULT_USDC_MORPHO_SPARK
        ).model_dump_json(),
        evaluator_address=env.BUYER_AGENT_WALLET_ADDRESS,
        expired_at=datetime.now() + timedelta(days=1),
    )

    print(f"Job {job_id} initiated")
    print("Listening for next steps...")
    # Keep the script running to listen for next steps
    threading.Event().wait()


if __name__ == "__main__":
    buyer()
