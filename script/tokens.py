from dataclasses import dataclass
from boa.contracts.abi.abi_contract import ABIContract


@dataclass(frozen=True)
class TokenPosition:
    symbol: str
    underlying_symbol: str
    token: ABIContract
    a_token: ABIContract | None
    recent_price: float | None = None


def _normalized_balance(token: ABIContract, user: str) -> float:
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


def show_aave_positions(token_positions: list[TokenPosition], user: str) -> None:
    print("Aave positions:")
    for token_position in token_positions:
        if token_position.a_token is not None:
            print(
                f"{token_position.symbol}: {_format_balance(token=token_position.a_token, user=user)}"
            )
        else:
            print(f"{token_position.symbol} has no matching aToken")


def show_position_values(token_positions: list[TokenPosition]) -> None:
    pass
