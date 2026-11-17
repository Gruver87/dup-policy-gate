"""CLI: evaluate / status / batch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from policy_gate import __version__
from policy_gate.audit import append_decision
from policy_gate.engine import PolicyEngine, load_policy
from policy_gate.keys import keys_status
from policy_gate.models import OrderIntent


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dup-policy-gate",
        description=(
            "Fail-closed spot-only policy gate before any order. "
            "Never places orders. Never prints secrets."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Policy JSON (default: configs/default_policy.json)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    st = sub.add_parser("status", help="Policy + key presence (booleans only)")
    _ = st

    ev = sub.add_parser("evaluate", help="Evaluate one intent JSON object")
    ev.add_argument(
        "intent",
        nargs="?",
        default=None,
        help="JSON string (or use --file)",
    )
    ev.add_argument("--file", type=Path, default=None)
    ev.add_argument("--audit", action="store_true", help="Append decision to audit log")
    ev.add_argument(
        "--audit-path",
        type=Path,
        default=None,
    )
    ev.add_argument(
        "--assume-keys",
        choices=("auto", "yes", "no"),
        default="auto",
        help="Override KuCoin key presence for tests",
    )

    batch = sub.add_parser("batch", help="Evaluate JSONL intents (one JSON object/line)")
    batch.add_argument("path", type=Path)
    batch.add_argument("--audit", action="store_true")
    return p


def _keys_flag(mode: str) -> bool | None:
    if mode == "auto":
        return None
    return mode == "yes"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy = load_policy(args.policy)
    engine = PolicyEngine(policy)

    if args.cmd == "status":
        out = {
            "tool_version": __version__,
            "policy": policy.to_dict(),
            "keys": keys_status(),
            "futures_auto": False,
            "note": "not financial advice; gate does not place orders",
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "evaluate":
        raw: str
        if args.file:
            raw = args.file.read_text(encoding="utf-8")
        elif args.intent:
            raw = args.intent
        else:
            print("provide intent JSON or --file", file=sys.stderr)
            return 2
        data = json.loads(raw)
        if not isinstance(data, dict):
            print("intent must be a JSON object", file=sys.stderr)
            return 2
        intent = OrderIntent.from_dict(data)
        decision = engine.evaluate(intent, keys_present=_keys_flag(args.assume_keys))
        if args.audit:
            append_decision(decision, args.audit_path)
        print(json.dumps(decision.to_dict(), indent=2, ensure_ascii=False))
        return 0 if decision.allowed else 1

    if args.cmd == "batch":
        lines = args.path.read_text(encoding="utf-8").splitlines()
        n_ok = 0
        n_fail = 0
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            intent = OrderIntent.from_dict(data)
            decision = engine.evaluate(intent)
            if args.audit:
                append_decision(decision, extra={"line": i})
            status = "ALLOW" if decision.allowed else "REFUSE"
            print(f"{i}\t{status}\t{intent.symbol}\t{';'.join(decision.reasons)}")
            if decision.allowed:
                n_ok += 1
            else:
                n_fail += 1
        print(f"batch done allow={n_ok} refuse={n_fail}")
        return 0 if n_fail == 0 else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
