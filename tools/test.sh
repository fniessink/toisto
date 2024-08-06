#/bin/bash

green -r

if [[ "$1" == "--fix" ]]; then
    ruff check --fix .
    ruff format .
else
    ruff check .
    ruff format --check .
fi

mypy src tests tools

vulture --exclude venv .

if [[ "$1" == "--fix" ]]; then
    fixit fix .
else
    fixit lint .
fi

bandit --quiet -r src tests tools

if [[ "$1" == "--fix" ]]; then
    python tools/format_json.py
else
    python tools/format_json.py --check-only
fi
