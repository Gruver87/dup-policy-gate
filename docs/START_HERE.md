# Start here (plain language)

**What:** a small library/CLI that answers: “is this trade intent allowed?”  
**Hard rule:** futures / leverage intents are **blocked** (`FUTURES_BLOCK`).

**Not:** a trading bot. It does not place orders.

```powershell
cd dup-policy-gate
python -m pip install -e ".[dev]"
.\scripts\demo_policy.ps1   # or: make demo
```

Use it before any auto-order path (Radar / agents) so futures cannot sneak in.

RU: это «шлагбаум» — спот можно, фьючерсы автоматом нет. Демо без ключей биржи.
