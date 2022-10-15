"""Command-line interface."""

import argparse

from .metadata import SUMMARY, VERSION, DECKS, SUPPORTED_LANGUAGES


parser = argparse.ArgumentParser(description=SUMMARY)
parser.add_argument("language", choices=SUPPORTED_LANGUAGES.keys(), help="language to practice")
parser.add_argument("-V", "--version", action="version", version=VERSION)
parser.add_argument(
    "-d", "--deck", action="append", default=[], choices=DECKS, help="deck to practice, can be repeated"
)
