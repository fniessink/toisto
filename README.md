# Toisto

Command-line app to practice languages. *Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

Toisto is alpha software at the moment. It comes with a limited set of words and phrases in Dutch, English, and Finnish.

## User guide

### How to install

Make sure you have these prequisities installed:

- MacOS (needed because Toisto uses the say command for text-to-speech),
- [Python 3.10 or newer](https://python.org), and
- [pipx](https://pypa.github.io/pipx/).

Install Toisto as follows:

```console
$ pipx install Toisto
```

### How to use

Start Toisto as follows, giving the language you want to practice and your language as arguments:

```console
$ toisto fi en
```

To practice a specific deck, pass it as follows:

```console
$ toisto fi en --deck colors
```

Add `--help` or `-h` to get help information:

```console
$ toisto --help
```

### Example session

```console
$ toisto fi nl
👋 Welcome to Toisto v0.0.5!

Practice as many words and phrases as you like, for as long as you like.
Hit Ctrl-C or Ctrl-D to quit.

Toisto tracks how many times you correctly translate words and phrases.
When you correctly translate a word or phrase multiple times in a row,
Toisto will not quiz you on it for a while. The more correct translations
in a row, the longer words and phrases are silenced.

Translate into Dutch:
Punainen
> rood
✅ Correct.

Translate into Dutch:
Harmaa
> bruin
⚠️ Incorrect. Please try again.
> grijs
✅ Correct.

Translate into Finnish:
Paars
> violetti
✅ Correct.

Translate into Finnish:
Groen
> virea
⚠️ Incorrect. Please try again.
> vihrea
❌ Incorrect. The correct answer is "Vihreä".
```

### How it works

Toisto presents words and phrases for you to translate. For each word or phrase, Toisto counts how often you translate it correctly in a row. So each word or phrase has its own streak. When you translate a word or phrase correctly, increasing its streak, Toisto will silence the word for a while. The longer the streak, the longer a word or phrase is silenced.

When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-progress.json` in your home folder.

## Developer guide

The information below is aimed at people who (want to help) develop Toisto.

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

Tag the commit and push it:

```console
$ git tag vX.Y.Z
$ git push --tags
```

## Software documentation

### Decks

Decks are located in `src/toisto/decks` in the form of JSON files. The format of the JSON files is as follows:

```json
[
    {"fi": "Viikonpäivät", "nl": "De dagen van de week"},
    {"fi": ["Mikä päivä tänään on?", "Mikä päivä on tänään?"], "nl": "Welke dag is het vandaag?"}
    {"singular": {"fi": "Päivä", "nl": "De dag"}, "plural": {"fi": "Päivät", "nl": "De dagen"}},
]
```

Each deck is a list of entries. There are two types of entries:
1. A translation entry. Translation entries are a mappings with exactly two language key-value pairs. The key is a language identifier. Currently "en" for English, "fi" for Finnish, and "nl" for Dutch are supported. Each language identifier has a value that is either a string or a list of strings. The values are words, phrases, or sentences in the language indicated by the key.
2. A noun entry. The entry is a mapping with `singular` and `plural` as keys and translation entries as values. It represents a noun with singular and plural versions in English, Finnish, and Dutch.

Toisto uses the entries to generate quizzes. Currently, two types of quizzes are generated:
1. Quizzes to translate a phrase from one language to another and vice versa. Toisto quizzes the user in both directions. If the language value is a list, Toisto uses all items as question and as answer. So both "Mikä päivä tänään on?" and "Mikä päivä on tänään?" are asked as question and both are accepted as correct answer for the quiz "Welke dag is het vandaag?"
2. Quizzes to singularize a plural noun or pluralize a singular noun. Users are only asked to singularize and pluralize nouns in their practice language, not their own language.

### Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many words the user wants to practice per session or per day. It only keeps track of how many times in a row a specific word or phrases is translated correctly. When a word or phrases is translated correctly twice or more in a row, the word is silenced for a while. The longer the streak, the longer the word is silenced. The exact amount is determined by a S-curve with a maximum value of 90 days. Whenever the user makes a mistake the streak is reset to 0.
