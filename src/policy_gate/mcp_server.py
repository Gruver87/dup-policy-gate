"""MCP stdio — policy check tools (no order placement)."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from policy_gate import __version__
from policy_gate.audit import append_decision
from policy_gate.engine import PolicyEngine, load_policy
from policy_gate.keys import keys_status
from policy_gate.models import OrderIntent

mcp = FastMCP("dup-policy-gate")
_engine = PolicyEngine(load_policy())


@mcp.tool()
def policy_status() -> str:
    """Policy config + key presence booleans (no secrets)."""
    return json.dumps(
        {
            "ok": True,
            "tool_version": __version__,
            "policy": _engine.policy.to_dict(),
            "keys": keys_status(),
            "futures_auto": False,
            "note": "not financial advice; does not place orders",
        },
        ensure_ascii=False,
    )


@mcp.tool()
def policy_check_order(
    symbol: str,
    side: str,
    market: str = "spot",
    sector: str | None = None,
    quote_usdt_micros: int = 0,
    open_positions: int = 0,
    dry_run: bool = True,
    leverage: int | None = None,
    ops_ready: bool | None = None,
    audit: bool = False,
) -> str:
    """Evaluate an order intent against FUTURES_BLOCK / size caps. Never places orders."""
    intent = OrderIntent(
        symbol=symbol,
        side=side,
        market=market,
        sector=sector,
        quote_usdt_micros=int(quote_usdt_micros),
        open_positions=int(open_positions),
        dry_run=bool(dry_run),
        leverage=leverage,
        ops_ready=ops_ready,
    )
    decision = _engine.evaluate(intent)
    if audit:
        append_decision(decision)
    return json.dumps(decision.to_dict(), ensure_ascii=False, default=str)


@mcp.tool()
def policy_check_json(intent_json: str, audit: bool = False) -> str:
    """Evaluate a full intent JSON object string."""
    try:
        data: Any = json.loads(intent_json)
    except json.JSONDecodeError as exc:
        return json.dumps({"allowed": False, "error": f"invalid json: {exc}"})
    if not isinstance(data, dict):
        return json.dumps({"allowed": False, "error": "intent must be object"})
    decision = _engine.evaluate(OrderIntent.from_dict(data))
    if audit:
        append_decision(decision)
    return json.dumps(decision.to_dict(), ensure_ascii=False, default=str)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
