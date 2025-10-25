#/bin/bash

export UV_PYTHON=3.11

uv run green -r tests

if [[ "$1" == "--fix" ]]; then
    uvx ruff format src tests tools
    uvx ruff check --fix src tests tools
else
    uvx ruff format --check src tests tools
    uvx ruff check src tests tools
fi

uvx mypy --python-executable=.venv/bin/python src tests tools

uvx vulture --exclude .venv src tests tools .vulture-whitelist.py

if [[ "$1" == "--fix" ]]; then
    uvx fixit fix src tests tools
else
    uvx fixit lint src tests tools
fi

uvx bandit --quiet -r src tests tools

if [[ "$1" == "--fix" ]]; then
    uv run --no-project --script tools/format_json.py
else
    uv run --no-project --script tools/format_json.py --check-only
fi
