set positional-arguments

export UV_PYTHON := `cat .python-version`

_default:
  @just --list

code_folders := "src tests tools"

# Sync the dependencies with the lock file
@uv-sync:
    uv sync --locked --all-extras --quiet

# Run the unit tests. Pass 'cov' to also check the test coverage.
test *cov: uv-sync
    uv run green {{ if cov == "cov" { "-r " } else { "" } }}tests

# Check the code for formatting and quality issues. Pass 'fix' to also fix issues.
ruff *fix: uv-sync
    uv run ruff format {{ if fix == "fix" { "" } else { "--check " } }}{{code_folders}}
    uv run ruff check {{ if fix == "fix" { "--fix " } else { "" } }}{{code_folders}}

# Check the code for quality issues. Pass 'fix' to also fix issues.
fixit *fix: uv-sync
    uv run fixit {{ if fix == "fix" { "fix" } else { "lint"} }} {{code_folders}}

# Check the classifiers in pyproject.toml. Pass 'fix' to also fix issues.
troml *fix: uv-sync
    uv run troml {{ if fix == "fix" { "suggest --fix" } else { "check"} }}

# Check the format of pyproject.toml. Pass 'fix' to also fix issues.
pyproject-fmt *fix: uv-sync
    uv run pyproject-fmt {{ if fix == "fix" { "" } else { "--check " } }}pyproject.toml

# Check the formatting of JSON files. Pass 'fix' to also fix issues.
format-json *fix:
    uv run --no-project --script tools/format_json.py {{ if fix == "fix" { "" } else { "--check-only" } }}

# Run the linters. Pass 'fix' to also fix issues.
lint *fix: (ruff fix) (fixit fix) (troml fix) (pyproject-fmt fix) (format-json fix)

# Check the code for typing issues
ty: uv-sync
    uv run ty check {{code_folders}}

# Check the code for typing issues
mypy: uv-sync
    uv run mypy --python-executable=.venv/bin/python {{code_folders}}

# Run the type checkers
type-check: ty mypy

# Check the code for security issues
bandit: uv-sync
    uv run bandit --quiet -r {{code_folders}}

# Check the code for dead code
vulture: uv-sync
    uv run vulture --exclude .venv {{code_folders}} .vulture-whitelist.py

# Run the formatters, linters, and checkers. Pass 'fix' to also fix issues.
quality *fix: (lint fix) (type-check) (bandit) (vulture)

# Run all checks. Pass 'fix' to also fix issues
all *fix: (test 'cov') (quality fix)

_sonarcloud:
    uv run coverage xml # SonarCloud needs a Cobertura compatible XML coverage report
    uv run python -m xmlrunner discover --output-file build/xunit.xml  # SonarCloud needs a JUnit compatible XML report

_ci: (test 'cov') (_sonarcloud) (quality)

# Build and publish the distribution packages.
publish:
    rm -rf build dist
    uv build
    uv publish
    git tag v`python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"`
    git push --tags

# Profile the code.
profile:
    mkdir -p build
    python -m cProfile -o build/profile.out .venv/bin/toisto
    gprof2dot -f pstats build/profile.out > build/profile.dot
    dot -Tpng build/profile.dot > build/profile.png
    open build/profile.png
