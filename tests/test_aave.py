import boa
from typing import Any, cast

from script.aave import (
    _deposit_tokens_into_pool,
    deposit_in_pool,
    deposit_usdc,
    withdraw_usdc,
)
from script.tokens import Portfolio, TokenPosition


class DummyToken:
    def __init__(
        self,
        balance: int,
        allowance_amount: int = 0,
        address: str = "0xtoken",
    ):
        self._balance = balance
        self._allowance = allowance_amount
        self.address = address
        self.approve_calls: list[tuple] = []

    def balanceOf(self, _user: str) -> int:
        return self._balance

    def allowance(self, _owner: str, _spender: str) -> int:
        return self._allowance

    def approve(self, spender: str, amount: int) -> None:
        self.approve_calls.append((spender, amount))

    def decimals(self) -> int:
        return 6


class DummyPool:
    def __init__(self, address: str = "0xpool"):
        self.address = address
        self.supply_calls: list[tuple] = []
        self.withdraw_calls: list[tuple] = []

    def supply(self, token_addr: str, amount: int, user: str, referral: int) -> None:
        self.supply_calls.append((token_addr, amount, user, referral))

    def withdraw(self, token_addr: str, amount: int, user: str) -> None:
        self.withdraw_calls.append((token_addr, amount, user))


def _make_usdc_portfolio(
    a_token_balance: int, token_balance: int
) -> tuple["Portfolio", "DummyPool", "DummyToken", "DummyToken"]:
    pool = DummyPool()
    a_token = DummyToken(balance=a_token_balance, address="0xa_usdc")
    token = DummyToken(balance=token_balance, address="0xusdc")
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=cast(Any, token),
                a_token=cast(Any, a_token),
            )
        ],
        pool_contract=cast(Any, pool),
    )
    return portfolio, pool, a_token, token


# --- deposit_in_pool ---


def test_deposit_in_pool_approves_when_allowance_is_insufficient():
    pool = DummyPool(address="0xpool")
    token = DummyToken(balance=100, allowance_amount=0, address="0xtoken")

    deposit_in_pool(pool_contract=cast(Any, pool), token=cast(Any, token), amount=50)

    assert len(token.approve_calls) == 1
    assert token.approve_calls[0] == ("0xpool", 50)


def test_deposit_in_pool_skips_approve_when_allowance_is_sufficient():
    pool = DummyPool(address="0xpool")
    token = DummyToken(balance=100, allowance_amount=100, address="0xtoken")

    deposit_in_pool(pool_contract=cast(Any, pool), token=cast(Any, token), amount=50)

    assert len(token.approve_calls) == 0


def test_deposit_in_pool_calls_supply_with_correct_args():
    pool = DummyPool(address="0xpool")
    token = DummyToken(balance=100, allowance_amount=200, address="0xtoken")

    deposit_in_pool(pool_contract=cast(Any, pool), token=cast(Any, token), amount=75)

    assert len(pool.supply_calls) == 1
    token_addr, amount, user, referral = pool.supply_calls[0]
    assert token_addr == "0xtoken"
    assert amount == 75
    assert user == boa.env.eoa
    assert referral == 0


# --- withdraw_usdc ---


def test_withdraw_usdc_calls_pool_withdraw_when_a_token_balance_is_positive():
    portfolio, pool, _, _ = _make_usdc_portfolio(a_token_balance=500, token_balance=0)

    withdraw_usdc(portfolio)

    assert len(pool.withdraw_calls) == 1
    token_addr, amount, user = pool.withdraw_calls[0]
    assert token_addr == "0xusdc"
    assert amount == 500
    assert user == "0xabc"


def test_withdraw_usdc_skips_when_a_token_balance_is_zero():
    portfolio, pool, _, _ = _make_usdc_portfolio(a_token_balance=0, token_balance=0)

    withdraw_usdc(portfolio)

    assert len(pool.withdraw_calls) == 0


# --- deposit_usdc ---


def test_deposit_usdc_calls_supply_when_wallet_balance_is_positive():
    portfolio, pool, _, _ = _make_usdc_portfolio(a_token_balance=0, token_balance=300)

    deposit_usdc(portfolio)

    assert len(pool.supply_calls) == 1


def test_deposit_usdc_skips_when_wallet_balance_is_zero():
    portfolio, pool, _, _ = _make_usdc_portfolio(a_token_balance=0, token_balance=0)

    deposit_usdc(portfolio)

    assert len(pool.supply_calls) == 0


# --- _deposit_tokens_into_pool ---


def test_deposit_tokens_into_pool_deposits_all_tokens_with_positive_balances():
    pool = DummyPool()
    token1 = DummyToken(balance=100, allowance_amount=200, address="0xtoken1")
    token2 = DummyToken(balance=200, allowance_amount=200, address="0xtoken2")

    _deposit_tokens_into_pool(
        tokens=cast(Any, [token1, token2]),
        pool_contract=cast(Any, pool),
        user="0xabc",
    )

    assert len(pool.supply_calls) == 2


def test_deposit_tokens_into_pool_skips_tokens_with_zero_balance():
    pool = DummyPool()
    token = DummyToken(balance=0, address="0xtoken")

    _deposit_tokens_into_pool(
        tokens=cast(Any, [token]),
        pool_contract=cast(Any, pool),
        user="0xabc",
    )

    assert len(pool.supply_calls) == 0
