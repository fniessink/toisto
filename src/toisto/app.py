"""Main module for the application."""

import readline  # pylint: disable=unused-import

from .ui.cli import argument_parser
from .command import practice, show_topics, show_progress
from .persistence import load_topics, load_progress


def main():
    """Main program."""
    args = argument_parser.parse_args()
    topics = load_topics(args.language, args.source_language, args.topic, args.topic_file)
    progress = load_progress(topics)
    if args.command == "practice":
        practice(progress)
    elif args.command == "topics":
        show_topics(args.language, args.source_language, topics)
    else:
        show_progress(args.language, topics, progress, args.sort)
