from boa.contracts.abi.abi_contract import ABIContract
import boa
from moccasin.config import get_active_network, Network
from script.setup_script import setup_script
from script.tokens import TokenPosition
from script.pricing import get_price


def rebalance_example():
    active_network: Network = get_active_network()

    # We're only going to play with eth-forked (the default).
    print(f"Active network: {active_network.name}")

    user: str = boa.env.eoa
    token_positions: list[TokenPosition]
    pool_contract: ABIContract
    token_positions, pool_contract = setup_script(user=user)

    token_prices: dict[str, float] = {}
    for token in token_positions:
        price: float = get_price(network=active_network, symbol=token.underlying_symbol)
        token_prices[token.symbol] = price
        print(f"Price for {token.symbol}: {price}")


def moccasin_main():

    rebalance_example()
