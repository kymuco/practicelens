.PHONY: install-dev install-api lint test check

install-dev:
	pip install -e .[dev]

install-api:
	pip install -e .[dev,api]

lint:
	ruff check .

test:
	pytest tests

check: lint test
