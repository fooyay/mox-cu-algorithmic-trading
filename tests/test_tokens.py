from script.tokens import _format_balance, _normalized_balance, show_balances


class DummyToken:
    def __init__(self, symbol: str, raw_balance: int, decimals: int):
        self._symbol = symbol
        self._raw_balance = raw_balance
        self._decimals = decimals

    def symbol(self) -> str:
        return self._symbol

    def balanceOf(self, _user: str) -> int:
        return self._raw_balance

    def decimals(self) -> int:
        return self._decimals


def test_format_balance_scales_by_decimals():
    token = DummyToken("USDC", 150, 2)

    result = _format_balance(token, "0xabc")

    assert result == "1.5 (raw: 150)"


def test_normalized_balance_scales_by_decimals():
    token = DummyToken("USDC", 150, 2)

    result = _normalized_balance(token, "0xabc")

    assert result == 1.5


def test_format_balance_with_zero_decimals():
    token = DummyToken("WBTC", 42, 0)

    result = _format_balance(token, "0xabc")

    assert result == "42.0 (raw: 42)"


def test_show_balances_prints_header_and_each_token_balance(capsys):
    user = "0x123"
    tokens = [
        DummyToken("USDC", 2500, 2),
        DummyToken("WETH", 3 * 10**18, 18),
    ]

    show_balances(tokens, user)

    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()

    assert lines[0] == f"Balances for {user}:"
    assert lines[1] == "USDC: 25.0 (raw: 2500)"
    assert lines[2] == "WETH: 3.0 (raw: 3000000000000000000)"
