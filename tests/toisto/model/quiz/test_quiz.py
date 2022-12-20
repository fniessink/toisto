"""Quiz unit tests."""

from typing import get_args

from toisto.model.model_types import ConceptId
from toisto.model.quiz.quiz import easiest_quizzes, instruction, QuizType

from ...base import ToistoTestCase


class QuizTestCase(ToistoTestCase):
    """Base class for unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz(ConceptId("english"), "fi", "nl", "Englanti", ["Engels"])


class QuizTest(QuizTestCase):
    """Unit tests for the quiz class."""

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
        quiz = self.create_quiz("1", "fi", "nl", "Yksi", ["Een", "Eén"])
        self.assertEqual("Een", quiz.answer)

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = self.create_quiz("1", "fi", "nl", "Yksi", ["Een", "Eén;hint should be ignored"])
        self.assertEqual(["Eén"], [str(answer) for answer in quiz.other_answers("Een")])

    def test_no_other_answers_when_quiz_type_is_listen(self):
        """Test that the other answers are not returned if the zuiz type is listen."""
        quiz = self.create_quiz("1", "fi", "nl", "Yksi", ["Een", "Eén;hint should be ignored"], "listen")
        self.assertEqual((), quiz.other_answers("Een"))

    def test_spelling_alternative_of_answer(self):
        """Test that a quiz can deal with alternative spellings of answers."""
        quiz = self.create_quiz("1", "fi", "nl", "Yksi", ["Een|Eén"])
        self.assertEqual("Een", quiz.answer)

    def test_spelling_alternative_of_question(self):
        """Test that a quiz can deal with alternative spellings of the question."""
        quiz = self.create_quiz("1", "nl", "fy", "Een|Eén", ["Yksi"])
        self.assertEqual("Een", quiz.question)

    def test_spelling_alternative_is_correct(self):
        """Test that an answer that matches a spelling alternative is correct."""
        quiz = self.create_quiz("1", "fi", "nl", "Yksi", ["Een|Eén", "één"])
        for alternative in ("Een", "Eén", "één"):
            self.assertTrue(quiz.is_correct(alternative))

    def test_other_answers_with_spelling_alternatives(self):
        """Test the spelling alternatives are returned as other answers."""
        quiz = self.create_quiz("1", "fi", "nl", "Yksi", ["Een|Eén", "één"])
        alternatives = ("Een", "Eén", "één")
        for alternative in alternatives:
            other_answers = list(alternatives)
            other_answers.remove(alternative)
            self.assertEqual(tuple(other_answers), quiz.other_answers(alternative))

    def test_instructions(self):
        """Test the instructions."""
        for quiz_type in get_args(QuizType):
            quiz = self.create_quiz("hi", "fi", "fi", "Hei", ["Hei hei"], (quiz_type,))
            self.assertEqual(instruction(quiz_type) + " Finnish", quiz.instruction())

    def test_instruction_with_hint(self):
        """Test that the question hint is added to the instruction."""
        quiz = self.create_quiz("to be", "en", "nl", "You are;singular", ["Jij bent|Je bent"])
        self.assertEqual("Translate into Dutch (singular)", quiz.instruction())

    def test_question_hint(self):
        """Test that a hint can be added to the question."""
        quiz = self.create_quiz("to be", "en", "nl", "You are;singular", ["Jij bent|Je bent"])
        self.assertEqual("You are", quiz.question)

    def test_question_hint_is_not_shown_when_question_and_answer_language_are_the_same(self):
        """Test that a hint is not shown when the question and answer languages are the same."""
        quiz = self.create_quiz("to be", "fi", "fi", "Hän on;female", ["He ovat"], "pluralize")
        self.assertEqual("Give the [underline]plural form[/underline] in Finnish", quiz.instruction())

    def test_question_hint_is_ignored_in_answer(self):
        """Test that a hint can be added to the question."""
        quiz = self.create_quiz("to be", "nl", "en", "Jij bent", ["You are;singular"])
        self.assertEqual("You are", quiz.answer)
        self.assertEqual(("You are",), quiz.answers)


class QuizEqualityTests(QuizTestCase):
    """Unit tests for the equality of quiz instances."""

    def test_equal(self):
        """Test that a quiz is equal to itself and to quizzes with the same parameters."""
        self.assertEqual(self.quiz, self.quiz)
        same_quiz = self.create_quiz("english", "fi", "nl", "Englanti", ["Engels"])
        self.assertEqual(same_quiz, self.quiz)

    def test_equal_with_different_hints(self):
        """Test that quizzes are equal if only their hints differ."""
        different_answer_hint = self.create_quiz("english", "fi", "nl", "Englanti;hint", ["Engels"])
        self.assertEqual(different_answer_hint, self.quiz)
        different_question_hint = self.create_quiz("english", "fi", "nl", "Englanti", ["Engels;hint"])
        self.assertEqual(different_question_hint, self.quiz)

    def test_not_equal_with_different_languages(self):
        """Test that quizzes are not equal if only their languages differ."""
        different_question_language = self.create_quiz("english", "en", "nl", "Englanti", ["Engels"])
        self.assertNotEqual(different_question_language, self.quiz)
        different_answer_language = self.create_quiz("english", "fi", "en", "Englanti", ["Engels"])
        self.assertNotEqual(different_answer_language, self.quiz)

    def test_not_equal_with_different_questions(self):
        """Test that quizzes are not equal if only their questions differ."""
        different_question = self.create_quiz("english", "fi", "nl", "Saksa", ["Engels"])
        self.assertNotEqual(different_question, self.quiz)

    def test_equal_with_different_answers(self):
        """Test that quizzes are equal if only their answers differ."""
        different_answers = self.create_quiz("english", "fi", "nl", "Englanti", ["Duits"])
        self.assertEqual(different_answers, self.quiz)

    def test_not_equal_with_different_quiz_types(self):
        """Test that quizzes are not equal if only their quiz types differ."""
        different_quiz_type = self.create_quiz("english", "fi", "nl", "Englanti", ["Engels"], "listen")
        self.assertNotEqual(different_quiz_type, self.quiz)


class EasiestQuizzesTest(ToistoTestCase):
    """Unit tests for finding the easiest quizzes."""

    def test_no_quizzes(self):
        """Test the easiest quizzes out of none."""
        self.assertEqual(set(), easiest_quizzes(set()))

    def test_one_quiz(self):
        """Test that the easiest quiz out of one is that one quiz."""
        quiz = self.create_quiz("english", "fi", "nl", "Englanti", ["Engels"])
        self.assertEqual({quiz}, easiest_quizzes({quiz}))

    def test_two_quizzes(self):
        """Test two quizzes."""
        quiz1 = self.create_quiz("english", "fi", "nl", "Englanti", ["Engels"])
        quiz2 = self.create_quiz("english", "fi", "nl", "Englanti", ["Engels"], "listen")
        self.assertEqual({quiz1}, easiest_quizzes({quiz1, quiz2}))
