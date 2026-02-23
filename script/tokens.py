from IPython.testing.decorators import f
from boa.contracts.abi.abi_contract import ABIContract


def _format_balance(token: ABIContract, user: str) -> str:
    raw_balance: int = token.balanceOf(user)
    decimals: int = token.decimals()
    formatted_balance: float = raw_balance / (10**decimals)
    return f"{formatted_balance} (raw: {raw_balance})"


def show_balances(tokens: list[ABIContract], user: str) -> None:
    print(f"Balances for {user}:")
    for token in tokens:
        symbol: str = token.symbol()
        balance_str = _format_balance(token, user)
        print(f"{symbol}: {balance_str}")
