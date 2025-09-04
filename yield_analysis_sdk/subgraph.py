from typing import Any, Dict, List

from requests import post

from .exceptions import ConfigurationError, ConnectionError
from .type import Chain, SharePriceHistory
from .validators import validate_address_value

SUBGRAPH_QUERY_URLS = {
    Chain.BASE: "https://gateway.thegraph.com/api/subgraphs/id/46pQKDXgcredBSK9cbGU8qEaPEpEZgQ72hSAkpWnKinJ",
    Chain.ARBITRUM: "https://gateway.thegraph.com/api/subgraphs/id/AH842SqnNHmMM54fY6eX9sGSV4BPo8fmeoj5C3qbNsr1",
}

daily_share_price_query = """
query DailyPriceHistory($vault_addresses: [Bytes!], $length: Int!) {
  vaultStats_collection(
    interval: day
    orderBy: timestamp
    orderDirection: desc
    first: $length
    where: {
        vault_: {
            address_in: $vault_addresses
        }
    }
  ) {
    timestamp
    pricePerShare
    vault {
      address
      name
      decimals
    }
  }
}
"""


def _format_vault_addresses(addresses: List[str]) -> List[str]:
    """Format vault addresses to lowercase for GraphQL compatibility"""
    return [validate_address_value(addr) for addr in addresses]


def _send_graphql_query_to_subgraph(
    chain: Chain,
    query: str,
    variables: Dict[str, Any],
    api_key: str,
) -> Any:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # Prepare the request payload
    payload = {"query": query, "variables": variables}

    # Send the GraphQL request to the Subgraph
    response = post(SUBGRAPH_QUERY_URLS[chain], headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        if "errors" in result:
            raise ConnectionError(f"GraphQL errors: {result['errors']}")
    else:
        raise ConnectionError(f"HTTP Error {response.status_code}: {response.text}")

    return result


def _format_price_history_response(
    res: dict, underlying_asset_decimals: int
) -> List[SharePriceHistory]:
    if not res or "data" not in res or not res["data"]["vaultStats_collection"]:
        return []

    history_by_vault = {}

    for entry in res["data"]["vaultStats_collection"]:
        vault_address = entry["vault"]["address"]
        vault_name = entry["vault"]["name"]
        vault_decimals = int(entry["vault"]["decimals"])
        timestamp = (
            int(entry["timestamp"]) // 1000000
        )  # Convert microseconds to seconds
        decimals_multiplier: float = 10 ** (vault_decimals - underlying_asset_decimals)
        price_per_share = float(entry["pricePerShare"]) * decimals_multiplier

        if vault_address not in history_by_vault:
            history_by_vault[vault_address] = {
                "name": vault_name,
                "address": vault_address,
                "price_history": [],
            }

        history_by_vault[vault_address]["price_history"].append(
            (timestamp, price_per_share)
        )

    # Sort price history by timestamp (oldest first)
    for vault_address in history_by_vault:
        history_by_vault[vault_address]["price_history"].sort(key=lambda x: x[0])

    # Convert to SharePriceHistory objects
    result = []
    for vault_data in history_by_vault.values():
        share_price_history = SharePriceHistory(
            name=vault_data["name"],
            address=vault_data["address"],
            price_history=vault_data["price_history"],
        )
        result.append(share_price_history)

    return result


def get_daily_share_price_history_from_subgraph(
    chain: Chain,
    vault_addresses: List[str],
    underlying_asset_decimals: int,
    length: int,
    api_key: str,
) -> List[SharePriceHistory]:
    """
    Get the daily share price history from the subgraph for a list of vault addresses.

    Args:
        chain: The blockchain chain to query.
        vault_addresses: A list of vault addresses to query.
        underlying_asset_decimals: The number of decimals of the underlying asset. e.g. 6 for USDC.
        length: The number of days to query.
        api_key: The API key for the subgraph.
    """
    if not api_key:
        raise ConfigurationError("SUBGRAPH_API_KEY is required")

    formatted_addresses = _format_vault_addresses(vault_addresses)

    variables = {
        "vault_addresses": formatted_addresses,
        "length": length * len(formatted_addresses),
    }

    res: dict = _send_graphql_query_to_subgraph(
        chain, daily_share_price_query, variables, api_key
    )
    return _format_price_history_response(res, underlying_asset_decimals)
