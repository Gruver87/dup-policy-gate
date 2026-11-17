"""Policy evaluation — FUTURES_BLOCK, spot-only, size caps, live key gate."""

from __future__ import annotations

import json
from pathlib import Path

from policy_gate.keys import kucoin_spot_keys_present
from policy_gate.models import (
    FUTURES_MARKETS,
    Decision,
    DecisionCode,
    OrderIntent,
    PolicyConfig,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = PACKAGE_ROOT / "configs" / "default_policy.json"


def load_policy(path: Path | None = None) -> PolicyConfig:
    cfg_path = path or DEFAULT_POLICY
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("policy config must be a JSON object")
    return PolicyConfig.from_dict(data)


def evaluate_intent(
    intent: OrderIntent,
    policy: PolicyConfig | None = None,
    *,
    keys_present: bool | None = None,
) -> Decision:
    """Return ALLOW only when every rule passes. Never places an order."""
    policy = policy or load_policy()
    reasons: list[str] = []

    if not intent.symbol:
        reasons.append("missing symbol")
    if intent.side not in {"buy", "sell"}:
        reasons.append(f"invalid side={intent.side!r} (buy|sell)")

    market = (intent.market or "").lower()
    if market in FUTURES_MARKETS or market.startswith("future"):
        reasons.append("FUTURES_BLOCK: futures/perp market refused")
    if policy.spot_only and market not in policy.allowed_markets:
        reasons.append(f"spot_only: market={market!r} not allowed")

    sector = (intent.sector or "").lower() if intent.sector else None
    if sector:
        if sector in policy.blocked_sectors or sector.startswith("futures"):
            reasons.append(f"FUTURES_BLOCK: sector={sector!r}")
        elif sector not in policy.allowed_sectors:
            reasons.append(f"sector={sector!r} not in allowed_sectors")

    if intent.quote_usdt_micros < 0:
        reasons.append("quote_usdt_micros must be >= 0")
    if intent.quote_usdt_micros > policy.max_quote_usdt_micros:
        reasons.append(
            f"size cap: quote_usdt_micros={intent.quote_usdt_micros} "
            f"> max={policy.max_quote_usdt_micros}"
        )

    if intent.side == "buy" and intent.open_positions >= policy.max_open_positions:
        reasons.append(
            f"max_open_positions={policy.max_open_positions} reached "
            f"(open={intent.open_positions})"
        )

    if policy.refuse_leverage and intent.leverage is not None and intent.leverage > 1:
        reasons.append(f"leverage={intent.leverage} refused")

    if policy.futures_auto:
        reasons.append("misconfigured policy: futures_auto must be false")

    keys_ok = kucoin_spot_keys_present() if keys_present is None else keys_present
    if not intent.dry_run:
        if policy.require_dry_run_without_keys and not keys_ok:
            reasons.append(
                "live refused: KuCoin Spot keys not present in env "
                "(dry_run=true allowed without keys)"
            )
        if policy.require_ops_ready_for_live and intent.ops_ready is not True:
            reasons.append("live refused: ops_ready must be true")

    if reasons:
        return Decision(
            code=DecisionCode.REFUSE,
            reasons=tuple(reasons),
            intent=intent,
            policy_version=policy.version,
        )
    return Decision(
        code=DecisionCode.ALLOW,
        reasons=("all policy checks passed",),
        intent=intent,
        policy_version=policy.version,
    )


class PolicyEngine:
    def __init__(self, policy: PolicyConfig | None = None) -> None:
        self.policy = policy or load_policy()

    def evaluate(
        self,
        intent: OrderIntent,
        *,
        keys_present: bool | None = None,
    ) -> Decision:
        return evaluate_intent(intent, self.policy, keys_present=keys_present)
