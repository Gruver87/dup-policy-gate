#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -e ".[dev]" -q
mkdir -p reports/demo
printf '%s\n' '{"symbol":"BTCUSDT","side":"buy","market":"spot","sector":"spot_alts","quote_usdt_micros":1000000,"dry_run":true}' > reports/demo/dry_spot.json
printf '%s\n' '{"symbol":"BTCUSDT","side":"buy","market":"futures","dry_run":true}' > reports/demo/futures.json
python -m policy_gate status
echo "== dry spot (expect ALLOW) =="
python -m policy_gate evaluate --file reports/demo/dry_spot.json --assume-keys no
echo "== futures (expect REFUSE) =="
set +e
python -m policy_gate evaluate --file reports/demo/futures.json --assume-keys no
rc=$?
set -e
if [[ "$rc" -ne 1 ]]; then
  echo "FAIL: futures should refuse with exit 1, got $rc" >&2
  exit 1
fi
echo "DEMO PASS"
