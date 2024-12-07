"""Main module for the application."""

from contextlib import suppress

with suppress(ImportError):
    import readline  # noqa: F401 `readline` imported but unused

from .command.configure import configure
from .command.practice import practice
from .command.show_progress import show_progress
from .metadata import BUILT_IN_CONCEPT_JSON_FILES, latest_version
from .model.filter import filter_concepts
from .model.language import LanguagePair
from .model.quiz.progress import Progress
from .model.quiz.quiz_factory import create_quizzes
from .model.quiz.quiz_type import QuizType
from .persistence.concept_loader import ConceptLoader
from .persistence.config import default_config, read_config
from .persistence.progress import load_progress
from .persistence.spelling_alternatives import load_spelling_alternatives
from .ui.cli import create_argument_parser, parse_arguments
from .ui.text import console, show_welcome


class CLI:
    """Command-line interface commands, arguments, and options."""

    def __init__(self) -> None:
        argument_parser = create_argument_parser(default_config())
        self.config = read_config(argument_parser)
        self.loader = ConceptLoader(argument_parser)
        self.build_in_concepts = self.loader.load_concepts(*BUILT_IN_CONCEPT_JSON_FILES)
        self.argument_parser = create_argument_parser(self.config, self.build_in_concepts)
        self.args = parse_arguments(self.argument_parser)
        self.language_pair = LanguagePair(self.args.target_language, self.args.source_language)

    @property
    def progress(self) -> Progress:
        """Return the current progress."""
        load_spelling_alternatives(self.language_pair)
        target_language = self.args.target_language
        concepts = self.build_in_concepts | self.loader.load_concepts(*self.args.extra)
        filtered_concepts = filter_concepts(concepts, self.args.concepts, target_language, self.argument_parser)
        quiz_types = tuple(QuizType.actions.get_values(quiz_type)[0] for quiz_type in self.args.quiz_type)
        quizzes = create_quizzes(self.language_pair, quiz_types, *filtered_concepts)
        return load_progress(target_language, quizzes, self.argument_parser, self.config)


def main() -> None:
    """Run the main program."""
    cli = CLI()
    match cli.args.command:
        case "configure":
            configure(cli.argument_parser, cli.config, cli.args)
        case "progress":
            show_progress(cli.progress, cli.args)
        case _:  # Default command is "practice"
            show_welcome(console.print, latest_version(), cli.config)
            practice(console.print, cli.language_pair, cli.progress, cli.config, cli.args)
