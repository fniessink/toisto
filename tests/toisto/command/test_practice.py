"""Unit tests for the practice command."""

from unittest.mock import MagicMock, Mock, call, patch

from toisto.command.practice import practice
from toisto.model.language import FI
from toisto.model.language.label import Label
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.persistence.config import default_config
from toisto.ui.dictionary import linkified
from toisto.ui.style import DELETED, SECONDARY
from toisto.ui.text import DONE, Feedback, ProgressUpdate, console

from ...base import FI_NL, NL_FI, ToistoTestCase


@patch("pathlib.Path.open", MagicMock())
@patch("toisto.ui.speech.gTTS", Mock())
@patch("toisto.ui.speech.Popen", Mock())
class PracticeTest(ToistoTestCase):
    """Test the practice command."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        super().setUp()
        self.language_pair = FI_NL
        self.concept = self.create_concept("hi", dict(fi="Terve!", nl="Hoi!"))
        self.quizzes = create_quizzes(self.language_pair, self.concept).by_quiz_type("read")

    def progress(self, quizzes: Quizzes) -> Progress:
        """Create the progress tracker."""
        return Progress({}, self.language_pair.target, quizzes)

    def practice(self, quizzes: Quizzes, progress: Progress | None = None, progress_update: int = 0) -> Mock:
        """Run the practice command and return the patched print statement."""
        config = default_config()
        config.set("commands", "mp3player", "mpg123")
        if progress is None:
            progress = self.progress(quizzes)
        with patch("rich.console.Console.print") as patched_print:
            practice(console.print, self.language_pair, progress, config, progress_update)
        return patched_print

    def assert_printed(self, output: str, patched_print: Mock) -> None:
        """Assert that the argument is in the call arguments list of the patched print method."""
        self.assertIn(call(output), patched_print.call_args_list)

    def assert_not_printed(self, argument: str, patched_print: Mock) -> None:
        """Assert that the argument is not in the call arguments list of the patched print method."""
        self.assertNotIn(call(argument), patched_print.call_args_list)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_quiz(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assert_printed(Feedback.CORRECT, patched_print)

    @patch("builtins.input", Mock(return_value="Hoi \n"))
    def test_answer_with_extra_whitespace(self):
        """Test that whitespace is stripped from answers."""
        patched_print = self.practice(self.quizzes)
        self.assert_printed(Feedback.CORRECT, patched_print)

    @patch("builtins.input", Mock(side_effect=["H o i!\n", "Ho i!\n"]))
    def test_answer_with_spaces(self):
        """Test that answers with spaces inside are not considered correct."""
        patched_print = self.practice(self.quizzes)
        self.assert_printed(Feedback.TRY_AGAIN, patched_print)
        self.assert_printed(
            f"{Feedback.INCORRECT}The correct answer is 'Ho[{DELETED}]_[/{DELETED}]i!'\n",
            patched_print,
        )

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_answer_with_question(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        self.assert_printed(Feedback.TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Dutch"), self.practice(self.quizzes))

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_answer_with_question_listen_quiz(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        quizzes = create_quizzes(self.language_pair, self.concept).by_quiz_type("dictate")
        self.assert_printed(Feedback.TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Finnish"), self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="talo\n"))
    def test_answer_with_question_grammar_quiz(self):
        """Test that the language to answer is not stressed, when the user answers a grammar quiz with the question."""
        concept = self.create_concept("house", dict(singular=dict(fi="talo"), plural=dict(fi="talot")))
        quizzes = create_quizzes(self.language_pair, concept).by_quiz_type("pluralize")
        self.assert_printed(Feedback.TRY_AGAIN, self.practice(quizzes))

    @patch("builtins.input", Mock(side_effect=["\n", "Hoi\n"]))
    @patch("builtins.print")
    def test_quiz_empty_answer(self, mock_print: Mock) -> None:
        """Test that the user is quizzed."""
        self.practice(self.quizzes)
        self.assertEqual([call("\x1b[F", end="")], mock_print.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_question(self):
        """Test that the question is printed."""
        self.assert_printed(linkified("Terve!"), self.practice(self.quizzes))

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_listen(self):
        """Test that the question is not printed on a listening quiz."""
        quizzes = create_quizzes(self.language_pair, self.concept).by_quiz_type("dictate")
        self.assert_not_printed(linkified("Terve"), self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_quiz_non_translate(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quizzes = create_quizzes(self.language_pair, self.concept).by_quiz_type("dictate")
        expected_text = f"{Feedback.CORRECT}[{SECONDARY}]Meaning '{linkified('Hoi!')}'[/{SECONDARY}]\n"
        self.assert_printed(expected_text, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="talot\n"))
    def test_quiz_with_multiple_meanings(self):
        """Test that the translation is not printed on a non-translate quiz."""
        concept = self.create_concept(
            "house",
            dict(singular=dict(fi="talo", nl="huis"), plural=dict(fi="talot", nl="huizen")),
        )
        quizzes = create_quizzes(self.language_pair, concept).by_quiz_type("pluralize")
        expected_argument = (
            f"{Feedback.CORRECT}[{SECONDARY}]Meaning '{linkified('huis')}', "
            f"respectively '{linkified('huizen')}'.[/{SECONDARY}]\n"
        )
        self.assert_printed(expected_argument, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="vieressä\n"))
    def test_quiz_with_example(self):
        """Test that the example is shown after the quiz."""
        concept = self.create_concept(
            "next to",
            dict(example="the museum is next to the church", fi="vieressä", nl="naast"),
        )
        self.create_concept(
            "the museum is next to the church",
            dict(fi="Museo on kirkon vieressä.", nl="Het museum is naast de kerk."),
        )
        quizzes = create_quizzes(self.language_pair, concept).by_quiz_type("dictate")
        expected_argument = (
            f"{Feedback.CORRECT}[{SECONDARY}]Meaning '{linkified('naast')}'.[/{SECONDARY}]\n"
            f"[{SECONDARY}]Example: 'Museo on kirkon vieressä.' meaning 'Het museum is naast de kerk.'[/{SECONDARY}]\n"
        )
        self.assert_printed(expected_argument, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="musta\n"))
    def test_quiz_with_multiple_examples(self):
        """Test that the examples are shown after the quiz."""
        examples = ["the car is black", "the cars are black"]
        concept = self.create_concept("black", dict(example=examples, fi="musta", nl="zwart"))
        self.create_concept("the car is black", dict(fi="Auto on musta.", nl="De auto is zwart."))
        self.create_concept("the cars are black", dict(fi="Autot ovat mustia.", nl="De auto's zijn zwart."))
        quizzes = create_quizzes(self.language_pair, concept).by_quiz_type("dictate")
        expected_argument = (
            f"{Feedback.CORRECT}[{SECONDARY}]Meaning '{linkified('zwart')}'.[/{SECONDARY}]\n"
            f"[{SECONDARY}]Examples:\n- 'Auto on musta.' meaning 'De auto is zwart.'\n"
            f"- 'Autot ovat mustia.' meaning 'De auto's zijn zwart.'[/{SECONDARY}]\n"
        )
        self.assert_printed(expected_argument, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="pöytävalaisin\n"))
    def test_quiz_with_example_with_synonyms_in_the_target_language(self):
        """Test that all synonyms of the example are shown after the quiz."""
        concept = self.create_concept(
            "table lamp",
            dict(example="I am looking for a table lamp", fi=["pöytälamppu", "pöytävalaisin"], nl="de tafellamp"),
        )
        self.create_concept(
            "I am looking for a table lamp",
            dict(fi=["Minä etsin pöytälamppua.", "Minä etsin pöytävalaisinta."], nl="Ik zoek een tafellamp."),
        )
        quizzes = create_quizzes(self.language_pair, concept).by_quiz_type("dictate")
        quizzes = Quizzes(quiz for quiz in quizzes if quiz.answer == Label(FI, "pöytävalaisin"))
        expected_argument = (
            f"{Feedback.CORRECT}[{SECONDARY}]Meaning '{linkified('de tafellamp')}'.[/{SECONDARY}]\n"
            f"[{SECONDARY}]Examples:\n- 'Minä etsin pöytälamppua.' meaning 'Ik zoek een tafellamp.'\n"
            f"- 'Minä etsin pöytävalaisinta.' meaning 'Ik zoek een tafellamp.'[/{SECONDARY}]\n"
        )
        self.assert_printed(expected_argument, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="de tafellamp\n"))
    def test_quiz_with_example_with_synonyms_in_the_source_language(self):
        """Test that all synonyms of the example are shown after the quiz."""
        self.language_pair = NL_FI
        concept = self.create_concept(
            "table lamp",
            dict(example="I am looking for a table lamp", fi=["pöytälamppu", "pöytävalaisin"], nl="de tafellamp"),
        )
        self.create_concept(
            "I am looking for a table lamp",
            dict(fi=["Minä etsin pöytälamppua.", "Minä etsin pöytävalaisinta."], nl="Ik zoek een tafellamp."),
        )
        quizzes = create_quizzes(self.language_pair, concept).by_quiz_type("dictate")
        expected_argument = (
            f"{Feedback.CORRECT}[{SECONDARY}]Meaning '{linkified('pöytälamppu')}' and "
            f"'{linkified('pöytävalaisin')}'.[/{SECONDARY}]\n"
            f"[{SECONDARY}]Examples:\n- 'Ik zoek een tafellamp.' meaning 'Minä etsin pöytälamppua.'\n"
            f"- 'Ik zoek een tafellamp.' meaning 'Minä etsin pöytävalaisinta.'[/{SECONDARY}]\n"
        )
        self.assert_printed(expected_argument, self.practice(quizzes))

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "Hoi\n", EOFError]))
    def test_quiz_try_again(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assert_printed(Feedback.TRY_AGAIN, patched_print)
        self.assert_printed(Feedback.CORRECT, patched_print)

    @patch("builtins.input", Mock(side_effect=["?\n", EOFError]))
    def test_quiz_skip_on_first_attempt(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assert_not_printed(Feedback.TRY_AGAIN, patched_print)
        self.assert_printed(f"The correct answer is '{linkified('Hoi!')}'\n", patched_print)

    @patch("builtins.input", Mock(side_effect=["first attempt", "?\n", EOFError]))
    def test_quiz_skip_on_second_attempt(self):
        """Test that the user is quizzed."""
        patched_print = self.practice(self.quizzes)
        self.assert_printed(Feedback.TRY_AGAIN, patched_print)
        self.assert_printed(f"The correct answer is '{linkified('Hoi!')}'\n", patched_print)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_progress(self):
        """Test that progress is shown after a correct answer."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=1)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_printed(progress_update(), patched_print)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_skip_progress(self):
        """Test that no progress is shown when the number of quizzes is smaller than the frequency."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=2)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_not_printed(progress_update(), patched_print)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_no_progress(self):
        """Test that no progress is shown when the requested frequency is zero."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=0)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_not_printed(progress_update(), patched_print)

    @patch("builtins.input", Mock(return_value="?\n"))
    def test_progress_after_skipped_quiz(self):
        """Test that progress is shown after a skipped answer."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=1)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_printed(progress_update(), patched_print)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "incorrect again\n"]))
    def test_progress_after_incorrect_answer(self):
        """Test that progress is shown after an incorrect answer."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=1)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_printed(progress_update(), patched_print)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        self.assert_printed(DONE, self.practice(self.quizzes))

    @patch("builtins.input", Mock(side_effect=[EOFError]))
    def test_exit(self):
        """Test that the user can quit."""
        patched_print = self.practice(self.quizzes)
        self.assertEqual(call(), patched_print.call_args_list[-1])
