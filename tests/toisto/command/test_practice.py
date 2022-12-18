"""Unit tests for the practice command."""

from unittest.mock import call, patch, Mock, MagicMock

from toisto.command import practice
from toisto.model import Progress, Topic, Topics
from toisto.model.model_types import ConceptId
from toisto.ui.text import DONE, TRY_AGAIN, linkify

from ..base import ToistoTestCase


@patch("os.system", Mock())
@patch("pathlib.Path.open", MagicMock())
@patch("gtts.gTTS.save", Mock())
class PracticeTest(ToistoTestCase):
    """Test the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.quiz = self.create_quiz(ConceptId("hi"), "fi", "nl", "Terve", ["Hoi"])
        self.topics = Topics(set([Topic("topic", set([self.quiz]))]))

    def practice(self):
        """Run the practice command and return the patch print statement."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        return patched_print

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz(self):
        """Test that the user is quizzed."""
        patched_print = self.practice()
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["\n", "hoi\n"]))
    @patch("builtins.print")
    def test_quiz_empty_answer(self, mock_print):
        """Test that the user is quizzed."""
        with patch("rich.console.Console.print"):
            practice(self.topics, Progress({}))
        self.assertEqual([call("\x1b[F", end="")], mock_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_question(self):
        """Test that the question is printed."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        self.assertIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_listen(self):
        """Test that the question is not printed on a listening quiz."""
        quiz = self.create_quiz("hello", "fi", "fi", "Terve", ["Terve"], "listen")
        topics = Topics(set([Topic("topic", set([quiz]))]))
        with patch("rich.console.Console.print") as patched_print:
            practice(topics, Progress({}))
        self.assertNotIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_quiz_non_translate(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quiz = self.create_quiz("hello", "fi", "fi", "Terve", ["Terve"], "listen", meanings=("Hoi",))
        topics = Topics(set([Topic("topic", set([quiz]))]))
        with patch("rich.console.Console.print") as patched_print:
            practice(topics, Progress({}))
        self.assertIn(
            call(f'✅ Correct.\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n'), patched_print.call_args_list
        )

    @patch("builtins.input", Mock(return_value="Talot\n"))
    def test_quiz_with_multiple_meanings(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quiz = self.create_quiz("house", "fi", "fi", "Talo", ["Talot"], "pluralize", meanings=("Huis", "Huizen"))
        topics = Topics(set([Topic("topic", set([quiz]))]))
        with patch("rich.console.Console.print") as patched_print:
            practice(topics, Progress({}))
        self.assertIn(call(
            f"""✅ Correct.\n[secondary]Meaning "{linkify("Huis")}", "{linkify("Huizen")}".[/secondary]\n"""),
            patched_print.call_args_list
        )

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["?\n", EOFError]))
    def test_quiz_skip_on_first_attempt(self):
        """Test that the user is quizzed."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        self.assertNotIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(f'The correct answer is "{linkify("Hoi")}".\n'),
        patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["first attempt", "?\n", EOFError]))
    def test_quiz_skip_on_second_attempt(self):
        """Test that the user is quizzed."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(f'The correct answer is "{linkify("Hoi")}".\n'), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        self.assertIn(call(DONE), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=[EOFError]))
    def test_exit(self):
        """Test that the user can quit."""
        with patch("rich.console.Console.print") as patched_print:
            practice(self.topics, Progress({}))
        self.assertEqual(call(), patched_print.call_args_list[-1])
