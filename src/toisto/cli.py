"""Command-line interface."""

import argparse

from .metadata import SUMMARY, VERSION, DECKS


parser = argparse.ArgumentParser(description=SUMMARY)
parser.add_argument("-V", "--version", action="version", version=VERSION)
parser.add_argument(
    "-d", "--deck", action="append", default=[], choices=DECKS, help="deck to practice, can be repeated"
)
