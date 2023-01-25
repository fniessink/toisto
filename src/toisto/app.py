"""Main module for the application."""

import readline  # pylint: disable=unused-import
import logging

# Suppress warning messages printed by the playsound module.
logging.getLogger().setLevel(logging.ERROR)  # pylint: disable=wrong-import-position

from .command import practice, show_topics, show_progress
from .metadata import latest_version
from .persistence import load_topics, load_progress, read_config
from .ui.cli import create_argument_parser
from .ui.text import show_welcome


def main():
    """Main program."""
    config = read_config()
    argument_parser = create_argument_parser()
    args = argument_parser.parse_args()
    topics = load_topics(args.language, args.source_language, args.topic, args.topic_file, argument_parser)
    progress = load_progress(topics, argument_parser)
    if args.command == "practice":
        show_welcome(latest_version())
        practice(progress, config)
    elif args.command == "topics":
        show_topics(args.language, args.source_language, topics)
    else:
        show_progress(args.language, topics, progress, args.sort)
