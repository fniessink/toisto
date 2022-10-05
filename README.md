# Toisto

Command-line app to practice languages. *Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

Toisto is alpha software at the moment. It comes with a limited set of words and phrases in Dutch and Finnish.

## Prerequisites

MacOS (for the say command), [Python 3.10 or newer](https://python.org), and [pipx](https://pypa.github.io/pipx/).

## How to install

```console
$ pipx install Toisto
```

## How to use

Start the program as follows:

```console
 $ toisto
```

## Example session

```console
Welcome to 'Toisto'!
Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
Toisto tracks how many times you correctly translate words and phrases. The fewer times you have
translated a word or phrase successfully, the more often it is presented for you to translate.

Dertien
> Kolmetoista
✅ Correct.

Kolmetoista
> Dertien
✅ Correct.

Veertien
> Neljätoista
✅ Correct.

Neljätoista
> viertien
❌ Incorrect. The correct answer is "veertien".

Neljätoista
> veertien
✅ Correct.
```

## How it works

Toisto presents words and phrases in Dutch and Finnish for you to translate. Words and phrases are sorted by 'progress'. When you translate a word or phrase correctly, its progress increases, otherwise it decreases. Words and phrases are sorted by progress so that the ones with the lowest score are presented to you first. When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-progress.json` in your home folder.

## Developer guidelines

### How to prepare

Clone the repository:

```console
$ git clone https://github.com/fniessink/toisto.git
```

Create a virtual environment, activate it, install the dependencies and install Toisto in development mode:

```console
$ cd toisto
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements-dev.txt
$ pip install -e .
```

## How to test

Run the unit tests as follows:

```console
$ green
```

To get a coverage report, run:

```console
$ green -r
```

### How to release

Update the version number in `pyproject.toml`.

Create the distribution files by running:

```console
$ python -m build
```

Upload the distribution files to PyPI by running:

```console
$ twine upload dist/*
```
