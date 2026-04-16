---
name: bnbchain-mcp
description: BNB Chain MCP server — read-only blockchain data via MCP tools. Blocks, transactions, contracts, ERC20/NFT info, balances, network queries. Use when querying BNB Chain / opBNB / EVM data via MCP.
---

# BNB Chain MCP Skill (Read-Only)

Query BNB Chain / opBNB / EVM blockchain data via the BNB Chain MCP server. This skill covers read-only operations: blocks, transactions, contracts, tokens, NFTs, balances, and network info.

> **Note:** On-chain write operations (transfers, swaps, approvals) should use the platform's wallet and onchain execution flow, not this MCP server.

---

## Setup / Pre-flight Checks

Before using this skill, verify the `bnbchain-mcp` server is registered in your agent:

```bash
if command -v bnbchain-mcp &>/dev/null; then
  echo "bnbchain-mcp is available globally"
elif [ -f .mcp.json ] && grep -q '"bnbchain-mcp"' .mcp.json; then
  echo "bnbchain-mcp is configured in .mcp.json"
elif [ -f openclaw.json ] && grep -q '"bnbchain-mcp"' openclaw.json; then
  echo "bnbchain-mcp is pre-configured by the platform"
else
  echo "bnbchain-mcp is NOT configured — follow the Setup steps below"
fi
```

If it is **not configured**, install and register it:

1. **Install the package globally** (recommended):
   ```bash
   npm install -g @bnb-chain/mcp
   ```
2. **Register the MCP server** in your agent's MCP settings:
   - **Claude Code**: Add the following to your project root `.mcp.json` (or user settings):
     ```json
     {
       "mcpServers": {
         "bnbchain-mcp": {
           "command": "npx",
           "args": ["-y", "@bnb-chain/mcp@latest"]
         }
       }
     }
     ```
   - **Other agents** (Cursor, Windsurf, etc.): Copy the same `bnbchain-mcp` entry into your agent's MCP configuration panel.
3. **Reload**: After adding the config, restart or reload your agent so the MCP tools are discovered.

---

## MCP server config

The `bnbchain-mcp` server connects via stdio. No private key is needed for read-only use.

```json
{
  "mcpServers": {
    "bnbchain-mcp": {
      "command": "npx",
      "args": ["-y", "@bnb-chain/mcp@latest"]
    }
  }
}
```

---

## Network parameter

Most tools accept **`network`** (optional): chain name or ID, e.g. `bsc`, `opbnb`, `ethereum`, `base`. Default is `bsc`. Use **`get_supported_networks`** to list supported networks.

---

## Available tools

| Category | Tools |
|----------|-------|
| Blocks | `get_latest_block`, `get_block_by_number`, `get_block_by_hash` |
| Transactions | `get_transaction`, `get_transaction_receipt`, `estimate_gas` |
| Network | `get_chain_info`, `get_supported_networks` |
| Balances | `get_native_balance`, `get_erc20_balance` |
| Contracts | `read_contract`, `is_contract` |
| Tokens / NFT | `get_erc20_token_info`, `get_nft_info`, `get_erc1155_token_metadata`, `check_nft_ownership`, `get_nft_balance`, `get_erc1155_balance` |
| ERC-8004 (read) | `get_erc8004_agent`, `get_erc8004_agent_wallet` |

## MCP prompts

Use these when the user wants analysis or guidance:

- **analyze_block** — Analyze a block and its contents
- **analyze_transaction** — Analyze a specific transaction
- **analyze_address** — Analyze an EVM address
- **interact_with_contract** — Guidance on interacting with a smart contract
- **explain_evm_concept** — Explain an EVM concept
- **compare_networks** — Compare EVM-compatible networks
- **analyze_token** — Analyze an ERC20 or NFT token

---

## Reference files

| Reference | Content |
|-----------|---------|
| [references/evm-tools-reference.md](references/evm-tools-reference.md) | Blocks, transactions, network, wallet, contracts, tokens, NFT |
| [references/greenfield-tools-reference.md](references/greenfield-tools-reference.md) | Greenfield read operations |
| [references/prompts-reference.md](references/prompts-reference.md) | All MCP prompts and when to use them |

---

## Documentation

- **BNB Chain MCP repo:** https://github.com/bnb-chain/bnbchain-mcp
- **npm:** `npx @bnb-chain/mcp@latest`
