"""Append-only JSONL audit of policy decisions — no secrets."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from policy_gate.models import Decision

DEFAULT_AUDIT = Path(__file__).resolve().parents[2] / "data" / "audit" / "policy.jsonl"
MAX_LINE = 16_384


def append_decision(
    decision: Decision,
    path: Path | None = None,
    *,
    extra: dict[str, Any] | None = None,
) -> Path:
    out = path or DEFAULT_AUDIT
    out.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "ts_ms": int(time.time() * 1000),
        "decision": decision.to_dict(),
    }
    if extra:
        # Strip anything that looks like a secret key name
        safe = {
            k: v
            for k, v in extra.items()
            if not any(
                s in str(k).lower()
                for s in ("secret", "passphrase", "password", "token", "api_key")
            )
        }
        record["extra"] = safe
    line = json.dumps(record, ensure_ascii=False, default=str)
    if len(line) > MAX_LINE:
        line = json.dumps(
            {
                "ts_ms": record["ts_ms"],
                "error": "audit_line_too_long",
                "allowed": decision.allowed,
            },
            ensure_ascii=False,
        )
    with out.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return out
