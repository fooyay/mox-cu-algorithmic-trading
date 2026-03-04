from dataclasses import replace

from script.setup_script import setup_script
from script.tokens import Portfolio, show_position_values
from script.pricing import update_prices


def rebalance_example():
    portfolio: Portfolio
    portfolio, _pool_contract = setup_script()
    updated_positions = update_prices(token_positions=portfolio.positions)
    portfolio = replace(portfolio, positions=updated_positions)

    show_position_values(portfolio=portfolio)


def moccasin_main():

    rebalance_example()
                                                                                                                                                    