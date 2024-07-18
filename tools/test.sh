#/bin/bash

green -r; ruff check .; ruff format --check .; mypy src tests tools; vulture src tests tools; fixit lint .; bandit -r src tests tools; python tools/format_json.py --check-only
