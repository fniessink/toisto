"""Unit tests for the practice command."""

import unittest
from unittest.mock import call, patch, Mock

from toisto.command import practice
from toisto.model import Progress, Quiz
from toisto.output import DONE, TRY_AGAIN


@patch("os.system", Mock())
class PracticeTest(unittest.TestCase):
    """Test the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.quiz = Quiz("fi", "nl", "Terve", ["Hoi"])

    @patch("builtins.input", Mock(side_effect=["hoi\n", EOFError]))
    def test_quiz(self):
        """Test that the user is quizzed."""
        with patch("builtins.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        with patch("builtins.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        with patch("builtins.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertIn(call(DONE), patched_print.call_args_list)
