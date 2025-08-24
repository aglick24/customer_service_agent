#!/bin/bash

# Ruff script for common formatting and linting tasks
# Usage: ./scripts/ruff.sh [check|format|fix|all]

set -e

case "${1:-all}" in
    "check")
        echo "🔍 Running Ruff linting check..."
        python3 -m ruff check src/ tests/
        ;;
    "format")
        echo "✨ Running Ruff formatting check..."
        python3 -m ruff format --check src/ tests/
        ;;
    "fix")
        echo "🔧 Running Ruff auto-fix..."
        python3 -m ruff check --fix src/ tests/
        ;;
    "format-fix")
        echo "🎨 Running Ruff format..."
        python3 -m ruff format src/ tests/
        ;;
    "all")
        echo "🚀 Running full Ruff check and format..."
        echo "🔍 Linting..."
        python3 -m ruff check src/ tests/
        echo "✨ Formatting..."
        python3 -m ruff format --check src/ tests/
        ;;
    *)
        echo "Usage: $0 [check|format|fix|format-fix|all]"
        echo "  check       - Run linting check only"
        echo "  format      - Run formatting check only"
        echo "  fix         - Run linting with auto-fix"
        echo "  format-fix  - Run formatting"
        echo "  all         - Run full check and format (default)"
        exit 1
        ;;
esac
