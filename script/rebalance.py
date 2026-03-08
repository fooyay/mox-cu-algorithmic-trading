from script.setup_script import setup_script
from script.tokens import Portfolio, get_portfolio_weights, show_portfolio_weights


BUFFER = 0.01


def needs_rebalancing(portfolio: Portfolio) -> bool:
    current_weights: dict[str, float] = get_portfolio_weights(portfolio)

    if sum(current_weights.values()) == 0:
        return False

    for token_position in portfolio.positions:
        current_weight: float = current_weights.get(token_position.symbol, 0.0)
        target_weight: float = token_position.target_weight or 0.0

        if current_weight > 0 and token_position.target_weight is None:
            return True

        if abs(current_weight - target_weight) > BUFFER:
            return True

    return False


def rebalance(portfolio: Portfolio) -> None:




    # withdraw from Aave

    # calculate trades needed to rebalance

    # make trades on Uniswap

    # deposit back to Aave
    pass


def rebalance_example():
    portfolio: Portfolio = setup_script()

    print("Before rebalance:")
    show_portfolio_weights(portfolio=portfolio)

    needs_rebalance: bool = needs_rebalancing(portfolio=portfolio)
    print(f"Needs rebalancing? {needs_rebalance}")

    if needs_rebalance:
        rebalance(portfolio=portfolio)
        print("\nAfter rebalance:")
        show_portfolio_weights(portfolio=portfolio)


def moccasin_main():

    rebalance_example()
