# Toisto

Command-line app to practice languages. *Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

Toisto is alpha software at the moment. It comes with a limited set of words and phrases in Dutch and Finnish.

## User guide

### How to install

Make sure you have these prequisities installed:

- MacOS (needed because Toista uses the say command for text-to-speech),
- [Python 3.10 or newer](https://python.org), and
- [pipx](https://pypa.github.io/pipx/).

Install Toista as follows:

```console
$ pipx install Toisto
```

### How to use

Start Toista as follows:

```console
 $ toisto
```

### Example session

```console
Welcome to 'Toisto' v0.0.1!

    Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
    Toisto tracks how many times you correctly translate words and phrases. The fewer times you have
    translated a word or phrase successfully, the more often it is presented for you to translate.

Negentig
> yhdeksänkymmentä
✅ Correct.

Kaksitoista
> twaalf
✅ Correct.

Zestien
> kuusitoista
✅ Correct.

Kuukaudet
> De maand
❌ Incorrect. The correct answer is "De maanden".
```

### How it works

Toisto presents words and phrases in Dutch and Finnish for you to translate. Words and phrases are sorted by 'progress'. When you translate a word or phrase correctly, its progress increases, otherwise it decreases. Words and phrases are sorted by progress so that the ones with the lowest score are presented to you first. When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-progress.json` in your home folder.

## Developer guide

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

### How to test

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

### How to check quality

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

## Software documentation

### Decks

Decks are located in `src/toisto/decks` in the form of JSON files. The format of the JSON files is as follows:

```json
[
    {"fi": "Terve", "nl": ["Hoi", "Hallo"]},
    {"fi": "Tervetuloa", "nl": "Welkom"}
]
```

Each deck is a list of entries. Each entry is a mapping with exactly two language key-value pairs. The key is a language identifier. Currently only "fi" for Finnish and "nl" for Dutch are supported. Each language identifier has a value which is either a string or a list of strings. The values are words, phrases, or sentences in the language indicated by the key.

Toisto quizzes the user in both directions, Finnish-Dutch and Dutch-Finnish. If the language value is a list, Toisto only uses the first item as question, but uses all values to check answers. So when quizzing Finnish-Dutch, both "Hoi" and "Hello" are accepted as answer to "Terve". But when quizzing Dutch-Finnish only "Hoi" is used as question.
