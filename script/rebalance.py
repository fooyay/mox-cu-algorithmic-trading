from script.aave import deposit_usdc, withdraw_usdc
from script.setup_script import setup_script
from script.tokens import (
    Portfolio,
    get_portfolio_value,
    get_portfolio_weights,
    show_portfolio_weights,
)
from script.trading import (
    buy_token_with_usdc,
    get_uniswap_router_contract,
    sell_all,
    sell_token_for_usdc,
)
from boa.contracts.abi.abi_contract import ABIContract

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


def _compute_pending_trades(
    positions: list,
    current_weights: dict[str, float],
    portfolio_value: float,
) -> dict[str, float]:
    """Return signed dollar deltas for positions needing partial rebalancing.

    Positive value = overweight (should sell). Negative value = underweight (should buy).
    Excludes USDC and positions scheduled for full liquidation (target_weight None or 0).
    """
    pending_trades: dict[str, float] = {}
    for token_position in positions:
        if token_position.symbol == "USDC":
            continue
        if token_position.target_weight is None or token_position.target_weight == 0:
            continue  # full liquidation; handled separately via sell_all
        current_weight: float = current_weights.get(token_position.symbol, 0.0)
        weight_difference: float = current_weight - token_position.target_weight
        if abs(weight_difference) > BUFFER:
            pending_trades[token_position.symbol] = weight_difference * portfolio_value
    return pending_trades


def rebalance(portfolio: Portfolio, router: ABIContract | None = None) -> None:
    portfolio_value: float = get_portfolio_value(portfolio)
    current_weights: dict[str, float] = get_portfolio_weights(portfolio)

    # first withdraw all USDC from Aave back to the user wallet,
    # so that we can use that USDC to trade with on Uniswap
    withdraw_usdc(portfolio)

    if router is None:
        router = get_uniswap_router_contract()

    for token_position in portfolio.positions:
        if token_position.symbol == "USDC":
            # We handle USDC at the end, after selling all other tokens for USDC
            # and buying all other tokens with USDC, because we need USDC to
            # execute the other trades.
            continue

        current_weight: float = current_weights.get(token_position.symbol, 0.0)

        # if the target weight is None or zero, and we currently have a balance of that token,
        # we want to sell all of it and buy USDC
        if current_weight > 0 and (
            token_position.target_weight is None or token_position.target_weight == 0
        ):
            sell_all(router, portfolio, symbol=token_position.symbol)

    pending_trades: dict[str, float] = _compute_pending_trades(
        positions=portfolio.positions,
        current_weights=current_weights,
        portfolio_value=portfolio_value,
    )

    # iterate through pending_trades, starting with the largest difference in weights,
    # and execute the necessary trades to rebalance the portfolio
    for symbol, dollar_delta in sorted(
        pending_trades.items(), key=lambda item: item[1], reverse=True
    ):
        dollar_amount: float = abs(dollar_delta)
        if dollar_delta > 0:
            sell_token_for_usdc(
                router=router,
                portfolio=portfolio,
                symbol=symbol,
                dollar_amount=dollar_amount,
            )
        else:
            buy_token_with_usdc(
                router=router,
                portfolio=portfolio,
                symbol=symbol,
                dollar_amount=dollar_amount,
            )

    # after all trades are executed, deposit any remaining USDC back into Aave
    deposit_usdc(portfolio)


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
