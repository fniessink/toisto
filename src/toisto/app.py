"""Main module for the application."""

import readline  # pylint: disable=unused-import

from .ui.cli import parser
from .command import practice, show_progress
from .persistence import load_quizzes, load_progress


def main():
    """Main program."""
    args = parser.parse_args()
    topics = load_quizzes(args.language, args.source_language, args.topic, args.topic_file)
    progress = load_progress()
    if args.command == "practice":
        practice(topics, progress)
    else:
        show_progress(args.language, topics, progress)
