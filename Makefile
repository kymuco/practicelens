.PHONY: install-dev install-api lint test regression check run-api

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

run-api:
	uvicorn practicelens.api.app:app --reload

check: lint test
