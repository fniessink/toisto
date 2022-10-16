"""Command-line interface."""

import argparse

from .metadata import SUMMARY, VERSION, DECKS, SUPPORTED_LANGUAGES


parser = argparse.ArgumentParser(description=SUMMARY)
parser.add_argument("-V", "--version", action="version", version=VERSION)
parser.add_argument(
    "-d", "--deck", action="append", default=[], choices=DECKS, metavar="{deck}",
    help="deck to use, can be repeated (default: all); available decks: %(choices)s"
)
parser.add_argument(
    "language", metavar="{language}", choices=SUPPORTED_LANGUAGES.keys(),
    help="language to practice; available languages: %(choices)s"
)
parser.add_argument(
    "command", metavar="{command}", choices=["practice", "progress"], default="practice", nargs="?",
    help="command to perform (default: practice); available commands: %(choices)s"
)
