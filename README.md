# Kieli

Command-line app to practice languages. *Kieli* is Finnish for *language*.

Kieli is alpha software at the moment. It comes with a limited set of words and phrases in Dutch and Finnish.

## Prerequisites

MacOS (for the say command), [Python 3.10 or newer](https://python.org), and [pipx](https://pypa.github.io/pipx/).

## How to install

```console
$ pipx install Kieli
```

## How to use

Start the program as follows:

```console
 $ kieli
```

## Example session

```console
Welcome to 'Kieli'!
Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
Kieli tracks how many times you correctly translate words and phrases. The fewer times you have
translated a word or phrase successfully, the more often it is presented for you to translate.

Dertien
> Kolmetoista
✅ Correct.

Kolmetoista
> Dertien
✅ Correct.

Veertien
> Neljätoista
✅ Correct.

Neljätoista
> viertien
❌ Incorrect. The correct answer is "veertien".

Neljätoista
> veertien
✅ Correct.
```

## How it works

Kieli presents words and phrases in Dutch and Finnish for you to translate. Words and phrases are sorted by 'progress'. When you translate a word or phrase correctly, its progress increases, otherwise it decreases. Words and phrases are sorted by progress so that the ones with the lowest score are presented to you first. When you stop the program (hit Ctrl-C or Ctrl-D), progress is saved in a file named `.kieli-progress.json` in your home folder.
