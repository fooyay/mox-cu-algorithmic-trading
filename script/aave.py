import boa

REFERRAL_CODE = 0


def deposit(pool_contract, token, amount):
    allowed_amount = token.allowance(boa.env.eoa, pool_contract.address)
    if allowed_amount < amount:
        token.approve(pool_contract.address, amount)
    print(
        f"Depositing {amount} of token {token.name()} to Aave Pool {pool_contract.address}..."
    )
    pool_contract.supply(token.address, amount, boa.env.eoa, REFERRAL_CODE)
