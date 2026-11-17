"""Intent / decision / config types — integer money only."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class DecisionCode(StrEnum):
    ALLOW = "allow"
    REFUSE = "refuse"


@dataclass(frozen=True)
class OrderIntent:
    """Proposed order — never executed by this package."""

    symbol: str
    side: str  # buy | sell
    market: str = "spot"  # spot | futures | margin | ...
    sector: str | None = None
    quote_usdt_micros: int = 0
    open_positions: int = 0
    dry_run: bool = True
    leverage: int | None = None
    ops_ready: bool | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrderIntent:
        return cls(
            symbol=str(data.get("symbol") or "").strip().upper(),
            side=str(data.get("side") or "").strip().lower(),
            market=str(data.get("market") or "spot").strip().lower(),
            sector=(
                str(data["sector"]).strip().lower()
                if data.get("sector") is not None
                else None
            ),
            quote_usdt_micros=int(data.get("quote_usdt_micros") or 0),
            open_positions=int(data.get("open_positions") or 0),
            dry_run=bool(data.get("dry_run", True)),
            leverage=int(data["leverage"]) if data.get("leverage") is not None else None,
            ops_ready=(
                bool(data["ops_ready"]) if data.get("ops_ready") is not None else None
            ),
            notes=str(data.get("notes") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Decision:
    code: DecisionCode
    reasons: tuple[str, ...]
    intent: OrderIntent
    policy_version: int = 1

    @property
    def allowed(self) -> bool:
        return self.code is DecisionCode.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "code": self.code.value,
            "reasons": list(self.reasons),
            "intent": self.intent.to_dict(),
            "policy_version": self.policy_version,
            "futures_auto": False,
            "note": "policy check only — does not place orders; not financial advice",
        }


@dataclass
class PolicyConfig:
    version: int = 1
    spot_only: bool = True
    allowed_markets: tuple[str, ...] = ("spot",)
    allowed_sectors: tuple[str, ...] = ("spot_alts", "memes", "listings")
    blocked_sectors: tuple[str, ...] = ("futures", "futures_long", "futures_short")
    max_quote_usdt_micros: int = 5_000_000  # 5 USDT
    max_open_positions: int = 2
    require_dry_run_without_keys: bool = True
    require_ops_ready_for_live: bool = True
    refuse_leverage: bool = True
    futures_auto: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyConfig:
        return cls(
            version=int(data.get("version") or 1),
            spot_only=bool(data.get("spot_only", True)),
            allowed_markets=tuple(
                str(x).lower() for x in (data.get("allowed_markets") or ["spot"])
            ),
            allowed_sectors=tuple(
                str(x).lower()
                for x in (
                    data.get("allowed_sectors") or ["spot_alts", "memes", "listings"]
                )
            ),
            blocked_sectors=tuple(
                str(x).lower()
                for x in (
                    data.get("blocked_sectors")
                    or ["futures", "futures_long", "futures_short"]
                )
            ),
            max_quote_usdt_micros=int(
                data.get("max_quote_usdt_micros") or 5_000_000
            ),
            max_open_positions=int(data.get("max_open_positions") or 2),
            require_dry_run_without_keys=bool(
                data.get("require_dry_run_without_keys", True)
            ),
            require_ops_ready_for_live=bool(
                data.get("require_ops_ready_for_live", True)
            ),
            refuse_leverage=bool(data.get("refuse_leverage", True)),
            futures_auto=False,  # never true
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["allowed_markets"] = list(self.allowed_markets)
        d["allowed_sectors"] = list(self.allowed_sectors)
        d["blocked_sectors"] = list(self.blocked_sectors)
        d["futures_auto"] = False
        return d


FUTURES_MARKETS = frozenset(
    {"futures", "future", "perp", "perps", "swap", "perpetual", "usdm", "coinm"}
)
