# Developer guide

The information below is aimed at people who (want to help) develop Toisto.

## How to prepare

Clone the repository:

```console
git clone https://github.com/fniessink/toisto.git
```

Create a virtual environment, activate it, and install Toisto in development mode, including development-only dependencies:

```console
cd toisto
python3 -m venv venv
. venv/bin/activate
pip install -e .[dev]
```

## How to test

Run the unit tests as follows:

```console
green
```

To run the unit tests and get a coverage report, use:

```console
green -r
```

## How to check quality

Run mypy to check for typing issues:

```console
mypy src tests
```

Run Ruff to check for linting issues:

```console
ruff check .
```

Run Ruff to check for formatting issues:

```console
ruff format --check .
```

Run vulture to check for dead code:

```console
vulture src tests
```

Run mutmut to check for unit test quality:

```console
$ mutmut run
```

## How to format the source code

Run Ruff to format the code:

```console
ruff format .
```

## How to release

Create a branch.

Update the [changelog](../CHANGELOG.md).

Update the version number in [`pyproject.toml`](../pyproject.toml).

Commit and push the changes and merge the branch.

Clean up old build and dist files:

```console
rm -rf build dist
```

Create the distribution files by running:

```console
python -m build
```

Upload the distribution files to PyPI by running:

```console
twine upload dist/*
```

> [!IMPORTANT]
> If twine fails with `ImportError: cannot import name 'appengine' from 'requests.packages.urllib3.contrib'`, this can be fixed by running `pip install --upgrade twine requests-toolbelt`.

Tag the commit and push it:

```console
git tag vX.Y.Z
git push --tags
```

## How to keep dependencies up-to-date

Python dependencies are kept up-to-date via a Dependabot GitHub action that checks for updated dependencies and creates pull request automatically.

The [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry) needs to be copied into the repository by hand, from time to time.
