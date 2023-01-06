"""Unit tests for the CLI module."""

import argparse
import unittest
from unittest.mock import Mock, patch

from toisto.ui.cli import argument_parser


class ParserTest(unittest.TestCase):
    """Unit tests for the CLI parser."""

    @patch("sys.stdout", Mock())
    def test_help(self):
        """Test that a help message is displayed."""
        self.assertRaises(SystemExit, argument_parser.parse_args, ["--help"])

    @patch.object(argparse.ArgumentParser, "_print_message")
    def test_version(self, write):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, argument_parser.parse_args, ["--version"])
        self.assertEqual("0.6.0\n", write.call_args_list[0][0][0])
