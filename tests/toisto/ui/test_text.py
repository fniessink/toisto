"""Unit tests for the output."""

from datetime import timedelta

from toisto.model import Label, Progress
from toisto.model.model_types import ConceptId
from toisto.ui.text import feedback_correct, feedback_incorrect, format_duration, instruction

from ..base import ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz(ConceptId("hello"), "nl", "fi", "Hoi", ["Terve"], meanings=("Hoi",))
        self.guess = Label("Terve")
        self.progress = Progress({})

    def assert_feedback_contains(self, feedback_text: str, *expected_strings: str) -> None:
        """Assert that the expected strings are in the feedback."""
        for expected_string in expected_strings:
            self.assertIn(expected_string, feedback_text)

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        feedback_text = feedback_correct(self.guess, self.quiz)
        self.assertEqual("""✅ Correct.\n[secondary]Meaning "Hoi".[/secondary]\n""", feedback_text)

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz("hello", "nl", "fi", "Hoi", ["Terve", "Hei"])
        feedback_text = feedback_correct(self.guess, quiz)
        expected_other_answer = quiz.other_answers(self.guess)[0]
        self.assertEqual(
            f"""✅ Correct.\n[secondary]Another correct answer is "{expected_other_answer}".[/secondary]\n""",
            feedback_text
        )

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz("hello", "nl", "fi", "Hoi", ["Terve", "Hei", "Hei hei"])
        feedback_text = feedback_correct(self.guess, quiz)
        other_answers = [f'"{answer}"' for answer in quiz.other_answers(self.guess)]
        self.assertEqual(
            f"""✅ Correct.\n[secondary]Other correct answers are {", ".join(other_answers)}.[/secondary]\n""",
            feedback_text
        )

    def test_show_feedback_on_incorrect_guess(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        feedback_text = feedback_incorrect("", self.quiz)
        self.assertEqual(
            """❌ Incorrect. The correct answer is "[inserted]Terve[/inserted]".\n"""
            """[secondary]Meaning "Hoi".[/secondary]\n""",
            feedback_text
        )

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(self.quiz))

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
