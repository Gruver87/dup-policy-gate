from __future__ import annotations

import json
from pathlib import Path

from policy_gate.audit import append_decision
from policy_gate.cli import main
from policy_gate.engine import evaluate_intent
from policy_gate.models import OrderIntent


def test_cli_status() -> None:
    assert main(["status"]) == 0


def test_cli_evaluate_allow() -> None:
    intent = json.dumps(
        {
            "symbol": "ETHUSDT",
            "side": "buy",
            "market": "spot",
            "sector": "spot_alts",
            "quote_usdt_micros": 500000,
            "dry_run": True,
        }
    )
    assert main(["evaluate", intent, "--assume-keys", "no"]) == 0


def test_cli_evaluate_refuse_futures() -> None:
    intent = json.dumps(
        {"symbol": "ETHUSDT", "side": "buy", "market": "futures", "dry_run": True}
    )
    assert main(["evaluate", intent, "--assume-keys", "no"]) == 1


def test_audit_write(tmp_path: Path) -> None:
    d = evaluate_intent(
        OrderIntent.from_dict(
            {
                "symbol": "AAAUSDT",
                "side": "sell",
                "market": "spot",
                "dry_run": True,
            }
        ),
        keys_present=False,
    )
    path = tmp_path / "policy.jsonl"
    append_decision(d, path)
    text = path.read_text(encoding="utf-8")
    assert "AAAUSDT" in text
    assert "secret" not in text.lower() or "api_key" not in text
