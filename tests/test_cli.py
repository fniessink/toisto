"""Unit tests for the CLI module."""

import unittest
from unittest.mock import Mock, patch

from toisto.cli import parser


class ParserTest(unittest.TestCase):
    """Unit tests for the CLI parser."""

    @patch("sys.stdout", Mock())
    def test_help(self):
        """Test that a help message is displayed."""
        self.assertRaises(SystemExit, parser.parse_args, ["--help"])
