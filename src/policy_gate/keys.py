"""Env key presence checks — never print secret values."""

from __future__ import annotations

import os

KUCOIN_KEY_NAMES = (
    "KUCOIN_API_KEY",
    "KUCOIN_API_SECRET",
    "KUCOIN_API_PASSPHRASE",
)


def env_present(name: str) -> bool:
    v = os.environ.get(name)
    return bool(v and str(v).strip())


def kucoin_spot_keys_present() -> bool:
    return all(env_present(n) for n in KUCOIN_KEY_NAMES)


def keys_status() -> dict[str, bool | str]:
    """Boolean presence map only — no secret material."""
    return {
        "kucoin_spot_keys_present": kucoin_spot_keys_present(),
        "radar_api_key_present": env_present("RADAR_API_KEY"),
        "checked": list(KUCOIN_KEY_NAMES) + ["RADAR_API_KEY"],
        "note": "presence only — values never returned",
    }
