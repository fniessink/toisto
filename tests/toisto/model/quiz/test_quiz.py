"""Quiz unit tests."""

from typing import get_args

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import QuizType
from toisto.persistence.spelling_alternatives import load_spelling_alternatives

from ....base import EN_FI, EN_NL, FI_EN, FI_NL, NL_EN, NL_FI, ToistoTestCase


class QuizTestCase(ToistoTestCase):
    """Base class for unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        self.concept = self.create_concept("english", {})
        self.language_pair = FI_NL
        self.quiz = self.create_quiz(self.concept, "Englanti", ["Engels"])


class QuizTest(QuizTestCase):
    """Unit tests for the quiz class."""

    def setUp(self):
        """Set up fixtures."""
        super().setUp()
        self.engels = Label(NL, "Engels")
        self.een = Label(NL, "Een")
        self.huis = Label(NL, "het huis")

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
        self.assertTrue(self.quiz.is_correct(self.engels, self.language_pair))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct(Label(NL, "engles"), self.language_pair))

    def test_upper_case_answer_is_correct(self):
        """Test that an upper case answer for a lower case question is correct."""
        quiz = self.create_quiz(self.create_concept("house", {}), "talo", ["het huis"])
        self.assertTrue(quiz.is_correct(Label(NL, "Het huis"), self.language_pair))

    def test_lower_case_answer_is_correct(self):
        """Test that a lower case answer to an upper case question is correct, if source language == answer language."""
        self.assertTrue(self.quiz.is_correct(Label(NL, "engels"), self.language_pair))

    def test_is_not_correct_due_to_upper_case_answer(self):
        """Test that a lower case answer is incorrect when the answer should be upper case."""
        concept = self.create_concept("finnish", {})
        quiz = self.create_quiz(concept, "suomi", ["het Fins"], "read", language_pair=FI_NL)
        self.assertTrue(quiz.is_correct(Label(NL, "fins"), FI_NL), quiz)
        quiz = self.create_quiz(concept, "het Fins", ["suomi"], "read", language_pair=NL_FI)
        self.assertTrue(quiz.is_correct(Label(FI, "Suomi"), NL_FI))
        quiz = self.create_quiz(concept, "suomi", ["het Fins"], "listen", language_pair=FI_NL)
        self.assertFalse(quiz.is_correct(Label(NL, "Suomi"), FI_NL))
        quiz = self.create_quiz(concept, "het Fins", ["suomi"], "listen", language_pair=NL_FI)
        self.assertTrue(quiz.is_correct(Label(FI, "Suomi"), NL_FI))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual(self.engels, self.quiz.answer)

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = self.create_quiz(self.concept, "Yksi", ["Een", "Eén"])
        self.assertEqual(self.een, quiz.answer)

    def test_other_answers(self):
        """Test that the other answers can be retrieved."""
        quiz = self.create_quiz(self.concept, "Yksi", ["Een", "Eén;note should be ignored"])
        self.assertEqual(["Eén"], [str(answer) for answer in quiz.other_answers(self.een)])

    def test_no_other_answers_when_quiz_type_is_listen(self):
        """Test that the other answers are not returned if the quiz type is dictate."""
        quiz = self.create_quiz(self.concept, "Yksi", ["Een", "Eén;note should be ignored"], "dictate")
        self.assertEqual((), quiz.other_answers(self.een))

    def test_no_generated_spelling_alternatives_as_other_answer(self):
        """Test that the other answers do not include generated spelling alternatives."""
        quiz = self.create_quiz(self.concept, "talo", ["het huis"])
        self.assertEqual((), quiz.other_answers(self.huis))

    def test_note(self):
        """Test that the first note is added to the instruction, the second is not, and neither to the question."""
        self.language_pair = EN_NL
        for question in (
            "You are;singular",
            "You are;singular;post quiz note",
            "You are;;post quiz note",
            "You are;;post quiz note 1;post quiz note 2",
        ):
            quiz = self.create_quiz(self.concept, question, ["Jij bent|Je bent"])
            hint = " (singular)" if "singular" in question else ""
            self.assertEqual(f"Translate into Dutch{hint}", quiz.instruction)
            self.assertEqual(Label(EN, "You are"), quiz.question)

    def test_question_note_is_ignored_in_answer(self):
        """Test that a note in the answer is ignored."""
        self.language_pair = NL_EN
        quiz = self.create_quiz(self.concept, "Jij bent", ["You are;singular"])
        self.assertEqual(Label(EN, "You are"), quiz.answer)

    def test_all_answer_notes_are_shown(self):
        """Test that all answer notes are shown."""
        self.language_pair = EN_NL
        answers = ["want;;explain want", "omdat;;explain omdat"]
        quiz = self.create_quiz(self.concept, "because", answers, "write")
        self.assertEqual(("explain want", "explain omdat"), quiz.answer_notes)


class QuizInstructionTest(QuizTestCase):
    """Unit tests for quiz instructions."""

    def test_instructions(self):
        """Test the instructions."""
        expected_instructions = [
            "Translate into Dutch",
            "Translate into Finnish",
            "Listen and write in Finnish",
            "Listen and write in Dutch",
            "Answer the question in Finnish",
            "Give the [underline]antonym[/underline] in Finnish",
            "Give the [underline]plural[/underline] in Finnish",
            "Give the [underline]singular[/underline] in Finnish",
            "Give the [underline]diminutive[/underline] in Finnish",
            "Give the [underline]male[/underline] in Finnish",
            "Give the [underline]female[/underline] in Finnish",
            "Give the [underline]neuter[/underline] in Finnish",
            "Give the [underline]positive degree[/underline] in Finnish",
            "Give the [underline]comparative degree[/underline] in Finnish",
            "Give the [underline]superlative degree[/underline] in Finnish",
            "Give the [underline]first person[/underline] in Finnish",
            "Give the [underline]second person[/underline] in Finnish",
            "Give the [underline]third person[/underline] in Finnish",
            "Give the [underline]infinitive[/underline] in Finnish",
            "Give the [underline]present tense[/underline] in Finnish",
            "Give the [underline]past tense[/underline] in Finnish",
            "Give the [underline]present perfect tense[/underline] in Finnish",
            "Give the [underline]declarative[/underline] in Finnish",
            "Give the [underline]interrogative[/underline] in Finnish",
            "Give the [underline]imperative[/underline] in Finnish",
            "Give the [underline]affirmative[/underline] in Finnish",
            "Give the [underline]negative[/underline] in Finnish",
            "Give the [underline]cardinal[/underline] in Finnish",
            "Give the [underline]ordinal[/underline] in Finnish",
            "Give the [underline]abbreviation[/underline] in Finnish",
            "Give the [underline]full form[/underline] in Finnish",
        ]
        for expected_instruction, quiz_type in zip(expected_instructions, get_args(QuizType), strict=True):
            quiz = self.create_quiz(self.concept, "Hei", ["Hei hei"], (quiz_type,))
            self.assertEqual(expected_instruction, quiz.instruction)

    def test_instuction_complete_sentence(self):
        """Test the instruction for a complete sentence."""
        self.language_pair = EN_NL
        quiz = self.create_quiz(self.concept, "Sentence.", ["Sentence."], "dictate")
        self.assertEqual("Listen and write a complete sentence in English", quiz.instruction)

    def test_question_note_is_not_shown_when_question_and_answer_language_are_the_same(self):
        """Test that a note is not shown if the question and answer languages are the same."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Hän on;female", ["He ovat"], "pluralize")
        self.assertEqual("Give the [underline]plural[/underline] in Finnish", quiz.instruction)

    def test_question_note_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_dictate(self):
        """Test that a note is shown if the question and answer languages are the same and the quiz type is dictate."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Suomi;country", ["Finland"], "dictate")
        self.assertEqual("Listen and write in Finnish (country)", quiz.instruction)

    def test_question_note_is_shown_when_question_language_equals_answer_language_and_quiz_type_is_answer(self):
        """Test that a note is shown if the question and answer languages are the same and the quiz type is answer."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Onko hän Bob?;positive or negative", ["On", "Ei"], "answer")
        self.assertEqual("Answer the question in Finnish (positive or negative)", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_note_when_quiz_type_is_dictate(self):
        """Test that colloquial labels get an automatic note."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "seittemän*", ["seitsemän"], "dictate")
        self.assertEqual("Listen to the colloquial Finnish and write in standard Finnish", quiz.instruction)

    def test_colloquial_labels_get_an_automatic_note_when_quiz_type_is_interpret(self):
        """Test that colloquial labels get an automatic note."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "seittemän*", ["zeven"], "interpret")
        self.assertEqual("Listen to the colloquial Finnish and write in Dutch", quiz.instruction)

    def test_sentences_get_an_automatic_note_when_quiz_type_is_listen(self):
        """Test that sentences get an automatic note when the quiz type is a listen quiz."""
        self.language_pair = FI_NL
        quiz = self.create_quiz(self.concept, "Terve!", ["Hallo!"], "interpret")
        self.assertEqual("Listen and write a complete sentence in Dutch", quiz.instruction)


class QuizSpellingAlternativesTests(QuizTestCase):
    """Unit tests for checking spelling alternatives."""

    def test_spelling_alternative_of_answer(self):
        """Test that a quiz can deal with alternative spellings of answers."""
        quiz = self.create_quiz(self.concept, "yksi", ["een|één"])
        self.assertEqual(Label(NL, "een"), quiz.answer)

    def test_spelling_alternative_of_question(self):
        """Test that a quiz can deal with alternative spellings of the question."""
        self.language_pair = NL_FI
        quiz = self.create_quiz(self.concept, "een|één", ["yksi"])
        self.assertEqual(Label(NL, "een"), quiz.question)

    def test_spelling_alternative_is_correct(self):
        """Test that an answer that matches a spelling alternative is correct."""
        quiz = self.create_quiz(self.concept, "Yksi.", ["Een|Eén", "één"])
        for alternative in ("Een", "Eén", "één"):
            self.assertTrue(quiz.is_correct(Label(NL, alternative), FI_NL))

    def test_other_answers_with_spelling_alternatives(self):
        """Test the spelling alternatives are returned as other answers."""
        quiz = self.create_quiz(self.concept, "Yksi.", ["Een|Eén", "één"])
        alternatives = ("Een", "Eén", "één")
        for alternative in alternatives:
            other_answers = list(alternatives)
            other_answers.remove(alternative)
            answer = Label(NL, alternative)
            self.assertEqual(tuple(Label(NL, answer) for answer in other_answers), quiz.other_answers(answer))

    def test_generated_spelling_alternative_is_correct(self):
        """Test that a generated spelling alternative is accepted as answer."""
        load_spelling_alternatives(EN_NL)
        self.language_pair = NL_EN
        quiz = self.create_quiz(self.concept, "Het is waar.", ["It is true."])
        self.assertTrue(quiz.is_correct(Label(EN, "It's true"), self.language_pair))
        quiz = self.create_quiz(self.concept, "Het is.", ["It is."])
        self.assertTrue(quiz.is_correct(Label(EN, "It's."), self.language_pair))
        quiz = self.create_quiz(self.concept, "Ik ben Alice.", ["I am Alice."])
        self.assertTrue(quiz.is_correct(Label(EN, "I'm Alice."), self.language_pair))
        quiz = self.create_quiz(self.concept, "Ik overval.", ["I ambush."])
        self.assertFalse(quiz.is_correct(Label(EN, "I'mbush."), self.language_pair))
        self.language_pair = EN_NL
        quiz = self.create_quiz(self.concept, "house", ["het huis"])
        self.assertTrue(quiz.is_correct(Label(NL, "huis"), self.language_pair))
        load_spelling_alternatives(FI_EN)
        self.language_pair = EN_FI
        quiz = self.create_quiz(self.concept, "I am", ["minä olen"])
        self.assertTrue(quiz.is_correct(Label(FI, "olen"), self.language_pair))
        quiz = self.create_quiz(self.concept, "I am Alice.", ["Minä olen Alice."])
        self.assertTrue(quiz.is_correct(Label(FI, "Olen Alice."), self.language_pair))

    def test_generated_spelling_alternative_is_no_other_answer(self):
        """Test that a generated spelling alternative is not an other answer."""
        self.language_pair = EN_NL
        load_spelling_alternatives(EN_NL)
        quiz = self.create_quiz(self.concept, "pain", ["de pijn"])
        answer = Label(NL, "pijn")
        self.assertTrue(quiz.is_correct(answer, self.language_pair))
        self.assertEqual((), quiz.other_answers(answer))

    def test_capitalized_answer_without_article(self):
        """Test that the article can be left out, even though the noun starts with a capital."""
        load_spelling_alternatives(FI_NL)
        quiz = self.create_quiz(self.concept, "englanti", ["het Engels"])
        answer = Label(NL, "Engels")
        self.assertTrue(quiz.is_correct(answer, self.language_pair))


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
        self.assertNotEqual(self.copy_quiz(self.quiz, question=str(self.quiz.question).lower()), self.quiz)

    def test_equal_when_answers_have_different_case(self):
        """Test that quizzes are equal if only the case of the answers differs."""
        answers = [str(answer).lower() for answer in self.quiz.answers]
        self.assertEqual(self.copy_quiz(self.quiz, answers=answers), self.quiz)
