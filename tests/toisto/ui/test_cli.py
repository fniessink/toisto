"""Unit tests for the CLI module."""

import os
import re
import unittest
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.metadata import README_URL, VERSION
from toisto.model.language import EN, FI
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.grammatical_form import GrammaticalForm
from toisto.model.language.label import Label, Labels
from toisto.persistence.config import default_config
from toisto.persistence.folder import home
from toisto.ui.cli import create_argument_parser, parse_arguments, practiceable_concepts

CONFIGURE_USAGE = """Usage: toisto configure [-h] [-t {language}] [-s {language}] [-e {path}] [-p {path}] \
[-u {frequency}] [-r {yes,no}]
                        [-m {mp3player}]"""
PRACTICE_USAGE = """Usage: toisto practice [-h] -t {language} -s {language} [-e {path}] [-q {quiz type}] \
[-u {frequency}] [-r {yes,no}]
                       [{concept} ...]"""
CONFIGURE_DESCRIPTION = f"Configure options and save them in {home()!s}/.toisto.cfg."
PRACTICE_USAGE_OPTIONAL_LANGUAGES = """Usage: toisto practice [-h] [-t {language}] [-s {language}] [-e {path}] \
[-q {quiz type}] [-u {frequency}]
                       [-r {yes,no}]
                       [{concept} ...]"""
PRACTICE_DESCRIPTION = "Practice a language."
POSITIONAL_ARGUMENTS = """Positional Arguments:
  {concept}             concept to use, can be repeated; default: all; built-in concepts:%s"""
HELP_OPTION = "-h, --help            show this help message and exit"
TARGET_OPTION = """-t, --target {language}
                        target language; %slanguages available in built-in concepts: en, fi, nl"""
SOURCE_OPTION = """-s, --source {language}
                        source language; %slanguages available in built-in concepts: en, fi, nl"""
EXTRA_OPTION = "-e, --extra {path}    file or folder with extra concepts to read, can be repeated; default: %s"
PROGRESS_FOLDER = f"""-p, --progress-folder {{path}}
                        folder where to save progress; default: {home()!s}"""
PROGRESS_OPTION = """-u, --progress-update {frequency}
                        show a progress update after each {frequency} quizzes; default: %s (0 means never)"""
RETENTION_OPTION = """-r, --show-quiz-retention {yes,no}
                        show the quiz retention after each quiz; default: no"""
MP3PLAYER_OPTION = """-m, --mp3player {mp3player}
                        mp3 player to play sounds; default: afplay"""
QUIZ_TYPE_OPTION = """-q, --quiz-type {quiz type}
                        quiz types to use, can be repeated; default: all; available quiz types: abbreviation,
                        affirmative, answer, antonym, cardinal, cloze, comparative degree, declarative, dictate,
                        diminutive, feminine, first person, full form, imperative, imperfective, infinitive,
                        interpret, interrogative, masculine, negative, neuter, order, ordinal, past tense, perfective,
                        plural, plural pronoun, positive degree, present tense, read, second person, singular,
                        singular pronoun, superlative degree, third person, verbal noun, write"""
HELP_MESSAGE = f"""Usage: toisto [-h] [-V] {{configure,practice,progress,self}} ...

Toisto is a command-line terminal app to practice languages.

Options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit

Commands:
  {{configure,practice,progress,self}}
                        default: practice; type `toisto {{command}} --help` for more information on a command
    configure           configure options, for example `toisto configure --target fi --source en` to make practicing
                        Finnish from English the default
    practice            practice a language, for example `toisto practice --target fi --source en` to practice Finnish
                        from English
    progress            show progress, for example `toisto progress --target fi --source en` to show progress on
                        practicing Finnish from English
    self                manage Toisto itself, for example `toisto self upgrade` to upgrade Toisto to the latest
                        version

See {README_URL} for more information.
"""


