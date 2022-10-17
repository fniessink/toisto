"""Quiz unit tests."""

import unittest

from toisto.model import Quiz


class QuizTest(unittest.TestCase):
    """Unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("fi", "nl", "Englanti", ["Engels"])

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.quiz.is_correct("engels"))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct("engles"))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual("Engels", self.quiz.get_answer())

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een", "Eén"])
        self.assertEqual("Een", quiz.get_answer())

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een", "Eén"])
        self.assertEqual(["Eén"], quiz.other_answers("Een"))

    def test_instruction(self):
        """Test the quiz instruction."""
        self.assertEqual("Translate into Dutch", self.quiz.instruction())
