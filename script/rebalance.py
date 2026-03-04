from script.setup_script import setup_script
from script.tokens import Portfolio, show_position_values


def rebalance_example():
    setup_context = setup_script()
    portfolio: Portfolio = setup_context.portfolio

    show_position_values(portfolio=portfolio)


def moccasin_main():

    rebalance_example()
