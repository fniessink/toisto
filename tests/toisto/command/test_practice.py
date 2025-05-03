"""Unit tests for the practice command."""

from argparse import Namespace
from unittest.mock import MagicMock, Mock, call, patch

from toisto.command.practice import practice
from toisto.model.language import FI, NL
from toisto.model.language.label import Label
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, INTERPRET, PLURAL, READ, WRITE
from toisto.persistence.config import default_config
from toisto.ui.dictionary import linkified
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
        self.concept = self.create_concept(
            "hi", labels=[{"label": "Terve!", "language": FI}, {"label": "Hoi!", "language": NL}]
        )
        self.quizzes = create_quizzes(self.language_pair, (READ,), self.concept)

    def progress(self, quizzes: Quizzes) -> Progress:
        """Create the progress tracker."""
        return Progress(self.language_pair.target, quizzes, {})

    def practice(self, quizzes: Quizzes, progress: Progress | None = None, progress_update: int = 0) -> Mock:
        """Run the practice command and return the patched print statement."""
        config = default_config()
        config.set("commands", "mp3player", "mpg123")
        if progress is None:
            progress = self.progress(quizzes)
        with patch("rich.console.Console.print") as patched_print:
            practice(console.print, self.language_pair, progress, config, Namespace(progress_update=progress_update))
        return patched_print

    def assert_printed(self, output: str, patched_print: Mock, **kwargs: str | bool) -> None:
        """Assert that the argument is in the call arguments list of the patched print method."""
        self.assertIn(call(output, **kwargs), patched_print.call_args_list)

    def assert_not_printed(self, argument: str, patched_print: Mock, **kwargs: str | bool) -> None:
        """Assert that the argument is not in the call arguments list of the patched print method."""
        self.assertNotIn(call(argument, **kwargs), patched_print.call_args_list)

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
        self.assert_printed(f"{Feedback.INCORRECT}The correct answer is 'Ho[deleted]_[/deleted]i!'\n", patched_print)

    @patch("builtins.input", Mock(return_value="hoi!\n"))
    def test_answer_quiz_in_lowercase_source_language(self):
        """Test that a lower case answer is accepted when the answer language is the user's source language."""
        patched_print = self.practice(self.quizzes)
        self.assert_printed(Feedback.CORRECT, patched_print)

    @patch("builtins.input", Mock(return_value="terve!\n"))
    def test_answer_quiz_in_lowercase_target_language(self):
        """Test that a lower case answer is not accepted when the answer language is the user's target language."""
        quizzes = create_quizzes(self.language_pair, (WRITE,), self.concept)
        patched_print = self.practice(quizzes)
        self.assert_printed(f"{Feedback.INCORRECT}The correct answer is 'Terve!'\n", patched_print)

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_answer_with_question(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        self.assert_printed(Feedback.TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Dutch"), self.practice(self.quizzes))

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_answer_with_question_listen_quiz(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        quizzes = create_quizzes(self.language_pair, (DICTATE,), self.concept)
        self.assert_printed(Feedback.TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Finnish"), self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="jätski\n"))
    def test_colloquial_answer_when_question_colloquial(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        concept = self.create_concept(
            "ice cream",
            labels=[
                {"label": "jäätelö", "language": FI},
                {"label": "jätski", "language": FI, "colloquial": True},
                {"label": "het ijsje", "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (DICTATE,), concept).colloquial
        self.assert_printed(
            Feedback.TRY_AGAIN_IN_ANSWER_STANDARD_LANGUAGE % dict(language="Finnish"),
            self.practice(quizzes),
        )

    @patch("builtins.input", Mock(return_value="jäätelö\n"))
    def test_standard_language_answer_when_question_colloquial(self):
        """Test that the language to answer is stressed, when the user answers the quiz with the wrong language."""
        concept = self.create_concept(
            "ice cream",
            labels=[
                {"label": "jäätelö", "language": FI},
                {"label": "jätski", "language": FI, "colloquial": True},
                {"label": "het ijsje", "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (INTERPRET,), concept).colloquial
        self.assert_printed(Feedback.TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language="Dutch"), self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="talo\n"))
    def test_answer_with_question_grammar_quiz(self):
        """Test that the language to answer is not stressed, when the user answers a grammar quiz with the question."""
        concept = self.create_concept(
            "house", labels=[{"label": dict(singular="talo", plural="talot"), "language": FI}]
        )
        quizzes = create_quizzes(self.language_pair, (PLURAL,), concept)
        self.assert_printed(Feedback.TRY_AGAIN, self.practice(quizzes))

    @patch("builtins.input", Mock(side_effect=["\n", "Hoi\n"]))
    @patch("builtins.print")
    @patch("toisto.command.practice.Speech.say")
    def test_quiz_empty_answer(self, say: Mock, print_: Mock) -> None:
        """Test that the speech is repeated more slowly when the user hits enter without answer."""
        self.practice(self.quizzes)
        self.assertEqual({"slow": True}, say.call_args_list[-1][-1])
        self.assertEqual([call("\x1b[F", end="")], print_.call_args_list)

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_question(self):
        """Test that the question is printed."""
        self.assert_printed(linkified("Terve!"), self.practice(self.quizzes))

    @patch("builtins.input", Mock(return_value="hoi\n"))
    def test_quiz_listen(self):
        """Test that the question is not printed on a listening quiz."""
        quizzes = create_quizzes(self.language_pair, (DICTATE,), self.concept)
        self.assert_not_printed(linkified("Terve"), self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="Terve\n"))
    def test_quiz_non_translate(self):
        """Test that the translation is not printed on a non-translate quiz."""
        quizzes = create_quizzes(self.language_pair, (DICTATE,), self.concept)
        expected_feedback = f"{Feedback.CORRECT}[secondary]Meaning '{linkified('Hoi!')}'[/secondary]\n"
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="talot\n"))
    def test_quiz_with_multiple_meanings(self):
        """Test that the translation is not printed on a non-translate quiz."""
        concept = self.create_concept(
            "house",
            labels=[
                {"label": {"singular": "talo", "plural": "talot"}, "language": FI},
                {"label": {"singular": "huis", "plural": "huizen"}, "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (PLURAL,), concept)
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Meaning '{linkified('huis')}', "
            f"respectively '{linkified('huizen')}'.[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="hij rijdt\n"))
    def test_quiz_third_person_read_quiz(self):
        """Test that both the masculine and feminine form are correct."""
        concept = self.create_concept(
            "to ride",
            labels=[
                {"label": {"third person": "hän ajaa"}, "language": FI},
                {"label": {"third person": dict(feminine="zij rijdt", masculine="hij rijdt")}, "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (READ,), concept)
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Another correct answer is "
            "'[link=https://en.wiktionary.org/wiki/zij]zij[/link] "
            "[link=https://en.wiktionary.org/wiki/rijdt]rijdt[/link]'.[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="hij rijdt\n"))
    def test_quiz_third_person_interpret_quiz(self):
        """Test that both the masculine and feminine form are correct."""
        concept = self.create_concept(
            "to ride",
            labels=[
                {"label": {"third person": "hän ajaa"}, "language": FI},
                {"label": {"third person": dict(feminine="zij rijdt", masculine="hij rijdt")}, "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (INTERPRET,), concept)
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Meaning '[link=https://en.wiktionary.org/wiki/hän]hän[/link] "
            "[link=https://en.wiktionary.org/wiki/ajaa]ajaa[/link]'.[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="vieressä\n"))
    def test_quiz_with_example(self):
        """Test that the example is shown after the quiz."""
        concept = self.create_concept(
            "next to",
            {"example": "the museum is next to the church"},
            labels=[{"label": "vieressä", "language": FI}, {"label": "naast", "language": NL}],
        )
        self.create_concept(
            "the museum is next to the church",
            labels=[
                {"label": "Museo on kirkon vieressä.", "language": FI},
                {"label": "Het museum is naast de kerk.", "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (DICTATE,), concept)
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Meaning '{linkified('naast')}'.[/secondary]\n"
            "[secondary]Example: 'Museo on kirkon vieressä.' meaning 'Het museum is naast de kerk.'[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="musta\n"))
    def test_quiz_with_multiple_examples(self):
        """Test that the examples are shown after the quiz."""
        examples = ["the car is black", "the cars are black"]
        concept = self.create_concept(
            "black",
            {"example": examples},
            labels=[{"label": "musta", "language": FI}, {"label": "zwart", "language": NL}],
        )
        self.create_concept(
            "the car is black",
            labels=[{"label": "Auto on musta.", "language": FI}, {"label": "De auto is zwart.", "language": NL}],
        )
        self.create_concept(
            "the cars are black",
            labels=[
                {"label": "Autot ovat mustia.", "language": FI},
                {"label": "De auto's zijn zwart.", "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (DICTATE,), concept)
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Meaning '{linkified('zwart')}'.[/secondary]\n"
            "[secondary]Examples:\n- 'Auto on musta.' meaning 'De auto is zwart.'\n"
            "- 'Autot ovat mustia.' meaning 'De auto's zijn zwart.'[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="pöytävalaisin\n"))
    def test_quiz_with_example_with_synonyms_in_the_target_language(self):
        """Test that all synonyms of the example are shown after the quiz."""
        concept = self.create_concept(
            "table lamp",
            {"example": "I am looking for a table lamp"},
            labels=[
                {"label": "pöytälamppu", "language": FI},
                {"label": "pöytävalaisin", "language": FI},
                {"label": "de tafellamp", "language": NL},
            ],
        )
        self.create_concept(
            "I am looking for a table lamp",
            labels=[
                {"label": "Minä etsin pöytälamppua.", "language": FI},
                {"label": "Minä etsin pöytävalaisinta.", "language": FI},
                {"label": "Ik zoek een tafellamp.", "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (DICTATE,), concept)
        quizzes = Quizzes(quiz for quiz in quizzes if quiz.answer == Label(FI, "pöytävalaisin"))
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Meaning '{linkified('de tafellamp')}'.[/secondary]\n"
            "[secondary]Examples:\n- 'Minä etsin pöytälamppua.' meaning 'Ik zoek een tafellamp.'\n"
            "- 'Minä etsin pöytävalaisinta.' meaning 'Ik zoek een tafellamp.'[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

    @patch("builtins.input", Mock(return_value="de tafellamp\n"))
    def test_quiz_with_example_with_synonyms_in_the_source_language(self):
        """Test that all synonyms of the example are shown after the quiz."""
        self.language_pair = NL_FI
        concept = self.create_concept(
            "table lamp",
            {"example": "I am looking for a table lamp"},
            labels=[
                {"label": "pöytälamppu", "language": FI},
                {"label": "pöytävalaisin", "language": FI},
                {"label": "de tafellamp", "language": NL},
            ],
        )
        self.create_concept(
            "I am looking for a table lamp",
            labels=[
                {"label": "Minä etsin pöytälamppua.", "language": FI},
                {"label": "Minä etsin pöytävalaisinta.", "language": FI},
                {"label": "Ik zoek een tafellamp.", "language": NL},
            ],
        )
        quizzes = create_quizzes(self.language_pair, (DICTATE,), concept)
        expected_feedback = (
            f"{Feedback.CORRECT}[secondary]Meaning '{linkified('pöytälamppu')}' and "
            f"'{linkified('pöytävalaisin')}'.[/secondary]\n"
            "[secondary]Example: 'Ik zoek een tafellamp.' meaning 'Minä etsin pöytälamppua.' and "
            "'Minä etsin pöytävalaisinta.'[/secondary]\n"
        )
        self.assert_printed(expected_feedback, self.practice(quizzes))

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
        self.assert_printed(progress_update(), patched_print, end="", highlight=False)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_skip_progress(self):
        """Test that no progress is shown when the number of quizzes is smaller than the frequency."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=2)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_not_printed(progress_update(), patched_print, end="", highlight=False)

    @patch("builtins.input", Mock(return_value="Hoi\n"))
    def test_no_progress(self):
        """Test that no progress is shown when the requested frequency is zero."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=0)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_not_printed(progress_update(), patched_print, end="", highlight=False)

    @patch("builtins.input", Mock(return_value="?\n"))
    def test_progress_after_skipped_quiz(self):
        """Test that progress is shown after a skipped answer."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=1)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_printed(progress_update(), patched_print, end="", highlight=False)

    @patch("builtins.input", Mock(side_effect=["incorrect\n", "incorrect again\n"]))
    def test_progress_after_incorrect_answer(self):
        """Test that progress is shown after an incorrect answer."""
        progress = self.progress(self.quizzes)
        patched_print = self.practice(self.quizzes, progress, progress_update=1)
        progress_update = ProgressUpdate(progress, 1)
        self.assert_printed(progress_update(), patched_print, end="", highlight=False)

    @patch("builtins.input", Mock(side_effect=["hoi\n", "hoi\n"]))
    def test_quiz_done(self):
        """Test that the user is quizzed until done."""
        self.assert_printed(DONE, self.practice(self.quizzes))

    @patch("builtins.input", Mock(side_effect=[EOFError]))
    def test_exit(self):
        """Test that the user can quit."""
        patched_print = self.practice(self.quizzes)
        self.assertEqual(call(), patched_print.call_args_list[-1])
