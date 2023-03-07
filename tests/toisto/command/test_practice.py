"""Unit tests for the practice command."""

from configparser import ConfigParser
from unittest.mock import MagicMock, Mock, call, patch

from toisto.command.practice import practice
from toisto.model.language.concept import ConceptId
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.topic import Topic, Topics
from toisto.ui.dictionary import linkify
from toisto.ui.text import DONE, TRY_AGAIN

from ...base import ToistoTestCase


@patch("os.system", Mock())
@patch("pathlib.Path.open", MagicMock())
@patch("gtts.gTTS.save", Mock())
class PracticeTest(ToistoTestCase):
    """Test the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.concept = self.create_concept(ConceptId("hi"))
        quiz = self.create_quiz(self.concept, "fi", "nl", "Terve", ["Hoi"])
        topics = Topics({Topic("topic", (), {quiz})})
        self.progress = Progress({}, topics)

    def practice(self, progress: Progress | None = None) -> Mock:
        """Run the practice command and return the patch print statement."""
        config = ConfigParser()
        config.add_section("commands")
        config.set("commands", "mp3player", "mpg123")
        with patch("rich.console.Console.print") as patched_print:
            practice(progress or self.progress, config)
        return patched_print

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_quiz(self):
        """Test that the user is quizzed."""
        patched_print = self.practice()
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["\n", "Hoi\n"]))
    @patch("builtins.print")
    def test_quiz_empty_answer(self, mock_print: Mock):
        """Test that the user is quizzed."""
        self.practice()
        self.assertEqual([call("\x1b[F", end="")], mock_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_question(self):
        """Test that the question is printed."""
        patched_print = self.practice()
        self.assertIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_listen(self):
        """Test that the question is not printed on a listening quiz."""
        quiz = self.create_quiz(self.concept, "fi", "fi", "Terve", ["Terve"], "listen")
        topics = Topics({Topic("topic", (), {quiz})})
        patched_print = self.practice(Progress({}, topics))
        self.assertNotIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_quiz_non_translate(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quiz = self.create_quiz(self.concept, "fi", "fi", "Terve", ["Terve"], "listen", meanings=("Hoi",))
        topics = Topics({Topic("topic", (), {quiz})})
        patched_print = self.practice(Progress({}, topics))
        expected_text = f'✅ Correct.\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n'
        self.assertIn(call(expected_text), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Talot\n"))
    def test_quiz_with_multiple_meanings(self):
        """Test that the translation is not printed on a non-translate quiz."""
        concept = self.create_concept("house")
        quiz = self.create_quiz(concept, "fi", "fi", "Talo", ["Talot"], "pluralize", meanings=("Huis", "Huizen"))
        topics = Topics({Topic("topic", (), {quiz})})
        patched_print = self.practice(Progress({}, topics))
        expected_text = f'✅ Correct.\n[secondary]Meaning "{linkify("Huis")}", "{linkify("Huizen")}".[/secondary]\n'
        self.assertIn(call(expected_text), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "Hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        patched_print = self.practice()
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["?\n", EOFError]))
    def test_quiz_skip_on_first_attempt(self):
        """Test that the user is quizzed."""
        patched_print = self.practice()
        self.assertNotIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(f'The correct answer is "{linkify("Hoi")}".\n'), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["first attempt", "?\n", EOFError]))
    def test_quiz_skip_on_second_attempt(self):
        """Test that the user is quizzed."""
        patched_print = self.practice()
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(f'The correct answer is "{linkify("Hoi")}".\n'), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        patched_print = self.practice()
        self.assertIn(call(DONE), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=[EOFError]))
    def test_exit(self):
        """Test that the user can quit."""
        patched_print = self.practice()
        self.assertEqual(call(), patched_print.call_args_list[-1])
