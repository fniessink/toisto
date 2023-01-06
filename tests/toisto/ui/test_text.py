"""Unit tests for the output."""

from datetime import timedelta
from unittest import TestCase

from toisto.model import Label, Progress, Topics
from toisto.model.model_types import ConceptId
from toisto.ui.text import feedback_correct, feedback_incorrect, format_duration, instruction, linkify

from ..base import ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz(ConceptId("hello"), "nl", "fi", "Hoi", ["Terve"], meanings=("Hoi",))
        self.guess = Label("Terve")
        self.progress = Progress({}, Topics(set()))

    def assert_feedback_contains(self, feedback_text: str, *expected_strings: str) -> None:
        """Assert that the expected strings are in the feedback."""
        for expected_string in expected_strings:
            self.assertIn(expected_string, feedback_text)

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        feedback_text = feedback_correct(self.guess, self.quiz)
        self.assertEqual(f"""✅ Correct.\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n""", feedback_text)

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz("hello", "nl", "fi", "Hoi", ["Terve", "Hei"])
        feedback_text = feedback_correct(self.guess, quiz)
        expected_other_answer = linkify(quiz.other_answers(self.guess)[0])
        self.assertEqual(
            f"""✅ Correct.\n[secondary]Another correct answer is "{expected_other_answer}".[/secondary]\n""",
            feedback_text,
        )

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz("hello", "nl", "fi", "Hoi", ["Terve", "Hei", "Hei hei"])
        feedback_text = feedback_correct(self.guess, quiz)
        other_answers = [f'"{linkify(answer)}"' for answer in quiz.other_answers(self.guess)]
        self.assertEqual(
            f"""✅ Correct.\n[secondary]Other correct answers are {", ".join(other_answers)}.[/secondary]\n""",
            feedback_text,
        )

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        feedback_text = feedback_incorrect("", self.quiz)
        self.assertEqual(
            """❌ Incorrect. The correct answer is "[inserted]Terve[/inserted]".\n"""
            f"""[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n""",
            feedback_text,
        )

    def test_show_alternative_answers_on_incorrect_guess(self):
        """Test that alternative answers are also given when the user guesses incorrectly."""
        quiz = self.create_quiz("hello", "nl", "fi", "Hoi", ["Terve", "Hei"])
        feedback_text = feedback_incorrect("", quiz)
        self.assertEqual(
            """❌ Incorrect. The correct answer is "[inserted]Terve[/inserted]".\n"""
            f"""[secondary]Another correct answer is "{linkify("Hei")}".[/secondary]\n""",
            feedback_text,
        )

    def test_show_feedback_on_question_mark(self):
        """Test that the correct feedback is given when the user doesn't know the answer."""
        feedback_text = feedback_incorrect("?", self.quiz)
        self.assertEqual(
            f"""The correct answer is "{linkify("Terve")}".\n[secondary]Meaning "{linkify("Hoi")}".[/secondary]\n""",
            feedback_text,
        )

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(self.quiz))

    def test_instruction_multiple_quiz_types(self):
        """Test that the quiz instruction is correctly formatted for multiple quiz types."""
        quiz = self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Zij eet"], ("give third person", "feminize"))
        self.assertEqual(
            "[quiz]Give the [underline]third person female[/underline] form in Dutch:[/quiz]", instruction(quiz)
        )


class FormatDurationTest(TestCase):
    """Unit tests for the format duration method."""

    def test_format_duration_seconds(self):
        """Test format seconds."""
        self.assertEqual("2 seconds", format_duration(timedelta(seconds=2)))

    def test_format_duration_minutes(self):
        """Test format minutes."""
        self.assertEqual("2 minutes", format_duration(timedelta(seconds=90)))

    def test_format_duration_hours(self):
        """Test format hours."""
        self.assertEqual("2 hours", format_duration(timedelta(seconds=7200)))

    def test_format_duration_daya(self):
        """Test format days."""
        self.assertEqual("2 days", format_duration(timedelta(days=2)))


class LinkifyTest(TestCase):
    """Unit tests for the linkify method."""

    def test_linkify(self):
        """Test the linkify method."""
        self.assertEqual("[link=https://en.wiktionary.org/wiki/test]Test[/link]", linkify("Test"))

    def test_linkify_multiple_words(self):
        """Test the linkify method."""
        self.assertEqual(
            "[link=https://en.wiktionary.org/wiki/test]Test[/link] "
            "[link=https://en.wiktionary.org/wiki/words]words[/link]",
            linkify("Test words"),
        )

    def test_punctuation(self):
        """Test that punctuation is not linked."""
        self.assertEqual("[link=https://en.wiktionary.org/wiki/test]Test[/link].", linkify("Test."))