class ParserTestCase(unittest.TestCase):
    """Base class for the CLI parser unit tests."""

    ANSI_ESCAPE_CODES = re.compile(r"\x1B\[\d+(;\d+){0,2}m")

    def setUp(self) -> None:
        """Set up the test fixtures."""
        os.environ["COLUMNS"] = "120"  # Set the width of the terminal to match the formatting of the expected results
        self.default_namespace = {
            "extra": [],
            "progress_update": 0,
            "show_quiz_retention": False,
            "source_language": None,
            "target_language": None,
        }

    def argument_parser(
        self,
        config_parser: ConfigParser | None = None,
        concepts: set[Concept] | None = None,
        latest_version: str = f"v{VERSION}",
    ) -> ArgumentParser:
        """Create the argument parser."""
        with patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[{"name": latest_version}])))):
            return create_argument_parser(config_parser or default_config(), concepts)

    def assert_output(self, expected_output: str, write: Mock) -> None:
        """Check the expected output."""
        self.assertEqual(expected_output, self.ANSI_ESCAPE_CODES.sub("", write.call_args_list[3][0][0]))


class HelpTest(ParserTestCase):
    """Unit tests for the help option."""

    @patch("sys.argv", ["toisto", "--help"])
    @patch("sys.stdout.write")
    def test_help(self, sys_stdout_write: Mock) -> None:
        """Test that the help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assert_output(HELP_MESSAGE, sys_stdout_write)

    @patch("sys.argv", ["toisto", "-h"])
    @patch("sys.stdout.write")
    def test_help_short_option(self, sys_stdout_write: Mock) -> None:
        """Test that the help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assert_output(HELP_MESSAGE, sys_stdout_write)


class ConfigureCommandTest(ParserTestCase):
    """Unit tests for the configure command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        super().setUp()
        self.default_namespace |= {
            "command": "configure",
            "mp3player": "afplay",
            "progress_folder": home(),
            "show_quiz_retention": "no",
        }

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--target", "nl", "--source", "fi"])
    def test_configure_command(self) -> None:
        """Test that the configure command can be specified."""
        expected_namespace = {
            **self.default_namespace,
            "target_language": "nl",
            "source_language": "fi",
        }
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--progress-update", "5"])
    def test_configure_progress_update(self) -> None:
        """Test that the progress update frequency can be configured."""
        expected_namespace = {**self.default_namespace, "progress_update": 5}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--show-quiz-retention", "yes"])
    def test_configure_quiz_retention(self) -> None:
        """Test that showing the quiz retention can be configured."""
        expected_namespace = {**self.default_namespace, "show_quiz_retention": "yes"}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--progress-folder", "/home/user/toisto"])
    @patch("toisto.ui.cli.Path.is_dir", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=True))
    def test_configure_progress_folder(self) -> None:
        """Test that the progress folder can be configured."""
        expected_namespace = {**self.default_namespace, "progress_folder": Path("/home/user/toisto")}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--progress-folder", "/home/user/toisto"])
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_configure_non_existing_progress_folder(self, sys_stderr_write: Mock) -> None:
        """Test that the progress folder is checked for existence."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "error: argument -p/--progress-folder: path '/home/user/toisto' does not exist",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--progress-folder", "/home/user/toisto"])
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.is_dir", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_configure_progress_folder_that_is_not_a_folder(self, sys_stderr_write: Mock) -> None:
        """Test that the progress folder is checked to be a folder."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "error: argument -p/--progress-folder: path '/home/user/toisto' is not a folder",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--extra", "/home/user/extra.json"])
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.resolve", Mock(return_value=Path("/home/user/extra.json")))
    def test_configure_concept_file(self) -> None:
        """Test that a concept file can be configured."""
        expected_namespace = {**self.default_namespace, "extra": [Path("/home/user/extra.json")]}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--extra", "/home/user/toisto"])
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=False))
    @patch("toisto.ui.cli.Path.is_dir", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.resolve", Mock(return_value=Path("/home/user/toisto")))
    def test_configure_concept_folder(self) -> None:
        """Test that a concept folder can be configured."""
        expected_namespace = {**self.default_namespace, "extra": [Path("/home/user/toisto")]}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--extra", "~/toisto/extra.json"])
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.resolve", Mock(return_value=Path("/home/user/toisto/extra.json")))
    def test_configure_concept_file_with_relative_path(self) -> None:
        """Test that a concept file with a relative path can be configured."""
        expected_namespace = {**self.default_namespace, "extra": [Path("/home/user/toisto/extra.json")]}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--extra", "/home/user/extra.json"])
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_configure_non_existing_concept_file(self, sys_stderr_write: Mock) -> None:
        """Test that the concept file is checked for existence."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "error: argument -e/--extra: path '/home/user/extra.json' does not exist",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--extra", "/home/user/extra.json"])
    @patch("toisto.ui.cli.Path.exists", Mock(return_value=True))
    @patch("toisto.ui.cli.Path.is_dir", Mock(return_value=False))
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_configure_not_a_file_or_a_folder(self, sys_stderr_write: Mock) -> None:
        """Test that the concept file is checked for being a file or folder."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "error: argument -e/--extra: path '/home/user/extra.json' is not a file or folder",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--help"])
    @patch("sys.stdout.write")
    def test_configure_help(self, sys_stdout_write: Mock) -> None:
        """Test that the configure help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assert_output(
            f"""{CONFIGURE_USAGE}

{CONFIGURE_DESCRIPTION}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION % ""}
  {EXTRA_OPTION % "none"}
  {PROGRESS_FOLDER}
  {PROGRESS_OPTION % "0"}
  {RETENTION_OPTION}
  {MP3PLAYER_OPTION}
""",
            sys_stdout_write,
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--help"])
    @patch("sys.stdout.write")
    def test_configure_help_with_extra_files(self, sys_stdout_write: Mock) -> None:
        """Test that the configure help message is displayed."""
        config_parser = default_config()
        config_parser.add_section("files")
        config_parser.set("files", "extra1.json", "")
        config_parser.set("files", "extra2.json", "")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser=config_parser))
        self.assert_output(
            f"""{CONFIGURE_USAGE}

{CONFIGURE_DESCRIPTION}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION % ""}
  {EXTRA_OPTION % "extra1.json, extra2.json"}
  {PROGRESS_FOLDER}
  {PROGRESS_OPTION % "0"}
  {RETENTION_OPTION}
  {MP3PLAYER_OPTION}
""",
            sys_stdout_write,
        )


