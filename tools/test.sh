#/bin/bash

export UV_PYTHON=3.11
CODE_FOLDERS="src tests tools"

uv sync --all-extras --quiet

uv run green -r tests

if [[ "$1" == "--fix" ]]; then
    uv run ruff format $CODE_FOLDERS
    uv run ruff check --fix $CODE_FOLDERS
else
    uv run ruff format --check $CODE_FOLDERS
    uv run ruff check $CODE_FOLDERS
fi

uv run mypy --python-executable=.venv/bin/python $CODE_FOLDERS

uv run vulture --exclude .venv $CODE_FOLDERS .vulture-whitelist.py

if [[ "$1" == "--fix" ]]; then
    uv run fixit fix $CODE_FOLDERS
else
    uv run fixit lint $CODE_FOLDERS
fi

uv run bandit --quiet -r $CODE_FOLDERS

if [[ "$1" == "--fix" ]]; then
    uv run troml suggest --fix
else
    uv run troml check
fi

if [[ "$1" == "--fix" ]]; then
    uv run pyproject-fmt pyproject.toml
else
    uv run pyproject-fmt --check pyproject.toml
fi

if [[ "$1" == "--fix" ]]; then
    uv run --no-project --script tools/format_json.py
else
    uv run --no-project --script tools/format_json.py --check-only
fi
