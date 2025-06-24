# Toisto

Toisto is an app to practice languages that runs in the [terminal](https://en.wikipedia.org/wiki/Terminal_emulator). It is developed in Python and available for Windows, Linux, macOS, and iOS (iPhone and iPad).

*Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

Toisto is beta software at the moment. It comes with a limited set of words and phrases in Dutch, English, and Finnish.

> [!NOTE]
> As long as Toisto is in beta the progress file format may change occasionally, causing your progress to be lost.

## Example sessions

<details>
<summary>Example session as GIF</summary>
<video src="https://github.com/fniessink/toisto/assets/3530545/8598dc4d-09ad-4057-9793-cee2fe54e420" controls="controls" style="max-width: 730px;">
</video>
</details>

<details>
<summary>Example session in text format</summary>

```console
$ toisto practice --target fi --source nl
👋 Welcome to Toisto v0.35.0!

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

## How to install Toisto

<details>
<summary>How to install Toisto on Windows</summary>

1. Install [uv](https://docs.astral.sh/uv/#getting-started). <details><summary>What is uv?</summary>uv is a tool that can install tools developed in Python, such as Toisto. Advantage of uv is that it also installs Python, if needed.</details>

2. Install Toisto:

```console
$ uv tool install toisto
```

If you have already installed Toisto and a newer version is available, upgrade Toisto as follows:

```console
$ uv tool upgrade toisto
```
</details>

<details>
<summary>How to install Toisto on Linux</summary>

1. On Linux, you must have an mp3 player installed so Toisto can speak. By default, Toisto expects `mpg123` to be available. If you want to use a different mp3 player, you can configure Toisto to do so, see [How to configure a different mp3 player](#how-to-configure-a-different-mp3-player) below.

2. Install [uv](https://docs.astral.sh/uv/#getting-started). <details><summary>What is uv?</summary>uv is a tool that can install tools developed in Python, such as Toisto. Advantage of uv is that it also installs Python, if needed.</details>

3. Install Toisto:

```console
$ uv tool install toisto
```

If you have already installed Toisto and a newer version is available, upgrade Toisto as follows:

```console
$ uv tool upgrade toisto
```
</details>

<details>
<summary>How to install Toisto on macOS</summary>

1. (Optional) On macOS, Toisto works best in a more modern terminal than the default one that macOS offers. We test with [iTerm2](https://iterm2.com). Toisto should work mostly fine with the default macOS terminal app, though.

2. Install [uv](https://docs.astral.sh/uv/#getting-started). <details><summary>What is uv?</summary>uv is a tool that can install tools developed in Python, such as Toisto. Advantage of uv is that it also installs Python, if needed.</details>

3. Install Toisto:

```console
$ uv tool install toisto
```

If you have already installed Toisto and a newer version is available, upgrade Toisto as follows:

```console
$ uv tool upgrade toisto
```
</details>

<details>
<summary>How to install Toisto on iOS (iPhone or iPad)</summary>

1. Install the free [a-Shell app](https://holzschu.github.io/a-Shell_iOS/). <details><summary>What is a-Shell?</summary>a-Shell provides a Unix-like terminal for Toisto to run in. It has Python pre-installed.</details>

2. Install Toisto using pip. <details><summary>What is pip?</summary>pip is a tool that can install packages developed in Python. It comes bundled with Python. a-Shell has Python pre-installed, and thus pip as well.</details>

   ```console
   $ pip install toisto
   ```

If you have already installed Toisto and a newer version is available, upgrade Toisto as follows:

```console
$ pip upgrade toisto
```
</details>

## How to use Toisto

### How to practice

Start Toisto as follows, giving the language you want to practice (the target language) and your language (the source language) as arguments:

```console
$ toisto practice --target fi --source en
```

To practice a specific concept and related concepts, pass it as follows (väri means color):

```console
$ toisto practice --target fi --source en väri
```

It's also possible to specify more than one concept to practice (hedelmä means fruit and vihannes means vegetable):

```console
$ toisto practice --target fi --source en hedelmä vihannes
```

Add `--help` or `-h` to get more information about the `practice` command, including the available concepts:

```console
$ toisto practice --help
```

### How to track progress

Use the `progress` command to see which quizzes you've answered correctly and when they will be presented next.

```console
$ toisto progress
```

Add `--help` or `-h` to get more information about the `progress` command:

```console
$ toisto progress --help
```

### How to share progress between devices

If you use Toisto on multiple devices, you probably want to share progress bwtween devices. Toisto can take progress made on other devices into account if it has access to the progress made on the other devices. To give Toisto access to those progress files, we need to make sure Toisto saves its progress to one shared folder from all devices. For example, on a cloud drive. Use the configure command on each device where you use Toisto to set the save folder:

```console
$ toisto configure --progress-folder /home/user/shared-drive/toisto  # Run this command on every device
```

See [How to configure the folder where to save progress](#How-to-configure-the-folder-where-to-save-progress) for more information on the `configure --progress-folder` command.

## How to configure Toisto

### How to configure your language

To prevent having to pass your target and source language as command-line arguments each time you run Toisto, you can save these to Toisto's configuration file:

```console
$ toisto configure --target nl --source en
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `languages` section if it doesn't exist, and adds or changes the target and source language:

```ini
[languages]
target = nl
source = en
```

### How to configure extra concept files

To prevent having to pass extra concept files as command-line arguments each time you run Toisto, you can save these to Toisto's configuration file:

```console
$ toisto configure --extra my_concepts1.json --extra my_concepts2.json
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `files` section if it doesn't exist, and adds the files to the list:

```ini
[files]
/home/user/my_concepts1.json
/home/user/my_concepts2.json
```

In addition to adding individual files, it is also possible to add folders to read extra concept files from. Toisto searches for concept files from the specified folders recursively.

> [!NOTE]
> See the [software documentation](docs/software.md) on how to create extra concept files.

### How to configure the folder where to save progress

By default, Toisto saves progress to your home folder. To save progress to a different folder, for example a cloud drive, configure the progress folder as follows:

```console
$ toisto configure --progress-folder /home/user/toisto
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `progress` section if it doesn't exist, and adds the folder:

```ini
[progress]
folder=/home/user/toisto
```

### How to configure progress updates

To prevent having to pass the desired progress update frequency as command-line argument each time you run Toisto, you can save the progress update frequency to Toisto's configuration file:

```console
$ toisto configure --progress-update 20
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `practice` section if it doesn't exist, and adds the desired progress update frequency:

```ini
[practice]
progress_update = 20
```

### How to configure a different mp3 player

On Windows, Linux, and macOS, Toisto uses Google Translate's text-to-speech API to convert text to speech and then plays the resulting mp3 file using an mp3 player. On iOS, Toisto uses the `say` command to convert text to speech and an mp3 player is not used.

By default, Toisto uses `afplay` on macOS, `mpg123` on Linux, and a builtin library (Pygame) on Windows to play the mp3 files.

You can configure Toisto to use a different mp3 player:

```console
$ toisto configure --mp3player name_of_mp3_player
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `commands` section if it doesn't exist, and adds the mp3 player:

```ini
[commands]
mp3player = name_of_mp3_player or `builtin`
```

Make sure the mp3 player is on the `PATH` or include the complete filepath of the mp3 player.

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

When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.toisto-{uuid}-progress-{target language}.json` in your home folder, for example `.toisto-221b69f2-83ef-11ef-abc8-2642a2aed6c5-progress-fi.json`.

## Further documentation

- [More information](docs/background.md) on why Toisto exists and what the future plans are.
- The [Toisto software documentation](docs/software.md) describes the inner workings of Toisto, including the format of the concept files.
- The [Toisto developer documentation](docs/developer.md) provides information on how to develop, test, and release Toisto. This is aimed at people who (want to help) develop Toisto.