class PracticeCommandTest(ParserTestCase):
    """Unit tests for the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        super().setUp()
        self.default_namespace |= {
            "command": "practice",
            "concepts": [],
            "quiz_type": [],
            "source_language": "fi",
            "target_language": "nl",
            "show_quiz_retention": "no",
        }

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--target", "nl", "--source", "fi"])
    def test_practice_command(self) -> None:
        """Test that the practice command can be specified."""
        self.assertEqual(Namespace(**self.default_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help(self, sys_stdout_write: Mock) -> None:
        """Test that the practice help message is displayed."""
        concepts = {
            Concept(ConceptId("included"), Labels((Label(EN, "included"),)), {}, answer_only=False),
            Concept(
                ConceptId("hyponym"),
                Labels((Label(EN, "hyponym, so not listed"),)),
                {"hypernym": (ConceptId("included"),)},
                answer_only=False,
            ),
            Concept(ConceptId("sentence"), Labels((Label(EN, "Sentence, so not listed."),)), {}, answer_only=False),
            Concept(ConceptId("answer only"), Labels((Label(EN, "answer only, so not listed"),)), {}, answer_only=True),
            Concept(
                ConceptId("concept with plural"),
                Labels(
                    (
                        Label(EN, "singular", GrammaticalForm("singular", "singular")),
                        Label(EN, "plural", GrammaticalForm("singular", "plural")),
                    ),
                ),
                {},
                answer_only=False,
            ),
        }
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(concepts=concepts))
        self.assert_output(
            f"""{PRACTICE_USAGE}

{PRACTICE_DESCRIPTION}

{POSITIONAL_ARGUMENTS % " included, singular"}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION % ""}
  {EXTRA_OPTION % "none"}
  {QUIZ_TYPE_OPTION}
  {PROGRESS_OPTION % "0"}
  {RETENTION_OPTION}
