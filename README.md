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

Add `--help` or `-h` to get help information:

```console
 $ toisto --help
```

### Example session

```console
👋 Welcome to Toisto v0.0.2!

Practice as many words and phrases as you like, for as long as you like.
Hit Ctrl-C or Ctrl-D to quit.

Toisto tracks how many times you correctly translate words and phrases.
When you correctly translate a word or phrase multiple times in a row,
Toisto will not quiz you on it for a while. The more correct translations
in a row, the longer words and phrases are silenced.

Punainen
> rood
✅ Correct, 3 times in a row. I won't quiz you on this one for 8 minutes.

Grijs
> harmaa
✅ Correct, 4 times in a row. I won't quiz you on this one for 13 minutes.

Keltainen
> geel
✅ Correct, 6 times in a row. I won't quiz you on this one for 36 minutes.

Violetti
> roze
❌ Incorrect. The correct answer is "Paars".
```

### How it works

Toisto presents words and phrases in Dutch and Finnish for you to translate. For each word or phrase, Toisto counts how often you translate it correclty in a row. So each word or phrase has its own streak. Words and phrases with the lowest streak are presented to you first. When you translate a word or phrase correctly, increasing its streak, Toisto will silence the word for a while. The longer the streak, the longer a word or phrase is silenced.

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
    {"fi": "Terve", "nl": ["Hoi", "Hallo"]},
    {"fi": "Tervetuloa", "nl": "Welkom"}
]
```

Each deck is a list of entries. Each entry is a mapping with exactly two language key-value pairs. The key is a language identifier. Currently only "fi" for Finnish and "nl" for Dutch are supported. Each language identifier has a value which is either a string or a list of strings. The values are words, phrases, or sentences in the language indicated by the key.

Toisto quizzes the user in both directions, Finnish-Dutch and Dutch-Finnish. If the language value is a list, Toisto only uses the first item as question, but uses all values to check answers. So when quizzing Finnish-Dutch, both "Hoi" and "Hello" are accepted as answer to "Terve". But when quizzing Dutch-Finnish only "Hoi" is used as question.

### Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many words the user wants to practice per session or per day. It only keeps track of how many times in a row a specific word or phrases is translated correctly. When a word or phrases is translated correctly twice or more in a row, the word is silenced for a while. The longer the streak, the longer the word is silenced. The exact amount is determined by a S-curve with a maximum value of 90 days. Whenever the user makes a mistake the streak is reset to 0.
