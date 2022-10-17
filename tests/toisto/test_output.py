"""Unit tests for the output."""

import unittest

from toisto.color import green, grey, purple
from toisto.model import Progress, Quiz
from toisto.output import feedback_correct, feedback_incorrect, instruction


class FeedbackTestCase(unittest.TestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("nl", "fi", "Hoi", ["Terve"])
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
        feedback_text = feedback_correct("Terve", self.quiz, self.progress.get_progress(self.quiz))
        self.assertEqual("✅ Correct.\n", feedback_text)

    def test_correct_second_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(2)
        feedback_text = feedback_correct("Terve", self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(
            feedback_text, "That's 2 times in a row. Skipping this quiz for", "minutes"
        )

    def test_correct_silenced_for_hours(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(10)
        feedback_text = feedback_correct("Terve", self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(
            feedback_text, "That's 10 times in a row. Skipping this quiz for", "hours"
        )

    def test_correct_silenced_for_days(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(20)
        feedback_text = feedback_correct("Terve", self.quiz, self.progress.get_progress(self.quiz))
        self.assert_feedback_contains(
            feedback_text, "That's 20 times in a row. Skipping this quiz for", "days"
        )

    def test_show_alternative_answer(self):
        """Test that alternative answers are shown."""
        quiz = Quiz("nl", "fi", "Hoi", ["Terve", "Hei"])
        feedback_text = feedback_correct("Terve", quiz, self.progress.get_progress(quiz))
        self.assertEqual(
            f"""✅ Correct.\n{grey(f'Another correct answer is "{quiz.other_answers("Terve")[0]}".')}\n""",
            feedback_text
        )

    def test_show_alternative_answers(self):
        """Test that alternative answers are shown."""
        quiz = Quiz("nl", "fi", "Hoi", ["Terve", "Hei", "Hei hei"])
        feedback_text = feedback_correct("Terve", quiz, self.progress.get_progress(quiz))
        other_answers = [f'"{answer}"' for answer in quiz.other_answers("Terve")]
        self.assertEqual(
            f"""✅ Correct.\n{grey(f'Other correct answers are {", ".join(other_answers)}.')}\n""",
            feedback_text
        )

    def test_incorrect(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        feedback_text = feedback_incorrect("", self.quiz)
        self.assertEqual(f"""❌ Incorrect. The correct answer is "{green('Terve')}".\n""", feedback_text)

    def test_instruction(self):
        """Test that the quiz instruction is correctly formatted."""
        self.assertEqual(purple("Translate into Finnish:"), instruction(self.quiz))
