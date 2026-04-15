.PHONY: install-dev install-api lint test regression check run-api build-package generate-demo-assets

install-dev:
	pip install -e .[dev]

install-api:
	pip install -e .[dev,api]

lint:
	ruff check .

test:
	pytest tests

regression:
	pytest tests/regression

check: lint test

run-api:
	uvicorn practicelens.api.app:app --reload

build-package:
	python -m build

generate-demo-assets:
	python tools/generate_demo_assets.py
