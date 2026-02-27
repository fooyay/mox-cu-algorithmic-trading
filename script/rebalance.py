from script.setup_script import setup_script
from script.tokens import TokenPosition, show_position_values
from script.pricing import update_prices


def rebalance_example():
    token_positions: list[TokenPosition]
    token_positions, _pool_contract = setup_script()
    token_positions = update_prices(token_positions=token_positions)

    show_position_values(token_positions=token_positions)

    # todo: refactor the above to get a portfolio object from the setup script


def moccasin_main():

    rebalance_example()
