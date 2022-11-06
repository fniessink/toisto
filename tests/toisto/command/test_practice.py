"""Unit tests for the practice command."""

from unittest.mock import call, patch, Mock, MagicMock

from toisto.command import practice
from toisto.model import Progress
from toisto.output import DONE, TRY_AGAIN

from ..base import ToistoTestCase


@patch("os.system", Mock())
@patch("pathlib.Path.open", MagicMock())
class PracticeTest(ToistoTestCase):
    """Test the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz(self):
        """Test that the user is quizzed."""
        with patch("rich.console.Console.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        with patch("rich.console.Console.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        with patch("rich.console.Console.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertIn(call(DONE), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=[EOFError]))
    def test_exit(self):
        """Test that the user can quit."""
        with patch("rich.console.Console.print") as patched_print:
            practice([self.quiz], Progress({}))
        self.assertEqual(call(), patched_print.call_args_list[-1])
