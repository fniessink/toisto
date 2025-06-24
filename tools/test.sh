#/bin/bash

uv run green -r

if [[ "$1" == "--fix" ]]; then
    uvx ruff check --fix .
    uvx ruff format .
else
    uvx ruff check .
    uvx ruff format --check .
fi

uvx mypy --python-executable=.venv/bin/python src tests tools

uvx vulture --exclude .venv .

if [[ "$1" == "--fix" ]]; then
    uvx fixit fix .
else
    uvx fixit lint .
fi

uvx bandit --quiet -r src tests tools

if [[ "$1" == "--fix" ]]; then
    uv run --no-project --script tools/format_json.py
else
    uv run --no-project --script tools/format_json.py --check-only
fi
