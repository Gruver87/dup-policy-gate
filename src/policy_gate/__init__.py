"""DUP Policy Gate — fail-closed spot-only checks before any order."""

from __future__ import annotations

__version__ = "0.1.0"

from policy_gate.engine import PolicyEngine, evaluate_intent
from policy_gate.models import Decision, OrderIntent, PolicyConfig

__all__ = [
    "__version__",
    "Decision",
    "OrderIntent",
    "PolicyConfig",
    "PolicyEngine",
    "evaluate_intent",
]
