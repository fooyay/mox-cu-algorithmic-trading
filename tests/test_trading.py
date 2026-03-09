from typing import Any, cast

from script.trading import buy_token_with_usdc, sell_all, sell_token_for_usdc
from script.tokens import Portfolio, TokenPosition


class DummyToken:
    def __init__(
        self,
        address: str,
        balance: int = 0,
        decimals_val: int = 18,
        allowance_val: int = 0,
    ):
        self.address = address
        self._balance = balance
        self._decimals = decimals_val
        self._allowance = allowance_val
        self.approve_calls: list[tuple] = []

    def balanceOf(self, _user: str) -> int:
        return self._balance

    def decimals(self) -> int:
        return self._decimals

    def approve(self, spender: str, amount: int) -> None:
        self.approve_calls.append((spender, amount))

    def allowance(self, _owner: str, _spender: str) -> int:
        return self._allowance


class DummyPool:
    def __init__(self, address: str = "0xpool"):
        self.address = address
        self.supply_calls: list[tuple] = []
        self.withdraw_calls: list[tuple] = []

    def supply(self, token_addr: str, amount: int, user: str, referral: int) -> None:
        self.supply_calls.append((token_addr, amount, user, referral))

    def withdraw(self, token_addr: str, amount: int, user: str) -> None:
        self.withdraw_calls.append((token_addr, amount, user))


class DummyRouter:
    def __init__(self, address: str = "0xrouter"):
        self.address = address
        self.exact_input_calls: list[tuple] = []

    def exactInputSingle(self, params: tuple) -> None:
        self.exact_input_calls.append(params)


def _make_portfolio(
    *,
    weth_a_balance: int = 0,
    weth_wallet_balance: int = 0,
    weth_price: float = 2000.0,
    usdc_wallet_balance: int = 0,
    pool: DummyPool | None = None,
    user: str = "0xabc",
) -> tuple["Portfolio", "DummyPool", "DummyToken", "DummyToken", "DummyToken", "DummyToken"]:
    if pool is None:
        pool = DummyPool()
    usdc_token = DummyToken(address="0xusdc", balance=usdc_wallet_balance, decimals_val=6)
    weth_token = DummyToken(address="0xweth", balance=weth_wallet_balance, decimals_val=18)
    weth_a_token = DummyToken(address="0xa_weth", balance=weth_a_balance)
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=cast(Any, usdc_token),
                a_token=None,
                recent_price=1.0,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=cast(Any, weth_token),
                a_token=cast(Any, weth_a_token),
                recent_price=weth_price,
            ),
        ],
        pool_contract=cast(Any, pool),
    )
    return portfolio, pool, usdc_token, weth_token, weth_a_token, cast(Any, None)


# --- sell_all ---


def test_sell_all_calls_pool_withdraw_and_router_swap_when_balance_is_positive():
    pool = DummyPool()
    router = DummyRouter()
    portfolio, pool, _, weth_token, weth_a_token, _ = _make_portfolio(
        weth_a_balance=500, pool=pool
    )

    sell_all(cast(Any, router), portfolio, symbol="WETH")

    assert len(pool.withdraw_calls) == 1
    assert pool.withdraw_calls[0] == ("0xweth", 500, "0xabc")
    assert len(router.exact_input_calls) == 1
    swap_params = router.exact_input_calls[0]
    assert swap_params[0] == "0xweth"   # tokenIn
    assert swap_params[1] == "0xusdc"   # tokenOut
    assert swap_params[4] == 500        # amountIn


def test_sell_all_skips_when_a_token_balance_is_zero():
    pool = DummyPool()
    router = DummyRouter()
    portfolio, pool, _, _, _, _ = _make_portfolio(weth_a_balance=0, pool=pool)

    sell_all(cast(Any, router), portfolio, symbol="WETH")

    assert len(pool.withdraw_calls) == 0
    assert len(router.exact_input_calls) == 0


# --- sell_token_for_usdc ---


def test_sell_token_for_usdc_calculates_token_amount_from_price_and_decimals():
    """price=2000.0, decimals=18, dollar_amount=1000 → token_amount = int(1000/2000 * 1e18)"""
    pool = DummyPool()
    router = DummyRouter()
    portfolio, pool, _, _, _, _ = _make_portfolio(weth_price=2000.0, pool=pool)

    sell_token_for_usdc(
        cast(Any, router), portfolio, symbol="WETH", dollar_amount=1000.0
    )

    expected_token_amount = int(1000.0 / 2000.0 * (10**18))
    assert len(pool.withdraw_calls) == 1
    assert pool.withdraw_calls[0][1] == expected_token_amount


def test_sell_token_for_usdc_calls_pool_withdraw_and_router_swap():
    pool = DummyPool()
    router = DummyRouter()
    portfolio, pool, _, _, _, _ = _make_portfolio(weth_price=2000.0, pool=pool)

    sell_token_for_usdc(
        cast(Any, router), portfolio, symbol="WETH", dollar_amount=1000.0
    )

    assert len(pool.withdraw_calls) == 1
    assert len(router.exact_input_calls) == 1
    swap_params = router.exact_input_calls[0]
    assert swap_params[0] == "0xweth"  # tokenIn
    assert swap_params[1] == "0xusdc"  # tokenOut


# --- buy_token_with_usdc ---


def test_buy_token_with_usdc_calculates_usdc_amount_from_price_and_decimals():
    """usdc price=1.0, decimals=6, dollar_amount=100 → usdc_amount = int(100/1.0 * 1e6)"""
    pool = DummyPool()
    router = DummyRouter()
    # weth_wallet_balance=0 so deposit step is skipped; focus on usdc_amount
    portfolio, pool, usdc_token, _, _, _ = _make_portfolio(pool=pool)

    buy_token_with_usdc(
        cast(Any, router), portfolio, symbol="WETH", dollar_amount=100.0
    )

    expected_usdc_amount = int(100.0 / 1.0 * (10**6))
    assert len(router.exact_input_calls) == 1
    swap_params = router.exact_input_calls[0]
    assert swap_params[4] == expected_usdc_amount   # amountIn (USDC)


def test_buy_token_with_usdc_calls_router_and_deposits_received_tokens():
    pool = DummyPool()
    router = DummyRouter()
    # weth_wallet_balance > 0 simulates tokens received after swap → deposit_in_pool called
    portfolio, pool, _, _, _, _ = _make_portfolio(
        weth_wallet_balance=500_000_000_000_000_000, pool=pool
    )

    buy_token_with_usdc(
        cast(Any, router), portfolio, symbol="WETH", dollar_amount=100.0
    )

    assert len(router.exact_input_calls) == 1
    assert len(pool.supply_calls) == 1


def test_buy_token_with_usdc_skips_deposit_when_no_tokens_received():
    pool = DummyPool()
    router = DummyRouter()
    # weth_wallet_balance=0 → no tokens received → deposit_in_pool not called
    portfolio, pool, _, _, _, _ = _make_portfolio(weth_wallet_balance=0, pool=pool)

    buy_token_with_usdc(
        cast(Any, router), portfolio, symbol="WETH", dollar_amount=100.0
    )

    assert len(router.exact_input_calls) == 1
    assert len(pool.supply_calls) == 0
