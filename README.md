# Toisto

Command-line app to practice languages. *Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

Toisto is beta software at the moment. It comes with a limited set of words and phrases in Dutch, English, and Finnish.

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

Add `--help` or `-h` to get more information about the command-line options and arguments:

```console
$ toisto --help
```

### Example sessions

![gif](https://raw.githubusercontent.com/fniessink/toisto/main/docs/demo.gif)

```console
$ toisto fi nl
 Welcome to Toisto v0.1.0!

Practice as many words and phrases as you like, for as long as you like.
Hit Ctrl-C or Ctrl-D to quit.

Toisto tracks how many times you correctly translate words and phrases.
When you correctly translate a word or phrase multiple times in a row,
Toisto will not quiz you on it for a while. The more correct translations
in a row, the longer words and phrases are silenced.

Listen and write in Finnish:
> Oranssi
✅ Correct.

Translate into Finnish:
Paars
> Violetti
✅ Correct.
Skipping this quiz for 3 days.

Translate into Dutch:
Keltainen
> Geel
✅ Correct.
Skipping this quiz for 3 days.

Translate into Finnish:
Groen
> virea
⚠️ Incorrect. Please try again.
> vihrea
❌ Incorrect. The correct answer is "Vihreä".
```

### How it works

Toisto quizzes you repeatably on words and phrases in the language you want to practice. For each quiz, Toisto keeps track of how long you answer it correctly. When you answer a quiz correctly multiple times, Toisto will silence the quiz for a while. The longer the time you have answered the quiz correctly, the longer a quiz is silenced. This starts at a few minutes, but then increases rapidly when you keep answering correctly.

At the moment, Toisto has the following types of quizzes:

- Translate a word or phrase from your practice language to your native language or the other way around. For example, if your native language is English and you're practicing Dutch, Toisto can ask you to give the English version of "Maandag" (which is, you guessed it, "Monday") or ask you to give the Dutch version of "Friday" (which is "Vrijdag").
- Listen to a word or phrase from your practice language and type what you hear. For example, if your practice language is Finnish, Toisto may say "Tänään on maanantai" (Today is Monday) and that's then what you have to type.
- Give a singular version of a plural, or a plural version of a singular. For example, what is the plural of "Talo" (meaning house in Finnish, and the answer is "Talot") or what is the singular of "Huizen" (meaning houses in Dutch, and the answer is "Huis").
- Change the grammatical person from and to first person, second person, and third person. For example, when asked what the second person of "Ik eet" (meaning "I eat") is, the correct answer would be "Jij eet" ("You eat").
- Change the grammatical gender from female to male or the other way around. For example, what is the male version of "She is" or what is the female version of "He is".
- Change the comparative degree of an adjective. For example, what is the superlative degree of "Aardig" (which means "Nice", and the answer would be "Aardigst").

When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-progress.json` in your home folder.

## Further documentation

- The [Toisto software documentation](docs/software.md) describes the inner workings of Toisto, including the format of the topic files.
- The [Toisto developer documentation](docs/developer.md) provides information on how to develop, test, and release Toisto. This is aimed at people who (want to help) develop Toisto.
