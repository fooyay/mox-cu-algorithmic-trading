from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import get_active_network

from script.aave import deposit_in_pool
from script.tokens import Portfolio, TokenPosition

UNISWAP_POOL_FEE = 3000  # 0.3% fee tier


def get_uniswap_router_contract() -> ABIContract:
    active_network = get_active_network()
    router_contract: ABIContract = active_network.manifest_named("uniswap_swap_router")
    return router_contract


def sell_all(router: ABIContract, portfolio: Portfolio, symbol: str) -> None:
    """Withdraw the full aToken balance from Aave and swap it for USDC on Uniswap."""
    token_position: TokenPosition = portfolio.by_symbol[symbol]
    balance: int = token_position.a_token.balanceOf(portfolio.user)
    if balance > 0:
        portfolio.pool_contract.withdraw(
            token_position.token.address, balance, portfolio.user
        )
        usdc_address: str = portfolio.by_symbol["USDC"].token.address
        token_position.token.approve(router.address, balance)
        router.exactInputSingle(
            (
                token_position.token.address,
                usdc_address,
                UNISWAP_POOL_FEE,
                portfolio.user,
                balance,
                0,  # amountOutMinimum: no slippage protection for sell_all
                0,  # sqrtPriceLimitX96: no price limit
            )
        )


def sell_token_for_usdc(
    router: ABIContract, portfolio: Portfolio, symbol: str, dollar_amount: float
) -> None:
    """Withdraw `dollar_amount` USD worth of `symbol` from Aave and swap it for USDC."""
    token_position: TokenPosition = portfolio.by_symbol[symbol]
    token_decimals: int = token_position.token.decimals()
    token_amount: int = int(
        dollar_amount / token_position.recent_price * (10**token_decimals)
    )

    portfolio.pool_contract.withdraw(
        token_position.token.address, token_amount, portfolio.user
    )

    usdc_address: str = portfolio.by_symbol["USDC"].token.address
    token_position.token.approve(router.address, token_amount)
    router.exactInputSingle(
        (
            token_position.token.address,
            usdc_address,
            UNISWAP_POOL_FEE,
            portfolio.user,
            token_amount,
            0,  # amountOutMinimum
            0,  # sqrtPriceLimitX96
        )
    )


def buy_token_with_usdc(
    router: ABIContract, portfolio: Portfolio, symbol: str, dollar_amount: float
) -> None:
    """Swap `dollar_amount` USD worth of USDC for `symbol` on Uniswap and deposit into Aave."""
    token_position: TokenPosition = portfolio.by_symbol[symbol]
    usdc_position: TokenPosition = portfolio.by_symbol["USDC"]
    usdc_decimals: int = usdc_position.token.decimals()
    usdc_amount: int = int(
        dollar_amount / usdc_position.recent_price * (10**usdc_decimals)
    )

    usdc_position.token.approve(router.address, usdc_amount)
    router.exactInputSingle(
        (
            usdc_position.token.address,
            token_position.token.address,
            UNISWAP_POOL_FEE,
            portfolio.user,
            usdc_amount,
            0,  # amountOutMinimum
            0,  # sqrtPriceLimitX96
        )
    )

    received: int = token_position.token.balanceOf(portfolio.user)
    if received > 0:
        deposit_in_pool(
            pool_contract=portfolio.pool_contract,
            token=token_position.token,
            amount=received,
        )
