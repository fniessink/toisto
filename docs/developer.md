# Developer guide

The information below is aimed at people who (want to help) develop Toisto.

## How to prepare

Clone the repository:

```console
$ git clone https://github.com/fniessink/toisto.git
```

Create a virtual environment, activate it, and install Toisto in development mode, including development-only dependencies:

```console
$ cd toisto
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -e .[dev]
```

## How to test

Run the unit tests as follows:

```console
$ green
.........................................................................................................

Ran 105 tests in 0.483s using 8 processes

OK (passes=105)
```

To run the unit tests and get a coverage report, use:

```console
$ green -r
```

## How to check quality

Run mypy to check for typing issues:

```console
$ mypy src tests
Success: no issues found in 49 source files
```

Run Ruff to check for linting issues:

```console
$ ruff .
```

## How to format the source code

Run Black to format the code:

```console
$ black src tests
All done! ✨ 🍰 ✨
67 files left unchanged.
```

## How to release

Update the [changelog](../CHANGELOG.md)

Update the version number in [`pyproject.toml`](../pyproject.toml).

Create the distribution files by running:

```console
$ python -m build
```

Upload the distribution files to PyPI by running:

```console
$ twine upload dist/*
```

Tag the commit and push it:

```console
$ git tag vX.Y.Z
$ git push --tags
```

## How to keep dependencies up-to-date

Python dependencies are kept up-to-date via a Dependabot GitHub action that checks for updated dependencies and creates pull request automatically.

The [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry) needs to be copied into the repository by hand, from time to time.
