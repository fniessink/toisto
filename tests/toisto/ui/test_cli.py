"""Unit tests for the CLI module."""

import os
import re
import unittest
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from unittest.mock import Mock, patch

from toisto.model.language import Language
from toisto.model.language.concept import Concept, ConceptId, RelatedConcepts
from toisto.model.language.label import Label
from toisto.model.topic.topic import Topic
from toisto.ui.cli import create_argument_parser, parse_arguments


class ParserTest(unittest.TestCase):
    """Unit tests for the CLI parser."""

    ANSI_ESCAPE_CODES = re.compile(r"\x1B\[\d+(;\d+){0,2}m")

    def setUp(self) -> None:
        """Set up the test fixtures."""
        os.environ["COLUMNS"] = "120"  # Set the width of the terminal to match the formatting of the expected results

    def argument_parser(
        self,
        config_parser: ConfigParser | None = None,
        concepts: set[Concept] | None = None,
        topics: set[Topic] | None = None,
    ) -> ArgumentParser:
        """Create the argument parser."""
        with patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name="v9999")])))):
            return create_argument_parser(config_parser or ConfigParser(), concepts, topics)

    @patch("sys.argv", ["toisto", "--help"])
    @patch("sys.stdout.write")
    def test_help(self, sys_stdout_write: Mock):
        """Test that the help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            """Usage: toisto [-h] [-V] {practice,progress,topics} ...

Toisto is a command-line terminal app to practice languages.

Options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit

Commands:
  {practice,progress,topics}
                        default: practice; type `toisto {command} --help` for more information on a command
    practice            practice a language, for example type `toisto practice --target fi --source en` to practice
                        Finnish from English
    progress            show progress, for example `toisto progress --target fi --source en` shows progress on
                        practicing Finnish from English
    topics              show topics, for example `toisto topics --topic nature` shows the contents of the nature topic

See https://github.com/fniessink/toisto/blob/main/README.md for more information.
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "nl", "--source", "fi"])
    def test_practice_command(self):
        """Test that the practice command can be specified."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            topic=[],
            topic_file=[],
            concept=[],
            concept_file=[],
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help(self, sys_stdout_write: Mock):
        """Test that the practice help message is displayed."""
        related = RelatedConcepts(None, (), {}, (), ())
        concepts = {
            Concept(ConceptId("foo"), {Language("en"): (Label("foo"),)}, {}, related, False),
            Concept(ConceptId("bar"), {Language("en"): (Label("bar"),)}, {}, related, False),
        }
        topics = {Topic("T1", frozenset([ConceptId("foo")])), Topic("T2", frozenset([ConceptId("bar")]))}
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(concepts=concepts, topics=topics))
        self.assertEqual(
            """Usage: toisto practice [-h] -t {language} -s {language} [-c {concept} | -T {topic}] [-C {concept file}]
                       [-o {topic file}]

Practice a language.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts: bar, foo
  -T, --topic {topic}   topic to use, can be repeated; default: all; built-in topics: T1, T2
  -C, --concept-file {concept file}
                        extra concept file to use, can be repeated
  -o, --topic-file {topic file}
                        extra topic file to use, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_default_languages_in_config(self, sys_stdout_write: Mock):
        """Test that the practice help message is displayed."""
        config_parser = ConfigParser()
        config_parser.add_section("languages")
        config_parser.set("languages", "target", "fi")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assertEqual(
            """Usage: toisto practice [-h] [-t {language}] -s {language} [-c {concept} | -T {topic}] [-C {concept file}]
                       [-o {topic file}]

Practice a language.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; default: fi; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -T, --topic {topic}   topic to use, can be repeated; default: all; built-in topics:
  -C, --concept-file {concept file}
                        extra concept file to use, can be repeated
  -o, --topic-file {topic file}
                        extra topic file to use, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_default_levels_in_config(self, sys_stdout_write: Mock):
        """Test that the practice help message is displayed."""
        config_parser = ConfigParser()
        config_parser.add_section("languages")
        config_parser.set("languages", "levels", "A1 A2")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assertEqual(
            """Usage: toisto practice [-h] -t {language} -s {language} [-c {concept} | -T {topic}] [-C {concept file}]
                       [-o {topic file}]

Practice a language.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -T, --topic {topic}   topic to use, can be repeated; default: all; built-in topics:
  -C, --concept-file {concept file}
                        extra concept file to use, can be repeated
  -o, --topic-file {topic file}
                        extra topic file to use, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "progress", "--help"])
    @patch("sys.stdout.write")
    def test_progress_help(self, sys_stdout_write: Mock):
        """Test that the progress help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            """Usage: toisto progress [-h] -t {language} -s {language} [-c {concept} | -T {topic}] [-C {concept file}]
                       [-o {topic file}] [-S {option}]

Show progress.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -T, --topic {topic}   topic to use, can be repeated; default: all; built-in topics:
  -C, --concept-file {concept file}
                        extra concept file to use, can be repeated
  -o, --topic-file {topic file}
                        extra topic file to use, can be repeated
  -S, --sort {option}   how to sort progress information; default: by retention; available options: attempts,
                        retention
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "topics", "--help"])
    @patch("sys.stdout.write")
    def test_topics_help(self, sys_stdout_write: Mock):
        """Test that the topics help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            """Usage: toisto topics [-h] -t {language} -s {language} [-c {concept} | -T {topic}] [-C {concept file}]
                     [-o {topic file}]

Show topics.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -T, --topic {topic}   topic to use, can be repeated; default: all; built-in topics:
  -C, --concept-file {concept file}
                        extra concept file to use, can be repeated
  -o, --topic-file {topic file}
                        extra topic file to use, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "--target", "nl", "--source", "fi"])
    def test_no_command(self):
        """Test that the practice command is returned if the user did not specify a command."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            topic=[],
            topic_file=[],
            concept=[],
            concept_file=[],
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "--version"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_long_option(self, print_message: Mock):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "-V"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_short_option(self, print_message: Mock):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "practice", "--target", "42", "--source", "@@"])
    @patch("sys.stderr.write")
    def test_invalid_language(self, sys_stderr_write: Mock):
        """Test that an error message is displayed if an invalid language is supplied."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "invalid choice: '42' (see https://www.iana.org/assignments/language-subtag-registry for valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "fi", "--source", "fi"])
    @patch("sys.stderr.write")
    def test_equal_target_and_source_language(self, sys_stderr_write: Mock):
        """Test that an error message is displayed if the target and source language are equal."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "toisto: error: target and source language are the same: 'fi' \n",
            sys_stderr_write.call_args_list[1][0][0],
        )
