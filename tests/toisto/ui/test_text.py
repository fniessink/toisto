"""Unit tests for the output."""

from toisto.model import Label, Progress
from toisto.ui.text import feedback_correct, feedback_incorrect, instruction

from ..base import ToistoTestCase


class FeedbackTestCase(ToistoTestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz("nl", "fi", "Hoi", ["Terve"])
        self.guess = Label("Terve")
        self.progress = Progress({})

    def update_progress(self, nr_correct: int) -> None:
        """Update the progress with a number of correct guess."""
        for _ in range(nr_correct):
            self.progress.update(self.quiz, True)

    def assert_feedback_contains(self, feedback_text: str, *expected_strings: str) -> None:
        """Assert that the expected strings are in the feedback."""
        for expected_string in expected_strings:
            self.assertIn(expected_string, feedback_text)

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        feedback_text = feedback_correct(self.guess, self.quiz, self.progress.get_progress(self.quiz))
        self.assertEqual("✅ Correct.\n", feedback_text)

    def test_correct_second_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(2)
        feedback_text = feedback_correct(self.guess, self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(feedback_text, "Skipping this quiz for", "minutes")

    def test_correct_silenced_for_hours(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(10)
        feedback_text = feedback_correct(self.guess, self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(feedback_text, "Skipping this quiz for", "hours")
        self.update_progress(4)
        feedback_text = feedback_correct(self.guess, self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(feedback_text, "Skipping this quiz for", "hours")

    def test_correct_silenced_for_days(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(20)
        feedback_text = feedback_correct(self.guess, self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(feedback_text, "Skipping this quiz for", "days")

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz("nl", "fi", "Hoi", ["Terve", "Hei"])
        feedback_text = feedback_correct(self.guess, quiz, self.progress.get_progress(quiz))
        expected_other_answer = quiz.other_answers(self.guess)[0]
        self.assertEqual(
            f"""✅ Correct.\n[secondary]Another correct answer is "{expected_other_answer}".[/secondary]\n""",
            feedback_text
        )

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        quiz = self.create_quiz("nl", "fi", "Hoi", ["Terve", "Hei", "Hei hei"])
        feedback_text = feedback_correct(self.guess, quiz, self.progress.get_progress(quiz))
        other_answers = [f'"{answer}"' for answer in quiz.other_answers(self.guess)]
        self.assertEqual(
            f"""✅ Correct.\n[secondary]Other correct answers are {", ".join(other_answers)}.[/secondary]\n""",
            feedback_text
        )

    def test_incorrect(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        feedback_text = feedback_incorrect("", self.quiz)
        self.assertEqual("""❌ Incorrect. The correct answer is "[inserted]Terve[/inserted]".\n""", feedback_text)

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        self.assertEqual("[quiz]Translate into Finnish:[/quiz]", instruction(self.quiz))
