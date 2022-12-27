"""Command-line interface."""

import argparse

from ..metadata import SUMMARY, VERSION, TOPICS, SUPPORTED_LANGUAGES


def add_language_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the language arguments to the parser."""
    choices = SUPPORTED_LANGUAGES.keys()
    parser.add_argument(
        "language", metavar="{practice language}", choices=choices,
        help="language to practice; available languages: %(choices)s"
    )
    parser.add_argument(
        "source_language", metavar="{your language}", choices=choices,
        help="your language; available languages: %(choices)s"
    )


def add_topic_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the topic arguments to the parser."""
    parser.add_argument(
        "-t", "--topic", action="append", default=[], choices=TOPICS, metavar="{topic}",
        help="topic to use, can be repeated (default: all); available topics: %(choices)s"
    )
    parser.add_argument(
        "-f", "--topic-file", action="append", default=[], metavar="{topic file}",
        help="topic file to use, can be repeated"
    )


argument_parser = argparse.ArgumentParser(description=SUMMARY)
argument_parser.add_argument("-V", "--version", action="version", version=VERSION)
subparsers = argument_parser.add_subparsers(
    dest="command", title="commands", help="type `%(prog)s {command} -h` for more information on a command",
    required=True
)
parser_practice = subparsers.add_parser(
    "practice", help="practice a language, for example type `%(prog)s practice fi en` to practice Finnish from English"
)
add_language_arguments(parser_practice)
add_topic_arguments(parser_practice)
parser_progress = subparsers.add_parser(
    "progress",
    help="show progress, for example type `%(prog)s progress fi en` to show progress on practicing Finnish from English"
)
add_language_arguments(parser_progress)
add_topic_arguments(parser_progress)
parser_progress.add_argument(
    "-s", "--sort", metavar="{option}", choices=["retention", "attempts"], default="retention",
    help="how to sort progress information (default: by retention); available options: %(choices)s"
)
