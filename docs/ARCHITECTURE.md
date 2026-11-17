# Architecture — dup-policy-gate

**Org:** DUP Labs · **Role:** policy layer **before** any order

## Position in stack

```text
agent / operator intent
        ↓
  dup-policy-gate   ← YOU ARE HERE (refuse or allow)
        ↓
  dup-market-radar trade API / manual KuCoin spot
```

This package **never** places orders and **never** enables futures auto.

## Rules (v0.1)

| Rule | Effect |
|------|--------|
| FUTURES_BLOCK | refuse futures/perp markets and futures_* sectors |
| spot_only | market must be in `allowed_markets` |
| size cap | `quote_usdt_micros ≤ max` (default 5 USDT) |
| max positions | refuse buy if `open_positions ≥ max` |
| leverage | refuse `leverage > 1` |
| live keys | live (`dry_run=false`) requires KuCoin Spot env presence |
| ops_ready | live requires `ops_ready=true` |
| audit | optional JSONL — no secrets |

## Related

- [`dup-market-radar`](https://github.com/Gruver87/dup-market-radar) — execution host
- [`dup-radar-news-mcp`](https://github.com/Gruver87/dup-radar-news-mcp) — digests only
- [`dup-evidence-graph`](https://github.com/Gruver87/dup-evidence-graph) — ops_ready / soak claims
