# Algorithmic Trading Project

🐍 Welcome to Algorithmic Trading!

## Quickstart

1. Deploy to a fake local network that titanoboa automatically spins up!

```bash
mox run deploy
```

2. Run tests

```bash
mox test
```

### EXPLORER_API_KEY needed
To create the ABI files, you will need to set up an API key for Etherscan.
You can get one for free at https://etherscan.io/myapikey. Once you have your
API key, expose it as an enviroment variable, "EXPLORER_API_KEY".

### ABIs needed
To create the ABI files, you can use mox explorer. However, you'll need the
EXPLORER_API_KEY environment variable set up to do this. Once you have your
API key, run a command like this, using the address of the token:

```bash
mox explorer get 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 --save --name usdc
```

## Game Plan
- [ ] Deposit into Aave
- [ ] Withdraw from Aave
- [ ] Trade tokens through Uniswap

The idea is to maintain a 70/30 ratio of tokens in the portfolio,
and rebalance when the ratio deviates by more than 5%.

_For documentation, please run `mox --help` or visit [the Moccasin documentation](https://cyfrin.github.io/moccasin)_
