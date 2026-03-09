from script.setup_script import setup_script
from script.tokens import (
    Portfolio,
    TokenPosition,
    get_portfolio_weights,
    show_portfolio_weights,
)


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


def withdraw_usdc(portfolio: Portfolio) -> None:
    """Withdraw the full aUSDC balance from Aave back to the user wallet."""
    usdc_position: TokenPosition = portfolio.by_symbol["USDC"]
    a_token_balance: int = usdc_position.a_token.balanceOf(portfolio.user)
    if a_token_balance > 0:
        portfolio.pool_contract.withdraw(
            usdc_position.token.address, a_token_balance, portfolio.user
        )


def deposit_usdc(portfolio: Portfolio) -> None:
    """Deposit the full USDC wallet balance into Aave."""
    usdc_position: TokenPosition = portfolio.by_symbol["USDC"]
    balance: int = usdc_position.token.balanceOf(portfolio.user)
    if balance > 0:
        deposit_in_pool(
            pool_contract=portfolio.pool_contract,
            token=usdc_position.token,
            amount=balance,
        )


def sell_down_to_target_weight(
    portfolio: Portfolio, token_position: TokenPosition
) -> None:
    # compute the amount to sell based on the total value of the portfolio and the difference in weights
    # check the price of the token to compute the amount to trade in terms of the token
    # withdraw token from Aave
    # trade on Uniswap to USDC
    pass


def buy_up_to_target_weight(
    portfolio: Portfolio, token_position: TokenPosition
) -> None:
    # compute the amount to buy based on the total value of the portfolio and the difference in weights
    # check the price of the token to compute the amount to trade in terms of the token
    # trade on Uniswap to token
    # deposit token back to Aave
    pass


def rebalance(portfolio: Portfolio) -> None:
    # get total value of portfolio
    # total_value: float = get_total_value(portfolio)

    current_weights: dict[str, float] = get_portfolio_weights(portfolio)

    pending_trades: dict[str, float] = {}

    # first withdraw all USDC from Aave back to the user wallet,
    # so that we can use that USDC to trade with on Uniswap
    withdraw_usdc(portfolio)

    for token_position in portfolio.positions:
        current_weight: float = current_weights.get(token_position.symbol, 0.0)
        target_weight: float = token_position.target_weight or 0.0

        if current_weight > 0 and token_position.target_weight is None:
            # sell all of that token and buy USDC
            break

        weight_difference: float = current_weight - target_weight

        if abs(weight_difference) > BUFFER:
            # add to pending_trades list, which needs to be sorted by difference in weights descending
            pending_trades[token_position.symbol] = weight_difference

    # iterate through pending_trades, starting with the largest difference in weights,
    # and execute the necessary trades to rebalance the portfolio
    for symbol, weight_difference in sorted(
        pending_trades.items(), key=lambda item: item[1], reverse=True
    ):
        if weight_difference > 0:
            # sell some of that token and buy USDC
            pass
        else:
            # buy some of that token and sell USDC
            pass

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
