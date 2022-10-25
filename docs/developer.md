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
.................

Ran 17 tests in 0.305s using 8 processes

OK (passes=17)
```

To run the unit tests and get a coverage report, use:

```console
$ green -r
```

## How to check quality

Run mypy to check for typing issues:

```console
$ mpypy src tests
Success: no issues found in 12 source files
```

Run Pylint to check for linting issues:

```console
$ pylint src tests

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
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
