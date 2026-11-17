from __future__ import annotations

from policy_gate.engine import PolicyEngine, evaluate_intent, load_policy
from policy_gate.models import OrderIntent


def _spot_buy(**kwargs):
    base = dict(
        symbol="BTCUSDT",
        side="buy",
        market="spot",
        sector="spot_alts",
        quote_usdt_micros=1_000_000,
        open_positions=0,
        dry_run=True,
    )
    base.update(kwargs)
    return OrderIntent.from_dict(base)


def test_allow_dry_spot() -> None:
    d = evaluate_intent(_spot_buy(), keys_present=False)
    assert d.allowed


def test_refuse_futures_market() -> None:
    d = evaluate_intent(_spot_buy(market="futures"), keys_present=False)
    assert not d.allowed
    assert any("FUTURES_BLOCK" in r for r in d.reasons)


def test_refuse_futures_sector() -> None:
    d = evaluate_intent(_spot_buy(sector="futures_long"), keys_present=False)
    assert not d.allowed


def test_refuse_size_cap() -> None:
    policy = load_policy()
    d = evaluate_intent(
        _spot_buy(quote_usdt_micros=policy.max_quote_usdt_micros + 1),
        policy,
        keys_present=False,
    )
    assert not d.allowed
    assert any("size cap" in r for r in d.reasons)


def test_refuse_live_without_keys() -> None:
    d = evaluate_intent(
        _spot_buy(dry_run=False, ops_ready=True),
        keys_present=False,
    )
    assert not d.allowed
    assert any("keys" in r.lower() for r in d.reasons)


def test_refuse_live_without_ops_ready() -> None:
    d = evaluate_intent(
        _spot_buy(dry_run=False, ops_ready=False),
        keys_present=True,
    )
    assert not d.allowed
    assert any("ops_ready" in r for r in d.reasons)


def test_allow_live_with_keys_and_ops() -> None:
    d = evaluate_intent(
        _spot_buy(dry_run=False, ops_ready=True),
        keys_present=True,
    )
    assert d.allowed


def test_refuse_leverage() -> None:
    d = evaluate_intent(_spot_buy(leverage=5), keys_present=False)
    assert not d.allowed


def test_engine_wrapper() -> None:
    eng = PolicyEngine()
    assert eng.evaluate(_spot_buy(), keys_present=False).allowed
