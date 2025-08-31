# User guide

## Toisto commands

Toisto has four commands: `practice`, `progress`, `configure`, and `self`.

To get more information on a specific command, add the help flag. For example:

```console
$ toisto practice --help
```

### Practice

Practice is the default command, so running Toisto without arguments starts Toisto in practice mode, provided you have configured your target and source languages. See [configure languages](#Configure-languages).

```console
$ toisto
```

To practice a specific concepts and concepts related to it:

```console
$ toisto viikko
```

> [!NOTE]
> 'viikko' means 'week', this practices 'week' and related concepts such as days of the week.

To practice multiple concepts and their related concepts:

```console
$ toisto practice hedelmä vihannes
```

> [!NOTE]
> 'hedelmä' means 'fruit' and 'vihannes' means 'vegetable'.

To see available concepts:

```console
$ toisto practice --help
```

To practice one or more specific quiz types:

```console
$ toisto --quiz-type antonym
```

### Track progress

Use the `progress` command to see which quizzes you've answered correctly and when they will be presented next.

```console
$ toisto progress
```

### Configure Toisto

Use the `configure` command to change Toisto settings. To show the current configuration, run the command without arguments:

```console
$ toisto configure
```

Which will show the contents of the configuration file:

```ini
╭────────────────── /Users/janedoe/.toisto.cfg ──────────────────╮
│ [commands]                                                     │
│ mp3player=afplay                                               │
│                                                                │
│ [practice]                                                     │
│ progress_update=10                                             │
│ show_quiz_retention=yes                                        │
│                                                                │
│ [languages]                                                    │
│ target=fi                                                      │
│ source=nl                                                      │
│                                                                │
│ [identity]                                                     │
│ uuid=b5313426-82f2-11af-af53-2822a2aed6c5                      │
│                                                                │
│ [progress]                                                     │
│ folder=/Users/janedoe                                          │
│                                                                │
╰────────────────────────────────────────────────────────────────╯
```

#### Configure languages

To prevent having to pass your target and source language as command-line arguments each time you run Toisto, you can save these to Toisto's configuration file:

```console
$ toisto configure --target nl --source en
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `languages` section if it doesn't exist, and adds or changes the target and source language:

```ini
[languages]
target=nl
source=en
```

#### Configure extra concept files

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

See the [software documentation](docs/software.md) on how to create extra concept files.

#### Configure where to save progress

By default, Toisto saves progress to your home folder. To save progress to a different folder, for example a cloud drive, configure the progress folder as follows:

```console
$ toisto configure --progress-folder /home/user/toisto
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `progress` section if it doesn't exist, and adds the folder:

```ini
[progress]
folder=/home/user/toisto
```

#### Configure progress updates

To prevent having to pass the desired progress update frequency as command-line argument each time you run Toisto, you can save the progress update frequency to Toisto's configuration file:

```console
$ toisto configure --progress-update 20
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `practice` section if it doesn't exist, and adds the desired progress update frequency:

```ini
[practice]
progress_update=20
```

#### Display quiz retention

To have Toisto show retention after each quiz, you can turn this on in Toisto's configuration file:

```console
$ toisto configure --show-quiz-retention
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `practice` section if it doesn't exist, and sets the show quiz retention to yes:

```ini
[practice]
show_quiz_retention=yes
```

#### Configure a different mp3 player

On Windows, Linux, and macOS, Toisto uses Google Translate's text-to-speech API to convert text to speech and then plays the resulting mp3 file using an mp3 player. On iOS and iPadOS, Toisto uses the `say` command to convert text to speech and an mp3 player is not used.

By default, Toisto uses `afplay` on macOS, `mpg123` on Linux, and a builtin library (Pygame) on Windows to play the mp3 files.

You can configure Toisto to use a different mp3 player:

```console
$ toisto configure --mp3player name_of_mp3_player
```

When running the previous command, Toisto creates a file `.toisto.cfg` in your home directory if it doesn't exist, adds the `commands` section if it doesn't exist, and adds the mp3 player:

```ini
[commands]
mp3player=name_of_mp3_player or `builtin`
```

Make sure the mp3 player is on the `PATH` or include the complete filepath of the mp3 player.

#### Share progress between devices

If you use Toisto on multiple devices, you probably want to share progress between devices. Toisto can take progress made on other devices into account if it has access to the progress made on the other devices. To give Toisto access to those progress files, we need to make sure Toisto saves its progress to one shared folder from all devices. For example, on a cloud drive. Use the configure command on each device where you use Toisto to set the save folder:

```console
$ toisto configure --progress-folder /home/user/shared-drive/toisto  # Run this command on every device
```

See [configure where to save progress](#Configure-where-to-save-progress) for more information on the `configure --progress-folder` command.

### Manage Toisto

Use the `self` command to manage Toisto itself. To check for new versions:

```console
$ toisto self version
```

To upgrade Toisto if a new version is available:

```console
$ toisto self upgrade
```

To uninstall Toisto:

```console
$ toisto self uninstall
```

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
