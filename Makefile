.PHONY: install-dev install-api lint test regression check run-api build-package

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

build-package:
	python -m build

check: lint test
