# Toisto

Toisto is an app to practice languages that runs in the [terminal](https://en.wikipedia.org/wiki/Terminal_emulator). It is developed in Python and available for Windows, Linux, macOS, iOS, and iPadOS.

It uses [spaced repetition](https://en.wikipedia.org/wiki/Spaced_repetition) to help you memorize vocabulary and phrases. It comes with a limited set of words and phrases in Dutch, English, and Finnish.

*Toisto* is Finnish and means *reiteration, playback, repetition, reproduction*.

> [!WARNING]
> Toisto is currently in beta. The progress file format may change occasionally, causing your progress to be lost.

## See it in action

Here's what a typical practice session looks like:

<video src="https://github.com/fniessink/toisto/assets/3530545/8598dc4d-09ad-4057-9793-cee2fe54e420" controls="controls" style="max-width: 730px;">
</video>

## Installation

### Prerequisites

On **Linux, Windows, and macOS**, install [uv](https://docs.astral.sh/uv/#getting-started):

```console
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

With uv you can install tools developed in Python, such as Toisto. Advantage of uv is that it also installs Python, if needed.

On **Linux**, you must have an mp3 player installed so Toisto can speak. By default, Toisto expects `mpg123` to be available. If you want to use a different mp3 player, you can configure Toisto to do so, see [configure a different mp3 player](docs/userguide.md#Configure-a-different-mp3-player) below.

On **macOS**, Toisto works best in a more modern terminal than the default macOS terminal. We test with [iTerm2](https://iterm2.com). Toisto should work mostly fine with the default macOS terminal app though, so installing iTerm2 or another terminal is optional.

On **iOS and iPadOS**, install the free [a-Shell app](https://holzschu.github.io/a-Shell_iOS/). a-Shell provides a Unix-like terminal for Toisto to run in. It has Python and pip (Python package manager) pre-installed.

### Install Toisto

On **Linux, Windows, and macOS**:

```console
$ uv tool install toisto
```

On **iOS and iPadOS**:

```console
$ pip install toisto
```

## Quick start

To practice:

```console
$ toisto practice --target fi --source en
```

Supported languages at the moment are English (`en`), Finnish (`fi`), and Dutch (`nl`).

To stop practicing: type `Ctrl-C` or `Ctrl-D`.

To prevent having to specify your target and source language every practice session, configure them as follows:

```console
$ toisto configure --target fi --source en
```

## Further documentation

- [User guide](docs/userguide.md).
- [Background information](docs/background.md) on why Toisto exists and what the future plans are.
- [Concept files](docs/concept_files.md) describes the format of the concept files.
- [Software documentation](docs/software.md) describes how Toisto works.
- [Developer documentation](docs/developer.md) provides information on how to develop, test, and release Toisto. This is aimed at people who (want to help) develop Toisto.
