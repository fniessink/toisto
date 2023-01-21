"""Command-line interface."""

from argparse import ArgumentParser, _SubParsersAction

from ..metadata import latest_version, SUMMARY, VERSION, TOPICS, SUPPORTED_LANGUAGES


def add_language_arguments(parser: ArgumentParser) -> None:
    """Add the language arguments to the parser."""
    choices = SUPPORTED_LANGUAGES.keys()
    practice_language_help = "language to practice; available languages: %(choices)s"
    parser.add_argument("language", metavar="{practice language}", choices=choices, help=practice_language_help)
    source_language_help = "your language; available languages: %(choices)s"
    parser.add_argument("source_language", metavar="{your language}", choices=choices, help=source_language_help)


def add_topic_arguments(parser: ArgumentParser) -> None:
    """Add the topic arguments to the parser."""
    topic_help = "topic to use, can be repeated (default: all); available topics: %(choices)s"
    parser.add_argument(
        "-t", "--topic", action="append", default=[], choices=TOPICS, metavar="{topic}", help=topic_help
    )
    topic_file_help = "topic file to use, can be repeated"
    parser.add_argument("-f", "--topic-file", action="append", default=[], metavar="{topic file}", help=topic_file_help)


def add_practice_command(subparser: _SubParsersAction) -> None:
    """Add a practice command."""
    command_help = "practice a language, for example type `%(prog)s practice fi en` to practice Finnish from English"
    add_command(subparser, "practice", "Practice a language.", command_help)


def add_progress_command(subparser: _SubParsersAction) -> None:
    """Add a command to show progress."""
    command_help = (
        "show progress, for example `%(prog)s progress fi en` shows progress on practicing Finnish from English"
    )
    parser = add_command(subparser, "progress", "Show progress.", command_help)
    sort_help = "how to sort progress information (default: by retention); available options: %(choices)s"
    parser.add_argument(
        "-s", "--sort", metavar="{option}", choices=["retention", "attempts"], default="retention", help=sort_help
    )


def add_topics_command(subparser: _SubParsersAction) -> None:
    """Add a command to show topics."""
    command_help = "show topics, for example `%(prog)s topics -t nature` shows the contents of the nature topic"
    add_command(subparser, "topics", "Show topics", command_help)


def add_command(subparser: _SubParsersAction, command: str, description: str, command_help: str) -> ArgumentParser:
    """Add a command."""
    parser = subparser.add_parser(command, description=description, help=command_help)
    add_language_arguments(parser)
    add_topic_arguments(parser)
    return parser


def create_argument_parser() -> ArgumentParser:
    """Create the argument parser."""
    argument_parser = ArgumentParser(description=SUMMARY)
    latest = latest_version()
    version = f"v{VERSION}" + (f" ({latest} is available)" if latest and latest.strip("v") > VERSION else "")
    argument_parser.add_argument("-V", "--version", action="version", version=version)
    command_help = "type `%(prog)s {command} -h` for more information on a command"
    subparser_action = argument_parser.add_subparsers(
        dest="command", title="commands", help=command_help, required=True
    )
    add_practice_command(subparser_action)
    add_progress_command(subparser_action)
    add_topics_command(subparser_action)
    return argument_parser
