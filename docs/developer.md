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
just all
```

To also apply automated fixes where possible:

```console
just all fix
```

## How to profile

Make sure you have [Graphviz](https://graphviz.org) installed.

To invoke Toisto with the profiler, create the dot file, convert it to a PNG image, and open it, run:

```console
just profile
```

## How to run mutation tests

To run the mutation test:

```console
mutmut run
```

If mutmut fails to run the 'clean tests', simply restart `mutmut run`.

To browse the results:

```console
mutmut browse
```

## How to release

Create a branch.

Update the version number in:

- the [changelog](../CHANGELOG.md),
- [`pyproject.toml`](../pyproject.toml), and
- [`sonar-project.properties`](../sonar-project.properties).

Update `uv.lock` by running:

```console
uv lock
```

Commit and push the changes and merge the branch.

Create and upload the distribution files to PyPI and tag and push the commit by running:

```console
just publish
```

## How to keep dependencies up-to-date

Python dependencies are kept up-to-date via a Dependabot GitHub action that checks for updated dependencies and creates pull request automatically.

The [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry) needs to be copied into the repository by hand, from time to time.
