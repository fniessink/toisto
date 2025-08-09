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
uv venv
. venv/bin/activate
uv pip install -e .[dev]
```

## How to test and check the quality

Run all tests and quality checks as follows:

```console
tools/test.sh
```

To also apply automated fixes where possible:

```console
tools/test.sh --fix
```

## How to profile

Make sure you have [Graphviz](https://graphviz.org) installed.

To invoke Toisto with the profiler, create the dot file, convert it to a PNG image, and open it, run:

```console
tools/profile.sh
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
uv build
```

Upload the distribution files to PyPI by running:

```console
uv publish
```

Tag the commit and push it:

```console
git tag vX.Y.Z
git push --tags
```

## How to keep dependencies up-to-date

Python dependencies are kept up-to-date via a Dependabot GitHub action that checks for updated dependencies and creates pull request automatically.

The [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry) needs to be copied into the repository by hand, from time to time.
