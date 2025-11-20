set positional-arguments

export UV_PYTHON := `cat .python-version`

_default:
  @just --list

code_folders := "src tests tools"

# Sync the dependencies with the lock file
@uv-sync:
    uv sync --locked --all-extras --quiet

# Run the unit tests, pass 'cov' to also check the test coverage
test *cov: uv-sync
    uv run green {{ if cov == "cov" { "-r " } else { "" } }}tests

# Check the code for typing issues
ty: uv-sync
    uv run ty check {{code_folders}}

# Check the code for typing issues
mypy: uv-sync
    uv run mypy --python-executable=.venv/bin/python {{code_folders}}

# Run the type checkers
type-check: ty mypy

# Check the code for dead code
vulture: uv-sync
    uv run vulture --exclude .venv {{code_folders}} .vulture-whitelist.py

# Check the code for formatting and quality issues, pass 'fix' to also fix issues
ruff *fix: uv-sync
    uv run ruff format {{ if fix == "fix" { "" } else { "--check " } }}{{code_folders}}
    uv run ruff check {{ if fix == "fix" { "--fix " } else { "" } }}{{code_folders}}

# Check the code for quality issues, pass 'fix' to also fix issues
fixit *fix: uv-sync
    uv run fixit {{ if fix == "fix" { "fix" } else { "lint"} }} {{code_folders}}

# Check the classifiers in pyproject.toml, pass 'fix' to also fix issues
troml *fix: uv-sync
    uv run troml {{ if fix == "fix" { "suggest --fix" } else { "check"} }}

# Check the format of pyproject.toml, pass 'fix' to also fix issues
pyproject-fmt *fix: uv-sync
    uv run pyproject-fmt {{ if fix == "fix" { "" } else { "--check " } }}pyproject.toml

# Run the linters, pass 'fix' to also fix issues
lint *fix: (ruff fix) (fixit fix) (troml fix) (pyproject-fmt fix)

# Check the code for security issues
bandit: uv-sync
    uv run bandit --quiet -r {{code_folders}}

# Check the formatting of JSON files
format-json *fix:
    uv run --no-project --script tools/format_json.py {{ if fix == "fix" { "" } else { "--check-only" } }}

# Run the formatters, linters, and checkers
quality: (lint) (type-check) (bandit) (vulture) (format-json)

# Run all checks
all: (test 'cov') (quality)

_sonarcloud:
    uv run coverage xml # SonarCloud needs a Cobertura compatible XML coverage report
    uv run python -m xmlrunner discover --output-file build/xunit.xml  # SonarCloud needs a JUnit compatible XML report

_ci: (test 'cov') (_sonarcloud) (quality)

profile:
    mkdir -p build
    python -m cProfile -o build/profile.out .venv/bin/toisto
    gprof2dot -f pstats build/profile.out > build/profile.dot
    dot -Tpng build/profile.dot > build/profile.png
    open build/profile.png
