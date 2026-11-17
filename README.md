# DUP Policy Gate

[![ci](https://github.com/Gruver87/dup-policy-gate/actions/workflows/ci.yml/badge.svg)](https://github.com/Gruver87/dup-policy-gate/actions/workflows/ci.yml)

**Org:** [DUP Labs](https://github.com/Gruver87) · **Author:** Uladzimir Dabranski  
**Version:** `0.1.0` · Fail-closed **spot-only** policy before any order

Intent policy gate for agents that may spend money or change risk. Pattern is reusable
beyond crypto (caps, market-mode blocks, audit JSONL). First stand: Market Radar spot-only.

Checks intents. Does **not** place orders. **FUTURES_BLOCK** always.  
Live without KuCoin Spot keys in env → **refuse** (dry_run still allowed).

| Related | Role |
|---------|------|
| [`dup-market-radar`](https://github.com/Gruver87/dup-market-radar) | Spot ops / trade API |
| [`dup-evidence-graph`](https://github.com/Gruver87/dup-evidence-graph) | ops_ready / soak honesty |
| [`dup-radar-news-mcp`](https://github.com/Gruver87/dup-radar-news-mcp) | Digests (no orders) |

## Quick demo

```bash
make demo
# or: bash scripts/demo.sh
# Windows: .\scripts\demo_policy.ps1
```

## Install

```bash
python -m pip install -e ".[dev]"
make test   # or: .\scripts\test_all.ps1
```

## CLI

```bash
python -m policy_gate status
python -m policy_gate evaluate --file intent.json --assume-keys no
```

Exit `0` = ALLOW · `1` = REFUSE.

## MCP

See [`mcp.json`](mcp.json) — tools `policy_status`, `policy_check_order`, `policy_check_json`.

## License

MIT — [`LICENSE`](LICENSE).
