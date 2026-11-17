.PHONY: install test demo lint

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	python -m ruff check src tests

demo: install
	python -m policy_gate status
	@mkdir -p reports/demo
	@printf '%s\n' '{"symbol":"BTCUSDT","side":"buy","market":"spot","sector":"spot_alts","quote_usdt_micros":1000000,"dry_run":true}' > reports/demo/dry_spot.json
	@printf '%s\n' '{"symbol":"BTCUSDT","side":"buy","market":"futures","dry_run":true}' > reports/demo/futures.json
	python -m policy_gate evaluate --file reports/demo/dry_spot.json --assume-keys no
	python -m policy_gate evaluate --file reports/demo/futures.json --assume-keys no; test $$? -eq 1
