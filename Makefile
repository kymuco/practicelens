.PHONY: install-dev install-api lint test regression check

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
