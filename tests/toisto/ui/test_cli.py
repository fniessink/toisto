"""Unit tests for the CLI module."""

import argparse
import unittest
from unittest.mock import Mock, patch

from toisto.ui.cli import create_argument_parser


class ParserTest(unittest.TestCase):
    """Unit tests for the CLI parser."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        with patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name="v9999")])))):
            self.argument_parser = create_argument_parser()

    @patch("sys.stdout", Mock())
    def test_help(self):
        """Test that a help message is displayed."""
        self.assertRaises(SystemExit, self.argument_parser.parse_args, ["--help"])

    @patch("sys.stderr", Mock())
    def test_no_args(self):
        """Test that a help message is displayed if no arguments are supplied."""
        self.assertRaises(SystemExit, self.argument_parser.parse_args, [])

    @patch.object(argparse.ArgumentParser, "_print_message")
    def test_version(self, write):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, self.argument_parser.parse_args, ["--version"])
        self.assertRegex(write.call_args_list[0][0][0], r"\d+.\d+.\d+")
