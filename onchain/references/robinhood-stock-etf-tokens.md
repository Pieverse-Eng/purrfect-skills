# Robinhood Stock/ETF Tokens

Use this reference when a user asks for Robinhood Chain stock token or tokenized
ETF contract addresses, or wants to check balances for one of those assets.

These addresses are for Robinhood Chain only.

## Chain

| Chain | Chain ID | Explorer |
| --- | ---: | --- |
| Robinhood Chain | 4663 | `https://robinhoodchain.blockscout.com` |

## Usage Notes

- Treat these as token contract addresses, not stock trading advice.
- A token with the same ticker but a different contract address is not the
  canonical Robinhood Stock Token.
- The current `purr` CLI resolves these tickers on `--chain-id 4663`; prefer the
  ticker for common balance/transfer commands and use the raw address when a
  tool path requires an address.
- The Name column uses Robinhood Chain token metadata display names with the
  "Robinhood Token" suffix omitted.
- Do not reuse these addresses on other chains.

## Stock Tokens

| Ticker | Name | Token Address |
| --- | --- | --- |
| AAPL | Apple | `0xaF3D76f1834A1d425780943C99Ea8A608f8a93f9` |
| AMD | AMD | `0x86923f96303D656E4aa86D9d42D1e57ad2023fdC` |
| AMZN | Amazon | `0x12f190a9F9d7D37a250758b26824B97CE941bF54` |
| BABA | Alibaba | `0xad25Ac6C84D497db898fa1E8387bf6Af3532a1c4` |
| BE | Bloom Energy | `0x822CC93fFD030293E9842c30BBD678F530701867` |
| COIN | Coinbase | `0x6330D8C3178a418788dF01a47479c0ce7CCF450b` |
| CRCL | Circle Internet Group | `0xdF0992E440dD0be65BD8439b609d6D4366bf1CB5` |
| CRWV | CoreWeave | `0x5f10A1C971B69e47e059e1dC91901B59b3fB49C3` |
| GOOGL | Alphabet Class A | `0x2e0847E8910a9732eB3fb1bb4b70a580ADAD4FE3` |
| INTC | Intel | `0xc72b96e0E48ecd4DC75E1e45396e26300BC39681` |
| META | Meta Platforms | `0xc0D6457C16Cc70d6790Dd43521C899C87ce02f35` |
| MSFT | Microsoft | `0xe93237C50D904957Cf27E7B1133b510C669c2e74` |
| MU | Micron Technology | `0xfF080c8ce2E5feadaCa0Da81314Ae59D232d4afD` |
| NVDA | NVIDIA | `0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC` |
| ORCL | Oracle | `0xb0992820E760d836549ba69BC7598b4af75dEE03` |
| PLTR | Palantir Technologies | `0x894E1EC2D74FFE5AEF8Dc8A9e84686acCB964F2A` |
| SNDK | Sandisk Corporation | `0xB90A19fF0Af67f7779afF50A882A9CfF42446400` |
| SPCX | Space Exploration Technologies Corp | `0x4a0E65A3EcceC6dBe60AE065F2e7bb85Fae35eEa` |
| TSLA | Tesla | `0x322F0929c4625eD5bAd873c95208D54E1c003b2d` |
| USAR | USA Rare Earth | `0xd917B029C761D264c6A312BBbcDA868658eF86a6` |

## Tokenized ETFs

| Ticker | Name | Token Address |
| --- | --- | --- |
| QQQ | Invesco QQQ | `0xD5f3879160bc7c32ebb4dC785F8a4F505888de68` |
| SGOV | iShares 0-3 Month Treasury Bond ETF | `0x92FD66527192E3e61d4DDd13322Aa222DE86F9B5` |
| SLV | iShares Silver Trust | `0x411eFb0E7f985935DAec3D4C3ebaEa0d0AD7D89f` |
| SPY | SPDR S&P 500 ETF Trust | `0x117cc2133c37B721F49dE2A7a74833232B3B4C0C` |
| USO | United States Oil Fund | `0xa30FA36Db767ad9eD3f7a60fC79526fB4d56D344` |

## Examples

```bash
purr wallet balance --chain-id 4663 --token NVDA
purr wallet balance --chain-id 4663 --token SPY
purr wallet balance --chain-id 4663 --token 0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC  # raw NVDA address
```
