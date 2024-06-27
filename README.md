# Toisto

Command-line app to practice languages. *Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

Toisto is beta software at the moment. It comes with a limited set of words and phrases in Dutch, English, and Finnish.

> [!NOTE]
> As long as Toisto is in beta the progress file format may change occasionally, causing your progress to be lost.

## Example sessions

<video src="https://github.com/fniessink/toisto/assets/3530545/8598dc4d-09ad-4057-9793-cee2fe54e420" controls="controls" style="max-width: 730px;">
</video>

<details>

<summary>Another example in text format</summary>

```console
$ toisto practice --target fi --source nl
👋 Welcome to Toisto v0.10.0!

Practice as many words and phrases as you like, for as long as you like.

Toisto quizzes you on words and phrases repeatedly. Each time you answer
a quiz correctly, Toisto will wait longer before repeating it. If you
answer incorrectly, you get one additional attempt to give the correct
answer. If the second attempt is not correct either, Toisto will reset
the quiz interval.

How does it work?
● To answer a quiz: type the answer, followed by Enter.
● To repeat the spoken text: type Enter without answer.
● To skip to the answer immediately: type ?, followed by Enter.
● To read more about an underlined word: keep ⌘ (the command key) pressed
  while clicking the word. Not all terminals may support this.
● To quit: type Ctrl-C or Ctrl-D.

Translate into Dutch:
musta
> zwart
✅ Correct.

Translate into Dutch:
valkoinen
> wit
✅ Correct.

Translate into Dutch:
keltainen
> oranje
⚠️  Incorrect. Please try again.
> geel
✅ Correct.

Translate into Finnish:
oranje
> oransi
⚠️  Incorrect. Please try again.
> oransie
❌ Incorrect. The correct answer is "oranssi".
```

</details>

## User guide

### Prerequisites

Make sure you have these prequisities installed:

- [Python 3.10 or newer](https://python.org).
- [pipx](https://pypa.github.io/pipx/).
- On Linux: the `mpg123` mp3 player.

If you want to use a different mp3 player, you can configure Toisto to do so, see [How to configure a different mp3 player](#how-to-configure-a-different-mp3-player) below.

For some features, Toisto needs a more modern terminal than the default one that MacOS offers. We test with [iTerm2](https://iterm2.com). But this is optional, Toisto should work fine with the default MacOS terminal app.

### How to install

Install Toisto as follows:

```console
$ pipx install Toisto
```

If you have already installed Toisto and a newer version is available, upgrade Toisto as follows:

```console
$ pipx upgrade Toisto
```

### How to use

Start Toisto as follows, giving the language you want to practice (the target language) and your language (the source language) as arguments:

```console
$ toisto practice --target fi --source en
```

To practice a specific concept and related concepts, pass it as follows:

```console
$ toisto practice --target fi --source en color
```

It's also possible to specify more than one concept to practice:

```console
$ toisto practice --target fi --source en fruit vegetable
```

Add `--help` or `-h` to get more information about the command-line options and arguments:

```console
$ toisto --help
```

### How to configure Toisto

#### How to configure your language

To prevent having to pass your target and source language as command-line arguments each time you run Toisto, put them in Toisto's configuration file. Create a file `.toisto.cfg` in your home directory if it doesn't exist, add the `languages` section if it doesn't exist, and add the target and source language:

```ini
[languages]
target = nl
source = en
```

#### How to configure progress updates

To prevent having to pass the desired progress update frequency as command-line argument each time you run Toisto, put it in Toisto's configuration file. Create a file `.toisto.cfg` in your home directory if it doesn't exist, add the `practice` section if it doesn't exist, and add the desired progress update frequency:

```ini
[practice]
progress_update = 20  # While practicing, give a progress update every 20 quizzes.
```

#### How to configure a different mp3 player

By default, Toisto uses `afplay` on MacOS, `mpg123` on Linux, and a builtin library (Pygame) on Windows to play mp3 files. You can configure Toisto to use a different mp3 player. Create a file `.toisto.cfg` in your home directory if it doesn't exist, add the `commands` section if it doesn't exist, and add the mp3 player:

```ini
[commands]
mp3player = name_of_mp3_player or `builtin`
```

Make sure the mp3 player is on the `PATH` or put the complete filepath in the config file.

## How it works

Toisto quizzes you repeatably on words and phrases in the language you want to practice, your target language. For each quiz, Toisto keeps track of how long you answer it correctly. When you answer a quiz correctly multiple times, Toisto will silence the quiz for a while. The longer the time you have answered the quiz correctly, the longer a quiz is silenced. This starts at a few minutes, but then increases rapidly when you keep answering correctly.

Toisto supports quiz types such as:

- **Translate** a word or phrase from your target language to your source language or the other way around.

  For example, if your native language is English and you're practicing Dutch, Toisto can ask you to give the English version of "maandag" (which is, you guessed it, "Monday") or ask you to give the Dutch version of "Friday" (which is "vrijdag").

- **Listen** to a word or phrase from your target language and type what you hear either in your target language or your source language.

  For example, if your target language is Finnish, Toisto may say "Tänään on maanantai" and then you have to type ether "Tänään on maanantai" or "Today is Monday".

- Give a **singular** version of a plural, or a **plural** version of a singular.

  For example, what is the plural of "talo" (meaning house in Finnish, and the answer is "talot") or what is the singular of "de huizen" (meaning the houses in Dutch, and the answer would be "het huis").

- Give the **diminutive** form of a word.

  For example, what is the diminutive form of "het huis" in Dutch (meaning house in Dutch and the answer would be "het huisje").

- Change the **grammatical person** from and to first person, second person, and third person.

  For example, when asked what the second person of "ik eet" (meaning "I eat") is, the correct answer would be "jij eet" ("you eat").

- Change the **tense** of verbs from present to past tense or the other way around.

  For example, what is the past tense of "she walks" or what is the present tense version of "he painted".

- Change the **comparative degree** of an adjective.

  For example, what is the superlative degree of "aardig" (which means "nice", and the answer would be "aardigst").

- Give the **antonym** of adjectives.

  For example, what is the antonym of "good"? The answer is of course "bad".

- Change the **grammatical mood** of sentences. Toisto currently supports declarative, interrogative, and imperative sentences.

  For example, what is the interrogative form of "The car is black"? The answer would be "Is the car black?".

- **Answer a question**.

  For example, a question in Finnish could be "Pidätko sinä jäätelöstä?" (meaning "Do you like ice cream?") and correct answers would be "Pidän" (meaning "Yes, I do") and "En" (meaning "No, I don't").

See [the complete list of quiz types](docs/software.md#quizzes).

When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-progress-{target language}.json` in your home folder, for example `.toisto-progress-fi.json`.

## Further documentation

- [More information](docs/background.md) on why Toisto exists and what the future plans are.
- The [Toisto software documentation](docs/software.md) describes the inner workings of Toisto, including the format of the concept files.
- The [Toisto developer documentation](docs/developer.md) provides information on how to develop, test, and release Toisto. This is aimed at people who (want to help) develop Toisto.
