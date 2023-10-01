"""Quiz unit tests."""

from typing import cast, get_args

from toisto.model.language.concept import ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.quiz.quiz import QuizType

from ....base import ToistoTestCase


class QuizTestCase(ToistoTestCase):
    """Base class for unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = create_concept(ConceptId("english"), cast(ConceptDict, {}))
        self.quiz = self.create_quiz(self.concept, "fi", "nl", "Englanti", ["Engels"])


class QuizTest(QuizTestCase):
    """Unit tests for the quiz class."""

    def test_defaults(self):
        """Test default values of optional attributes."""
        self.assertEqual(("read",), self.quiz.quiz_types)
        self.assertEqual((), self.quiz.blocked_by)
        self.assertEqual((), self.quiz.question_meanings)
        self.assertEqual((), self.quiz.answer_meanings)

    def test_repr(self):
        """Test the repr() function."""
        self.assertEqual("english:fi:nl:Englanti:read", repr(self.quiz))

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.quiz.is_correct("Engels"))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct("engles"))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual("Engels", self.quiz.answer)

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Yksi", ["Een", "Eén"])
        self.assertEqual("Een", quiz.answer)

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Yksi", ["Een", "Eén;note should be ignored"])
        self.assertEqual(["Eén"], [str(answer) for answer in quiz.other_answers("Een")])

    def test_no_other_answers_when_quiz_type_is_listen(self):
        """Test that the other answers are not returned if the quiz type is dictate."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Yksi", ["Een", "Eén;note should be ignored"], "dictate")
        self.assertEqual((), quiz.other_answers("Een"))

    def test_spelling_alternative_of_answer(self):
        """Test that a quiz can deal with alternative spellings of answers."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Yksi", ["Een|Eén"])
        self.assertEqual("Een", quiz.answer)

    def test_spelling_alternative_of_question(self):
        """Test that a quiz can deal with alternative spellings of the question."""
        quiz = self.create_quiz(self.concept, "nl", "fy", "Een|Eén", ["Yksi"])
        self.assertEqual("Een", quiz.question)

    def test_spelling_alternative_is_correct(self):
        """Test that an answer that matches a spelling alternative is correct."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Yksi", ["Een|Eén", "één"])
        for alternative in ("Een", "Eén", "één"):
            self.assertTrue(quiz.is_correct(alternative))

    def test_other_answers_with_spelling_alternatives(self):
        """Test the spelling alternatives are returned as other answers."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Yksi", ["Een|Eén", "één"])
        alternatives = ("Een", "Eén", "één")
        for alternative in alternatives:
            other_answers = list(alternatives)
            other_answers.remove(alternative)
            self.assertEqual(tuple(other_answers), quiz.other_answers(alternative))

    def test_instructions(self):
        """Test the instructions."""
        expected_instructions = [
            "Translate into",
            "Translate into",
            "Listen and write in",
            "Listen and write in",
            "Answer the question in",
            "Give the [underline]antonym[/underline] in",
            "Give the [underline]plural[/underline] in",
            "Give the [underline]singular[/underline] in",
            "Give the [underline]diminutive[/underline] in",
            "Give the [underline]male[/underline] in",
            "Give the [underline]female[/underline] in",
            "Give the [underline]neuter[/underline] in",
            "Give the [underline]positive degree[/underline] in",
            "Give the [underline]comparative degree[/underline] in",
            "Give the [underline]superlative degree[/underline] in",
            "Give the [underline]first person[/underline] in",
            "Give the [underline]second person[/underline] in",
            "Give the [underline]third person[/underline] in",
            "Give the [underline]infinitive[/underline] in",
            "Give the [underline]present tense[/underline] in",
            "Give the [underline]past tense[/underline] in",
            "Give the [underline]declarative[/underline] in",
            "Give the [underline]interrogative[/underline] in",
            "Give the [underline]affirmative[/underline] in",
            "Give the [underline]negative[/underline] in",
        ]
        for expected_instruction, quiz_type in zip(expected_instructions, get_args(QuizType), strict=True):
            quiz = self.create_quiz(self.concept, "fi", "fi", "Hei", ["Hei hei"], (quiz_type,))
            self.assertEqual(expected_instruction + " Finnish", quiz.instruction)

    def test_note(self):
        """Test that the first note is added to the instruction, the second is not, and neither to the question."""
        for question in (
            "You are;singular",
            "You are;singular;post quiz note",
            "You are;;post quiz note",
            "You are;;post quiz note 1;post quiz note 2",
        ):
            quiz = self.create_quiz(self.concept, "en", "nl", question, ["Jij bent|Je bent"])
            hint = " (singular)" if "singular" in question else ""
            self.assertEqual(f"Translate into Dutch{hint}", quiz.instruction)
            self.assertEqual("You are", quiz.question)

    def test_question_note_is_not_shown_when_question_and_answer_language_are_the_same(self):
        """Test that a note is not shown if the question and answer languages are the same."""
        quiz = self.create_quiz(self.concept, "fi", "fi", "Hän on;female", ["He ovat"], "pluralize")
        self.assertEqual("Give the [underline]plural[/underline] in Finnish", quiz.instruction)

    def test_question_note_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_listen(self):
        """Test that a note is shown if the question and answer languages are the same and the quiz type is dictate."""
        quiz = self.create_quiz(self.concept, "fi", "fi", "Suomi;country", ["Finland"], "dictate")
        self.assertEqual("Listen and write in Finnish (country)", quiz.instruction)

    def test_question_note_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_answer(self):
        """Test that a note is shown if the question and answer languages are the same and the quiz type is answer."""
        quiz = self.create_quiz(self.concept, "fi", "fi", "Onko hän Bob?;positive or negative", ["On", "Ei"], "answer")
        self.assertEqual("Answer the question in Finnish (positive or negative)", quiz.instruction)

    def test_question_note_is_ignored_in_answer(self):
        """Test that a note in the answer is ignored."""
        quiz = self.create_quiz(self.concept, "en", "nl", "Jij bent", ["You are;singular"])
        self.assertEqual("You are", quiz.answer)
        self.assertEqual(("You are",), quiz.answers)

    def test_all_answer_notes_are_shown(self):
        """Test that all answer notes are shown."""
        answers = ["want;;explain want", "omdat;;explain omdat"]
        quiz = self.create_quiz(self.concept, "en", "nl", "because", answers, "write")
        self.assertEqual(("explain want", "explain omdat"), quiz.answer_notes)

    def test_colloquial_labels_get_an_automatic_note_when_quiz_type_is_dictate(self):
        """Test that colloquial labels get an automatic note."""
        quiz = self.create_quiz(self.concept, "fi", "fi", "seittemän*", ["seitsemän"], "dictate")
        self.assertEqual("Listen to the colloquial Finnish and write in standard Finnish", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_note_when_quiz_type_is_interpret(self):
        """Test that colloquial labels get an automatic note."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "seittemän*", ["zeven"], "interpret")
        self.assertEqual("Listen to the colloquial Finnish and write in Dutch", quiz.instruction)

    def test_sentences_get_an_automatic_note_when_quiz_type_is_listen(self):
        """Test that sentences get an automatic note when the quiz type is a listen quiz."""
        quiz = self.create_quiz(self.concept, "fi", "nl", "Terve!", ["Hallo!"], "interpret")
        self.assertEqual("Listen and write a complete sentence in Dutch", quiz.instruction)


