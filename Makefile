.PHONY: install-dev install-api lint test test-fast test-regression regression check run-api build-package generate-demo-assets generate-evaluation-assets generate-evaluation-showcase

install-dev:
	pip install -e .[dev]

install-api:
	pip install -e .[dev,api]

lint:
	ruff check .

test:
	pytest tests

test-fast:
	pytest tests/unit tests/integration

test-regression:
	pytest tests/regression

regression: test-regression

check: lint test

run-api:
	uvicorn practicelens.api.app:app --reload

build-package:
	python -m build

generate-demo-assets:
	python tools/generate_demo_assets.py

generate-evaluation-assets:
	python tools/generate_evaluation_assets.py

generate-evaluation-showcase:
	python tools/generate_evaluation_showcase.py
