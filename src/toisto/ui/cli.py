"""Command-line interface."""

import argparse

from ..metadata import SUMMARY, VERSION, TOPICS, SUPPORTED_LANGUAGES


parser = argparse.ArgumentParser(description=SUMMARY)
parser.add_argument("-V", "--version", action="version", version=VERSION)
parser.add_argument(
    "-t", "--topic", action="append", default=[], choices=TOPICS, metavar="{topic}",
    help="topic to use, can be repeated (default: all); available topics: %(choices)s"
)
parser.add_argument(
    "-f", "--topic-file", action="append", default=[], metavar="{topic file}",
    help="topic file to use, can be repeated"
)
parser.add_argument(
    "language", metavar="{language to practice}", choices=SUPPORTED_LANGUAGES.keys(),
    help="language to practice; available languages: %(choices)s"
)
parser.add_argument(
    "source_language", metavar="{your language}", choices=SUPPORTED_LANGUAGES.keys(),
    help="your language; available languages: %(choices)s"
)
parser.add_argument(
    "command", metavar="{command}", choices=["practice", "progress"], default="practice", nargs="?",
    help="command to perform (default: practice); available commands: %(choices)s"
)
