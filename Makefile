.PHONY: help lint format fix check test install-dev clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install development dependencies
	pip3 install -e ".[dev]"

lint:  ## Run Ruff linting check
	python3 -m ruff check src/ tests/

format:  ## Run Ruff formatting check
	python3 -m ruff format --check src/ tests/

fix:  ## Run Ruff auto-fix for linting issues
	python3 -m ruff check --fix src/ tests/

format-fix:  ## Run Ruff formatting
	python3 -m ruff format src/ tests/

check: lint format  ## Run both linting and formatting checks

all: check  ## Run all checks (alias for check)

test:  ## Run tests with pytest
	python3 -m pytest tests/ -v --cov=src --cov-report=term-missing

test-html:  ## Run tests and generate HTML coverage report
	python3 -m pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/"

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
