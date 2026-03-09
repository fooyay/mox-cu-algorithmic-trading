from dataclasses import dataclass
from boa.contracts.abi.abi_contract import ABIContract


@dataclass(frozen=True)
class TokenPosition:
    symbol: str
    underlying_symbol: str
    token: ABIContract
    a_token: ABIContract | None
    recent_price: float | None = None
    target_weight: float | None = None


@dataclass(frozen=True)
class Portfolio:
    user: str
    positions: list[TokenPosition]
    pool_contract: ABIContract | None = None

    @property
    def by_symbol(self) -> dict[str, "TokenPosition"]:
        return {position.symbol: position for position in self.positions}


def _position_values_and_total(portfolio: Portfolio) -> tuple[list[float], float]:
    position_values: list[float] = []
    total_value: float = 0.0
    for token_position in portfolio.positions:
        if token_position.recent_price is not None:
            value: float = (
                _normalized_balance(token_position.a_token, portfolio.user)
                * token_position.recent_price
            )
            position_values.append(value)
            total_value += value
        else:
            position_values.append(0.0)
    return position_values, total_value


def get_portfolio_value(portfolio: Portfolio) -> float:
    position_values, total_value = _position_values_and_total(portfolio)
    return total_value


def get_portfolio_weights(portfolio: Portfolio) -> dict[str, float]:
    position_values, total_value = _position_values_and_total(portfolio)
    if total_value == 0:
        return {token_position.symbol: 0.0 for token_position in portfolio.positions}

    return {
        token_position.symbol: value / total_value
        for token_position, value in zip(portfolio.positions, position_values)
    }


def _normalized_balance(token: ABIContract | None, user: str) -> float:
    if token is None:
        return 0.0
    raw_balance: int = token.balanceOf(user)
    decimals: int = token.decimals()
    normalized_balance: float = raw_balance / (10**decimals)
    return normalized_balance


def _format_balance(token: ABIContract, user: str) -> str:
    raw_balance: int = token.balanceOf(user)
    formatted_balance: float = _normalized_balance(token, user)
    return f"{formatted_balance} (raw: {raw_balance})"


def show_balances(tokens: list[ABIContract], user: str) -> None:
    print(f"Balances for {user}:")
    for token in tokens:
        symbol: str = token.symbol()
        balance_str = _format_balance(token, user)
        print(f"{symbol}: {balance_str}")


def show_aave_positions(portfolio: Portfolio) -> None:
    print("Aave positions:")
    for token_position in portfolio.positions:
        if token_position.a_token is not None:
            print(
                f"{token_position.symbol}: {_format_balance(token=token_position.a_token, user=portfolio.user)}"
            )
        else:
            print(f"{token_position.symbol} has no matching aToken")


def show_position_values(portfolio: Portfolio) -> None:
    print("Position values:")
    output_string: str = ""
    position_values, total_usd_value = _position_values_and_total(portfolio)
    for token_position, value in zip(portfolio.positions, position_values):
        if token_position.recent_price is not None:
            output_string += f"{token_position.symbol}: {value:.2f} USD\n"
        else:
            output_string += f"{token_position.symbol} has no recent price"
    print(output_string)
    print(f"Total USD value: {total_usd_value:.2f} USD")


def show_portfolio_weights(portfolio: Portfolio) -> None:
    print("Portfolio weights:")
    position_values, _ = _position_values_and_total(portfolio)
    portfolio_weights = get_portfolio_weights(portfolio)

    for token_position, value in zip(portfolio.positions, position_values):
        weight: float = portfolio_weights[token_position.symbol] * 100
        print(f"{token_position.symbol}: ${value:.2f} ({weight:.2f}%)")
