"""Unit tests for the output."""

from unittest import TestCase

from toisto.model.language.label import Label
from toisto.model.model_types import ConceptId
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.topic import Topics
from toisto.ui.dictionary import DICTIONARY_URL, linkify
from toisto.ui.text import feedback_correct, feedback_incorrect, instruction

from ...base import ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = self.create_concept(ConceptId("hello"))
        self.quiz = self.create_quiz(self.concept, "nl", "fi", "Hoi", ["Terve"], meanings=("Hoi",))
        self.guess = Label("Terve")
        self.progress = Progress({}, Topics(set()))

    def assert_feedback_contains(self, feedback_text: str, *expected_strings: str) -> None:
        """Assert that the expected strings are in the feedback."""
        for expected_string in expected_strings:
            self.assertIn(expected_string, feedback_text)

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        feedback_text = feedback_correct(self.guess, self.quiz)
        self.assertEqual(f'✅ Correct.\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n', feedback_text)

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz(self.concept, "nl", "fi", "Hoi", ["Terve", "Hei"])
        expected_other_answer = linkify(quiz.other_answers(self.guess)[0])
        expected_text = f'✅ Correct.\n[secondary]Another correct answer is "{expected_other_answer}".[/secondary]\n'
        self.assertEqual(expected_text, feedback_correct(self.guess, quiz))

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz(self.concept, "nl", "fi", "Hoi", ["Terve", "Hei", "Hei hei"])
        other_answers = [f'"{linkify(answer)}"' for answer in quiz.other_answers(self.guess)]
        expected_text = f'✅ Correct.\n[secondary]Other correct answers are {", ".join(other_answers)}.[/secondary]\n'
        self.assertEqual(expected_text, feedback_correct(self.guess, quiz))

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        expected_text = (
            f'❌ Incorrect. The correct answer is "[inserted]{linkify("Terve")}[/inserted]".\n'
            f'[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect("", self.quiz))

    def test_show_alternative_answers_on_incorrect_guess(self):
        """Test that alternative answers are also given when the user guesses incorrectly."""
        quiz = self.create_quiz(self.concept, "nl", "fi", "Hoi", ["Terve", "Hei"])
        expected_text = (
            f'❌ Incorrect. The correct answer is "[inserted]{linkify("Terve")}[/inserted]".\n'
            f'[secondary]Another correct answer is "{linkify("Hei")}".[/secondary]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect("", quiz))

    def test_show_feedback_on_question_mark(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        expected_text = (
            f'The correct answer is "{linkify("Terve")}".\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n'
        )
        self.assertEqual(expected_text, feedback_incorrect("?", self.quiz))

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(self.quiz))

    def test_instruction_multiple_quiz_types(self):
        """Test that the quiz instruction is correctly formatted for multiple quiz types."""
        quiz = self.create_quiz(self.concept, "nl", "nl", "Ik eet", ["Zij eet"], ("give third person", "feminize"))
        expected_text = "[quiz]Give the [underline]third person female[/underline] in Dutch:[/quiz]"
        self.assertEqual(expected_text, instruction(quiz))


class LinkifyTest(TestCase):
    """Unit tests for the linkify method."""

    def test_linkify(self):
        """Test the linkify method."""
        self.assertEqual(f"[link={DICTIONARY_URL}/test]Test[/link]", linkify("Test"))

    def test_linkify_multiple_words(self):
        """Test the linkify method."""
        expected_text = f"[link={DICTIONARY_URL}/test]Test[/link] [link={DICTIONARY_URL}/words]words[/link]"
        self.assertEqual(expected_text, linkify("Test words"))

    def test_punctuation(self):
        """Test that punctuation is not linked."""
        self.assertEqual(f"[link={DICTIONARY_URL}/test]Test[/link].", linkify("Test."))