""",
            sys_stdout_write,
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_languages_in_config(self, sys_stdout_write: Mock) -> None:
        """Test that the practice help message is displayed."""
        config_parser = default_config()
        config_parser.add_section("languages")
        config_parser.set("languages", "target", "fi")
        config_parser.set("languages", "source", "nl")
        concepts = {
            Concept(
                ConceptId("included"), Labels((Label(EN, "not included"), Label(FI, "included"))), {}, answer_only=False
            ),
        }
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser, concepts=concepts))
        self.assert_output(
            f"""{PRACTICE_USAGE_OPTIONAL_LANGUAGES}

{PRACTICE_DESCRIPTION}

{POSITIONAL_ARGUMENTS % " included"}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % "default: fi; "}
  {SOURCE_OPTION % "default: nl; "}
  {EXTRA_OPTION % "none"}
  {QUIZ_TYPE_OPTION}
  {PROGRESS_OPTION % "0"}
  {RETENTION_OPTION}
""",
            sys_stdout_write,
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_progress_update_in_config(self, sys_stdout_write: Mock) -> None:
        """Test that the practice help message is displayed."""
        config_parser = default_config()
        config_parser.set("practice", "progress_update", "42")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assert_output(
            f"""{PRACTICE_USAGE}

{PRACTICE_DESCRIPTION}

{POSITIONAL_ARGUMENTS % ""}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION % ""}
  {EXTRA_OPTION % "none"}
  {QUIZ_TYPE_OPTION}
  {PROGRESS_OPTION % 42}
  {RETENTION_OPTION}
""",
            sys_stdout_write,
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "--target", "nl", "--source", "fi"])
    def test_no_command(self) -> None:
        """Test that the practice command is returned if the user did not specify a command."""
        self.assertEqual(Namespace(**self.default_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "practice", "--target", "42", "--source", "@@"])
    @patch("sys.stderr.write")
    def test_invalid_language(self, sys_stderr_write: Mock) -> None:
        """Test that an error message is displayed if an invalid language is supplied."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "invalid choice: '42' (see https://www.iana.org/assignments/language-subtag-registry for valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "fi", "--source", "fi"])
    @patch("sys.stderr.write")
    def test_equal_target_and_source_language(self, sys_stderr_write: Mock) -> None:
        """Test that an error message is displayed if the target and source language are equal."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "toisto: error: target and source language are the same: 'fi' \n",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "fi", "--source", "nl", "foo"])
    @patch("sys.stderr.write")
    def test_invalid_concept(self, sys_stderr_write: Mock) -> None:
        """Test that an error message is displayed if an invalid concept is supplied."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "invalid choice 'foo' (run `toisto practice -h` to see the valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--target", "nl", "--source", "fi", "--progress-update", "5"])
    def test_progress_update(self) -> None:
        """Test that the progress update frequency can be configured."""
        expected_namespace = {**self.default_namespace, "progress_update": 5}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--show-quiz-retention", "yes", "--target", "nl", "--source", "fi"])
    def test_show_quiz_retention(self) -> None:
        """Test that the quiz retention can be shown."""
        expected_namespace = {**self.default_namespace, "show_quiz_retention": "yes"}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "practice", "--quiz-type", "dictate", "--target", "nl", "--source", "fi"])
    def test_quiz_type(self) -> None:
        """Test that a quiz type can be selected."""
        expected_namespace = {**self.default_namespace, "quiz_type": ["dictate"]}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch(
        "sys.argv",
        ["toisto", "practice", "--quiz-type", "dictate", "--quiz-type", "write", "--target", "nl", "--source", "fi"],
    )
    def test_quiz_types(self) -> None:
        """Test that multiple quiz types can be selected."""
        expected_namespace = {**self.default_namespace, "quiz_type": ["dictate", "write"]}
        self.assertEqual(Namespace(**expected_namespace), parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "practice", "--quiz-type", "foo", "--target", "nl", "--source", "fi"])
    @patch("sys.stderr.write")
    def test_incorrect_quiz_type(self, sys_stderr_write: Mock) -> None:
        """Test that an error message is shown when an incorrect quiz type is selected."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "invalid choice 'foo' (run `toisto practice -h` to see the valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )


class ProgressCommandTest(ParserTestCase):
    """Unit tests for the progress command."""

    @patch("sys.argv", ["toisto", "progress", "--help"])
    @patch("sys.stdout.write")
    def test_progress_help(self, sys_stdout_write: Mock) -> None:
        """Test that the progress help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assert_output(
            f"""Usage: toisto progress [-h] -t {{language}} -s {{language}} [-e {{path}}] [-q {{quiz type}}] \
[-S {{option}}] [{{concept}} ...]

Show progress.

{POSITIONAL_ARGUMENTS % ""}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION % ""}
  {EXTRA_OPTION % "none"}
  {QUIZ_TYPE_OPTION}
  -S, --sort {{option}}   how to sort progress information; default: by retention; available options: attempts,
                        retention
""",
            sys_stdout_write,
        )

    @patch("sys.argv", ["toisto", "progress", "--help"])
    @patch("sys.stdout.write")
    def test_progress_help_with_languages_in_config(self, sys_stdout_write: Mock) -> None:
        """Test that the progress help message is displayed."""
        config_parser = default_config()
        config_parser.add_section("languages")
        config_parser.set("languages", "target", "fi")
        config_parser.set("languages", "source", "nl")
        self.maxDiff = None
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assert_output(
            f"""Usage: toisto progress [-h] [-t {{language}}] [-s {{language}}] [-e {{path}}] [-q {{quiz type}}] \
[-S {{option}}] [{{concept}} ...]

Show progress.

{POSITIONAL_ARGUMENTS % ""}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % "default: fi; "}
  {SOURCE_OPTION % "default: nl; "}
  {EXTRA_OPTION % "none"}
  {QUIZ_TYPE_OPTION}
  -S, --sort {{option}}   how to sort progress information; default: by retention; available options: attempts,
                        retention
""",
            sys_stdout_write,
        )


