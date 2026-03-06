from operator import ne
from script.setup_script import setup_script
from script.tokens import Portfolio, get_portfolio_weights, show_portfolio_weights

DESIRED_WEIGHTS: dict[str, float] = {
    "USDC": 0.15,
    "WETH": 0.30,
    "WBTC": 0.50,
    "LINK": 0.05,
}
BUFFER = 0.01


def needs_rebalancing(portfolio: Portfolio) -> bool:
    current_weights: dict[str, float] = get_portfolio_weights(portfolio)

    if sum(current_weights.values()) == 0:
        return False

    for symbol, current_weight in current_weights.items():
        if symbol not in DESIRED_WEIGHTS and current_weight > 0:
            return True

        desired_weight: float = DESIRED_WEIGHTS.get(symbol, 0.0)
        if abs(current_weight - desired_weight) > BUFFER:
            return True

    for symbol, desired_weight in DESIRED_WEIGHTS.items():
        if symbol not in current_weights and desired_weight > BUFFER:
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
