from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import get_active_network


def get_uniswap_router_contract() -> ABIContract:
    active_network = get_active_network()
    router_contract: ABIContract = active_network.manifest_named("uniswap_swap_router")
    return router_contract
