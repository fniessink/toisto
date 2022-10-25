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

If you have already installed Toisto and a newer version is available, upgrade Toisto as follows:

```console
$ pipx upgrade Toisto
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
👋 Welcome to Toisto v0.0.8!

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

Toisto quizzes you repeatably on words and phrases in the language you want to practice. At the moment, Toisto has three types of quizzes:

- Translate a word or phrase from your practice language to your native language or the other way around,
- Give a singular version of a plural noun,
- Give a plural version of a singular noun.

For each quiz, Toisto counts how often in a row you answered it correctly. So each quiz has its own streak. When you answer a quiz correctly multiple times, Toisto will silence the quiz for a while. The longer the streak, the longer a quiz is silenced. This starts at a few minutes, but then increases rapidly when you keep answering correctly: a streak of 13 correct answers silences a quiz for 24 hours, a streak of 18 silences the quiz for 10 days, and a streak of 20 silences it for 20 days. The maximum amount of time a quiz is silenced is roughly three months.

When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-progress.json` in your home folder.

## Further documentation

- The [Toisto software documentation](docs/software.md) describes the inner workings of Toisto, including the format of the topic files.
- The [Toisto developer documentation](docs/developer.md) provides information on how to develop, test, and release Toisto. This is aimed at people who (want to help) develop Toisto.
