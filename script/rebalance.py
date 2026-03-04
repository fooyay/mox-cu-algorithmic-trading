from dataclasses import replace

from script.setup_script import setup_script
from script.tokens import Portfolio, show_position_values
from script.pricing import update_prices


def rebalance_example():
    setup_context = setup_script()
    portfolio: Portfolio = setup_context.portfolio
    updated_positions = update_prices(token_positions=portfolio.positions)
    portfolio = replace(portfolio, positions=updated_positions)

    show_position_values(portfolio=portfolio)


def moccasin_main():

    rebalance_example()
                                                                                                                                                    