"""Unit tests for the practice command."""

from configparser import ConfigParser
from unittest.mock import MagicMock, Mock, call, patch

from toisto.command.practice import practice
from toisto.model.language import Language
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.ui.dictionary import linkify
from toisto.ui.style import DELETED, SECONDARY
from toisto.ui.text import CORRECT, DONE, INCORRECT, TRY_AGAIN, TRY_AGAIN_IN_ANSWER_LANGUAGE, console

from ...base import ToistoTestCase


@patch("pathlib.Path.open", MagicMock())
@patch("toisto.ui.speech.gTTS", Mock())
@patch("toisto.ui.speech.Popen", Mock())
class PracticeTest(ToistoTestCase):
    """Test the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        super().setUp()
        self.concept = self.create_concept("hi", dict(fi="Terve", nl="Hoi"))
        self.quizzes = create_quizzes(self.fi, self.nl, self.concept).by_quiz_type("read")

    def practice(self, quizzes: Quizzes) -> Mock:
        """Run the practice command and return the patch print statement."""
        config = ConfigParser()
        config.add_section("commands")
        config.set("commands", "mp3player", "mpg123")
        progress = Progress({}, Language("fi"), quizzes)
        with patch("rich.console.Console.print") as patched_print:
            practice(console.print, progress, config)
        return patched_print

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_quiz(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(CORRECT), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Hoi \n"))
    def test_answer_with_extra_whitespace(self):
        """Test that whitespace is stripped from answers."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(CORRECT), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["H o i\n", "Ho i\n"]))
    def test_answer_with_spaces(self):
        """Test that answers with spaces inside are not considered correct."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(
            call(f'{INCORRECT}The correct answer is "Ho[{DELETED}]_[/{DELETED}]i".\n'),
            patched_print.call_args_list,
        )

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_answer_with_question(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Dutch")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_answer_with_question_listen_quiz(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        quizzes = create_quizzes(Language("fi"), Language("nl"), self.concept).by_quiz_type("dictate")
        patched_print = self.practice(quizzes)
        self.assertIn(call(TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Finnish")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="talo\n"))
    def test_answer_with_question_grammar_quiz(self):
        """Test that the language to answer is not stressed, when the user answers a grammar quiz with the question."""
        concept = self.create_concept("house", dict(singular=dict(fi="talo"), plural=dict(fi="talot")))
        quizzes = create_quizzes(self.fi, self.fi, concept).by_quiz_type("pluralize")
        patched_print = self.practice(quizzes)
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["\n", "Hoi\n"]))
    @patch("builtins.print")
    def test_quiz_empty_answer(self, mock_print: Mock) -> None:
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
        quizzes = create_quizzes(self.fi, self.fi, self.concept).by_quiz_type("dictate")
        patched_print = self.practice(quizzes)
        self.assertNotIn(call(linkify("Terve")), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_quiz_non_translate(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quizzes = create_quizzes(self.fi, self.nl, self.concept).by_quiz_type("dictate")
        patched_print = self.practice(quizzes)
        expected_text = f'{CORRECT}[{SECONDARY}]Meaning "{linkify("Hoi")}".[/{SECONDARY}]\n'
        self.assertIn(call(expected_text), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="talot\n"))
    def test_quiz_with_multiple_meanings(self):
        """Test that the translation is not printed on a non-translate quiz."""
        concept = self.create_concept(
            "house",
            dict(singular=dict(fi="talo", nl="huis"), plural=dict(fi="talot", nl="huizen")),
        )
        quizzes = create_quizzes(self.fi, self.nl, concept).by_quiz_type("pluralize")
        patched_print = self.practice(Quizzes(quizzes))
        expected_call = call(
            f'{CORRECT}[{SECONDARY}]Meaning "{linkify("huis")}", respectively "{linkify("huizen")}".[/{SECONDARY}]\n',
        )
        self.assertIn(expected_call, patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="vieressä\n"))
    def test_quiz_with_example(self):
        """Test that the example is shown after the quiz."""
        concept = self.create_concept("next to", dict(example="the museum is next to the church", fi="vieressä"))
        self.create_concept("the museum is next to the church", dict(fi="Museo on kirkon vieressä."))
        quizzes = create_quizzes(self.fi, self.fi, concept).by_quiz_type("dictate")
        patched_print = self.practice(Quizzes(quizzes))
        expected_call = call(
            f'{CORRECT}[{SECONDARY}]Meaning "{linkify("vieressä")}".[/{SECONDARY}]\n'
            f'[{SECONDARY}]Example: Museo on kirkon vieressä.[/{SECONDARY}]\n'
        )
        self.assertIn(expected_call, patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="musta\n"))
    def test_quiz_with_examples(self):
        """Test that the examples are shown after the quiz."""
        examples = ["the car is black", "the cars are black"]
        concept = self.create_concept("black", dict(example=examples, fi="musta"))
        self.create_concept("the car is black", dict(fi="Auto on musta."))
        self.create_concept("the cars are black", dict(fi="Autot ovat mustia."))
        quizzes = create_quizzes(self.fi, self.fi, concept).by_quiz_type("dictate")
        patched_print = self.practice(Quizzes(quizzes))
        expected_call = call(
            f'{CORRECT}[{SECONDARY}]Meaning "{linkify("musta")}".[/{SECONDARY}]\n'
            f'[{SECONDARY}]Examples:\n- Auto on musta.\n- Autot ovat mustia.[/{SECONDARY}]\n'
        )
        self.assertIn(expected_call, patched_print.call_args_list)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "Hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assertIn(call(TRY_AGAIN), patched_print.call_args_list)
        self.assertIn(call(CORRECT), patched_print.call_args_list)

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
