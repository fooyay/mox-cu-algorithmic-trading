from boa.contracts.abi.abi_contract import ABIContract
import boa
from moccasin.config import get_active_network, Network
from script.setup_script import setup_script


def rebalance_example():
    active_network: Network = get_active_network()

    # We're only going to play with eth-forked (the default).
    print(f"Active network: {active_network.name}")

    user: str = boa.env.eoa
    # usdc, weth, wbtc, wsol
    tokens: list[ABIContract]
    pool_contract: ABIContract
    (tokens, pool_contract) = setup_script()


def moccasin_main():

    rebalance_example()
