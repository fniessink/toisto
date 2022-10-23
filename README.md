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

To practice a specific topic, pass it as follows:

```console
$ toisto fi en --topic colors
```

Add `--help` or `-h` to get help information:

```console
$ toisto --help
```

### Example sessions

![gif](https://raw.githubusercontent.com/fniessink/toisto/main/docs/demo.gif)

```console
$ toisto fi nl
👋 Welcome to Toisto v0.0.7!

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

Create a virtual environment, activate it, and install Toisto in development mode, including development-only dependencies:

```console
$ cd toisto
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -e .[dev]
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

### Topics

Builtin topics are located in `src/toisto/topics` in the form of JSON files. Users can also create their own topic files as long as it complies with the description below and pass them to Toisto using the `-t/--topic-file` command-line option.

Each topic is a list of *concepts* with *labels* in different languages. A concept can be anything that can be expressed in language. The labels are words, phrases, or sentences that express the concept in a specific language.

The format of the JSON files is as follows:

```json
[
    {
        "en": "Days of the week",
        "fi": "Viikonpäivät",
        "nl": "De dagen van de week"
    },
    {
        "en": "What day is it today?",
        "fi": [
            "Mikä päivä tänään on?",
            "Mikä päivä on tänään?"
        ],
        "nl": "Welke dag is het vandaag?"
    },
    {
        "singular": {
            "en": "Day",
            "fi": "Päivä",
            "nl": "De dag"
        },
        "plural": {
            "en": "Days",
            "fi": "Päivät",
            "nl": "De dagen"
        }
    }
]
```

Concepts are represented in the topic files as JSON mappings with language identifiers as keys and labels as values. Currently supported language identifiers are "en" for English, "fi" for Finnish, and "nl" for Dutch. Labels consist of either one string or a list of strings. A list of strings is used when there are multiple equivalent ways to express the concept in a language, as with "Mikä päivä tänään on?" and "Mikä päivä on tänään?" above.

When concepts can have both singular and plural forms, such as with most nouns, these are represented in the JSON as mappings with `singular` and `plural` as keys and concepts as values.

Sometimes a concept in one language can be two different concepts in another language. For example, both in English and Dutch there are separate greetings for the afternoon and the whole day: "Good afternoon" and "Good day" in English and "Goedemiddag" and "Goedendag" in Dutch. In Finnish "Hyvää päivää", or just "Päivää", is used for both. As an aside, "Hyvää iltapäivää", although grammatically correct, is not used.

If we would include all these labels in one concept, Toisto would consider "Goedemiddag" a correct transation of "Good day", which is undesirable. The solution is to distribute the labels over four different concepts:

- One concept with the labels "Goedemiddag" and "Good afternoon" and one concept with the labels "Goedendag" and "Good day", both without Finnish labels. This ensures that "Goedemiddag" is not considered to be a correct translation of "Good day".
- One concept with the Finnish labels "Hyvää päivää" and "Päivää" and with both Dutch labels, "Goedendag" and "Goedemiddag" and one concept with the Finnish labels "Hyvää päivää" and "Päivää" and with both English labels, "Good day" and "Good afternoon". This ensures that "Goedendag", "Goedemiddag", "Good day", and "Good afternoon" are all correct translations for "Hyvää päivää" and "Päivää". Unfortunately, We cannot put the English and Dutch labels in one concept with the Finnish labels because otherwise Toisto would still consider "Goedemiddag" to be a correct translation of "Good day".

In the topic file this looks as follows:

```json
[
    {
        "en": "Good day",
        "nl": "Goedendag"
    },
    {
        "en": "Good afternoon",
        "nl": "Goedemiddag"
    },
    {
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "en": [
            "Good afternoon",
            "Good day"
        ]
    },
    {
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "nl": [
            "Goedendag",
            "Goedemiddag"
        ]
    }
]
```

Toisto uses the concepts to generate quizzes. Currently, two types of quizzes are generated:

1. Quizzes to translate a concept from one language to another and vice versa. Toisto quizzes the user in both directions. If there are multiple labels, Toisto uses all labels as question and as answer. So both "Mikä päivä tänään on?" and "Mikä päivä on tänään?" are asked as question and both are accepted as correct answer for the quiz "Welke dag is het vandaag?".
2. Quizzes to singularize a plural concept or pluralize a singular concept. Users are only asked to singularize and pluralize concepts in their practice language, not their own language.

### Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of how many times in a row a specific quiz is answered correctly. When a quiz is answered correctly twice or more in a row, the quiz is silenced for a while. The longer the streak, the longer the quiz is silenced. The exact amount is determined by a S-curve with a maximum value of 90 days. Whenever the user makes a mistake the streak is reset to 0.