class SelfCommandTest(ParserTestCase):
    """Unit tests for the self command."""

    SELF_HELP = """Usage: toisto self [-h] {upgrade,uninstall,version} ...

Manage Toisto itself.

Options:
  -h, --help            show this help message and exit

Commands:
  {upgrade,uninstall,version}
                        type `toisto self {command} --help` for more information on a command
    upgrade             upgrade Toisto to the latest version
    uninstall           uninstall Toisto, excluding configuration and progress files
    version             show the installed version and the latest version available if it is newer
"""
    SELF_COMMAND_HELP = """Usage: toisto self %s [-h]

%s.

Options:
  -h, --help  show this help message and exit
"""

    @patch("sys.argv", ["toisto", "self"])
    @patch("sys.stderr.write")
    @patch("sys.stdout.write")
    def test_self_command(self, sys_stdout_write: Mock, sys_stderr_write: Mock) -> None:
        """Test that invoking help without arguments prints the help for self."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        sys_stderr_write.assert_not_called()
        self.assert_output(self.SELF_HELP, sys_stdout_write)

    @patch("sys.argv", ["toisto", "self", "--help"])
    @patch("sys.stderr.write")
    @patch("sys.stdout.write")
    def test_self_help(self, sys_stdout_write: Mock, sys_stderr_write: Mock) -> None:
        """Test the help for self."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        sys_stderr_write.assert_not_called()
        self.assert_output(self.SELF_HELP, sys_stdout_write)

    @patch("sys.argv", ["toisto", "self", "upgrade", "--help"])
    @patch("sys.stderr.write")
    @patch("sys.stdout.write")
    def test_self_upgrade_help(self, sys_stdout_write: Mock, sys_stderr_write: Mock) -> None:
        """Test the help for self upgrade."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        sys_stderr_write.assert_not_called()
        expected_message = self.SELF_COMMAND_HELP % ("upgrade", "Upgrade Toisto")
        self.assert_output(expected_message, sys_stdout_write)

    @patch("sys.argv", ["toisto", "self", "uninstall", "--help"])
    @patch("sys.stderr.write")
    @patch("sys.stdout.write")
    def test_self_uninstall_help(self, sys_stdout_write: Mock, sys_stderr_write: Mock) -> None:
        """Test the help for self uninstall."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        sys_stderr_write.assert_not_called()
        expected_message = self.SELF_COMMAND_HELP % ("uninstall", "Uninstall Toisto")
        self.assert_output(expected_message, sys_stdout_write)

    @patch("sys.argv", ["toisto", "self", "version", "--help"])
    @patch("sys.stderr.write")
    @patch("sys.stdout.write")
    def test_self_version_help(self, sys_stdout_write: Mock, sys_stderr_write: Mock) -> None:
        """Test the help for self version."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        sys_stderr_write.assert_not_called()
        expected_message = self.SELF_COMMAND_HELP % ("version", "Show the current version")
        self.assert_output(expected_message, sys_stdout_write)


class VersionTest(ParserTestCase):
    """Unit tests for the version option."""

    @patch("sys.argv", ["toisto", "--version"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_long_option(self, print_message: Mock) -> None:
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(f"v{VERSION}\n", print_message.call_args_list[0][0][0])

    @patch("sys.argv", ["toisto", "-V"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_short_option(self, print_message: Mock) -> None:
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(f"v{VERSION}\n", print_message.call_args_list[0][0][0])

    @patch("sys.argv", ["toisto", "--version"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_when_newer_version_available(self, print_message: Mock) -> None:
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(latest_version="v9999"))
        self.assertEqual(
            f"v{VERSION} (v9999 is available, run toisto self upgrade to install)\n",
            print_message.call_args_list[0][0][0],
        )


class PracticeableConceptsTest(unittest.TestCase):
    """Unit tests for the practiceable concepts filter."""

    def test_empty_set(self):
        """Test that filtering the practiceable concepts from an empty set results in an empty set."""
        self.assertEqual(set(), practiceable_concepts(set()))

    def test_regular_concept(self):
        """Test that a regular concept can be practiced."""
        concept = Concept(ConceptId("concept"), Labels((Label(EN, "concept"),)), {}, answer_only=False)
        self.assertEqual({concept}, practiceable_concepts({concept}))

    def test_answer_only(self):
        """Test that an answer-only concept is not practiceable."""
        answer_only = Concept(ConceptId("concept"), Labels((Label(EN, "concept"),)), {}, answer_only=True)
        self.assertEqual(set(), practiceable_concepts({answer_only}))

    def test_sentence(self):
        """Test that a sentence is not practiceable."""
        sentence = Concept(ConceptId("concept"), Labels((Label(EN, "Concept."),)), {}, answer_only=False)
        self.assertEqual(set(), practiceable_concepts({sentence}))

    def test_hypernym_and_hyponym(self):
        """Test that a hypernym is practiceable and its hyponym is not."""
        hypernym = Concept(ConceptId("hypernym"), Labels((Label(EN, "hypernym"),)), {}, answer_only=False)
        hyponym = Concept(
            ConceptId("hyponym"),
            Labels((Label(EN, "hyponym"),)),
            {"hypernym": (ConceptId("hypernym"),)},
            answer_only=False,
        )
        self.assertEqual({hypernym}, practiceable_concepts({hypernym, hyponym}))

    def test_concept_that_both_hypernym_and_hyponym(self):
        """Test that a concept that is both hypernym and hyponym is practiceable."""
        hypernym = Concept(ConceptId("hypernym"), Labels((Label(EN, "hypernym"),)), {}, answer_only=False)
        both = Concept(
            ConceptId("both"), Labels((Label(EN, "both"),)), {"hypernym": (ConceptId("hypernym"),)}, answer_only=False
        )
        hyponym = Concept(
            ConceptId("hyponym"), Labels((Label(EN, "hyponym"),)), {"hypernym": (ConceptId("both"),)}, answer_only=False
        )
        self.assertEqual({hypernym, both}, practiceable_concepts({hypernym, both, hyponym}))