class QuizEqualityTests(QuizTestCase):
    """Unit tests for the equality of quiz instances."""

    def test_equal(self):
        """Test that a quiz is equal to itself and to quizzes with the same parameters."""
        self.assertEqual(self.quiz, self.quiz)
        self.assertEqual(self.copy_quiz(self.quiz), self.quiz)

    def test_equal_with_different_notes(self):
        """Test that quizzes are equal if only their notes differ."""
        self.assertEqual(self.copy_quiz(self.quiz, question="Englanti;note"), self.quiz)
        self.assertEqual(self.copy_quiz(self.quiz, answers=["Engels;note"]), self.quiz)

    def test_not_equal_with_different_languages(self):
        """Test that quizzes are not equal if only their languages differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, question_language="nl"), self.quiz)
        self.assertNotEqual(self.copy_quiz(self.quiz, answer_language="en"), self.quiz)

    def test_not_equal_with_different_questions(self):
        """Test that quizzes are not equal if only their questions differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, question="Saksa"), self.quiz)

    def test_equal_with_different_answers(self):
        """Test that quizzes are equal if only their answers differ."""
        self.assertEqual(self.copy_quiz(self.quiz, answers=["Duits"]), self.quiz)

    def test_not_equal_with_different_quiz_types(self):
        """Test that quizzes are not equal if only their quiz types differ."""
        self.assertNotEqual(self.copy_quiz(self.quiz, quiz_type="dictate"), self.quiz)

    def test_not_equal_when_questions_have_different_case(self):
        """Test that quizzes are different if only the case of the question differs."""
        self.assertNotEqual(self.copy_quiz(self.quiz, question=self.quiz.question.lower()), self.quiz)

    def test_equal_when_answers_have_different_case(self):
        """Test that quizzes are equal if only the case of the answers differs."""
        self.assertEqual(self.copy_quiz(self.quiz, answers=[answer.lower() for answer in self.quiz.answers]), self.quiz)
