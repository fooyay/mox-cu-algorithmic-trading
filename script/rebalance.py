from script.setup_script import setup_script
from script.tokens import Portfolio, show_position_values
from script.pricing import update_portfolio_prices


def rebalance_example():
    setup_context = setup_script()
    portfolio: Portfolio = setup_context.portfolio
    portfolio = update_portfolio_prices(portfolio=portfolio)

    show_position_values(portfolio=portfolio)


def moccasin_main():

    rebalance_example()
                                                                                                                                                    