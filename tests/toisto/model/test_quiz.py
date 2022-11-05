"""Quiz unit tests."""

import unittest
from typing import get_args

from toisto.model import Label, Quiz
from toisto.model.quiz import quiz_type_factory, QuizType, INSTRUCTION


class QuizTest(unittest.TestCase):
    """Unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("fi", "nl", Label("Englanti"), [Label("Engels")])

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.quiz.is_correct("engels"))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct("engles"))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual("Engels", self.quiz.answer)

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een", "Eén"])
        self.assertEqual("Een", quiz.answer)

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een", "Eén"])
        self.assertEqual(["Eén"], quiz.other_answers("Een"))

    def test_instruction(self):
        """Test the quiz instruction."""
        self.assertEqual("Translate into Dutch", self.quiz.instruction())

    def test_spelling_alternative_of_answer(self):
        """Test that a quiz can deal with alternative spellings of answers."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een|Eén"])
        self.assertEqual("Een", quiz.answer)

    def test_spelling_alternative_of_question(self):
        """Test that a quiz can deal with alternative spellings of the question."""
        quiz = Quiz("nl", "fy", "Een|Eén", ["Yksi"])
        self.assertEqual("Een", quiz.question)

    def test_spelling_alternative_is_correct(self):
        """Test that an answer that matches a spelling alternative is correct."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een|Eén", "één"])
        for alternative in ("Een", "Eén", "één"):
            self.assertTrue(quiz.is_correct(alternative))

    def test_other_answers_with_spelling_alternatives(self):
        """Test the spelling alternatives are returned as other answers."""
        quiz = Quiz("fi", "nl", "Yksi", ["Een|Eén", "één"])
        alternatives = ("Een", "Eén", "één")
        for alternative in alternatives:
            other_answers = list(alternatives)
            other_answers.remove(alternative)
            self.assertEqual(other_answers, quiz.other_answers(alternative))

    def test_instructions(self):
        """Test the instructions"""
        for quiz_type, instruction in zip(get_args(QuizType), INSTRUCTION.values()):
            quiz = Quiz("fi", "fi", "Label1", ["Label2"], quiz_type)
            self.assertEqual(instruction + " Finnish", quiz.instruction())


class QuizTypeFactoryTest(unittest.TestCase):
    """Unit tests for the quiz type factory function."""

    def test_unknown_grammatical_categories(self):
        """Test that unknown grammatical categoriews throw an exception."""
        self.assertRaises(NotImplementedError, quiz_type_factory, ("not a grammatical category",))
