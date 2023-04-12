"""Unit tests for the practice command."""

from configparser import ConfigParser
from typing import cast
from unittest.mock import MagicMock, Mock, call, patch

from toisto.command.practice import practice
from toisto.model.language import Language
from toisto.model.language.concept import ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
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
        self.concept = create_concept(ConceptId("hi"), cast(ConceptDict, dict(fi="Terve", nl="Hoi")))
        self.quizzes = create_quizzes(Language("fi"), Language("nl"), self.concept).by_quiz_type("read")
        self.progress = Progress({}, Language("fi"))

    def practice(self, quizzes: Quizzes) -> Mock:
        """Run the practice command and return the patch print statement."""
        config = ConfigParser()
        config.add_section("commands")
        config.set("commands", "mp3player", "mpg123")
        with patch("rich.console.Console.print") as patched_print:
            practice(quizzes, self.progress, config)
        return patched_print

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_quiz(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["\n", "Hoi\n"]))
    @patch("builtins.print")
    def test_quiz_empty_answer(self, mock_print: Mock):
        """Test that the user is quizzed."""
        self.practice(self.quizzes)
        self.assertEqual([call("\x1b[F", end="")], mock_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_question(self):
        """Test that the question is printed."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_listen(self):
        """Test that the question is not printed on a listening quiz."""
        quizzes = create_quizzes("fi", "fi", self.concept).by_quiz_type("listen")
        patched_print = self.practice(quizzes)
        self.assertNotIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_quiz_non_translate(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quizzes = create_quizzes("fi", "nl", self.concept).by_quiz_type("listen")
        patched_print = self.practice(quizzes)
        expected_text = f'✅ Correct.\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n'
        self.assertIn(call(expected_text), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="talot\n"))
    def test_quiz_with_multiple_meanings(self):
        """Test that the translation is not printed on a non-translate quiz."""
        concept = create_concept(
            "house",
            dict(singular=dict(fi="talo", nl="huis"), plural=dict(fi="talot", nl="huizen")),
        )
        quizzes = create_quizzes("fi", "nl", concept).by_quiz_type("pluralize")
        patched_print = self.practice(Quizzes(quizzes))
        expected_text = f'✅ Correct.\n[secondary]Meaning "{linkify("huis")}", "{linkify("huizen")}".[/secondary]\n'
        self.assertIn(call(expected_text), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "Hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call("✅ Correct.\n"), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["?\n", EOFError]))
    def test_quiz_skip_on_first_attempt(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assertNotIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(f'The correct answer is "{linkify("Hoi")}".\n'), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["first attempt", "?\n", EOFError]))
    def test_quiz_skip_on_second_attempt(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(f'The correct answer is "{linkify("Hoi")}".\n'), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(DONE), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=[EOFError]))
    def test_exit(self):
        """Test that the user can quit."""
        patched_print = self.practice(self.quizzes)
        self.assertEqual(call(), patched_print.call_args_list[-1])
