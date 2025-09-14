"""Quiz type unit tests."""

from toisto.model.language import EN, NL
from toisto.model.language.grammatical_form import GrammaticalForm
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz_type import ANTONYM, PLURAL, READ, SINGULAR, THIRD_PERSON, GrammaticalQuizType, QuizType
from toisto.persistence.spelling_alternatives import load_spelling_alternatives
from toisto.ui.dictionary import linkified
from toisto.ui.format import quoted

from ....base import EN_NL, ToistoTestCase


class GrammaticalQuizTypeTest(ToistoTestCase):
    """Unit tests for the grammatical quiz type."""

    def test_is_quiz_type(self):
        """Test that the grammatical quiz type is indeed a grammatical quiz type."""
        self.assertTrue(PLURAL.is_quiz_type(PLURAL))

    def test_is_not_quiz_type(self):
        """Test that the grammatical quiz type is not a semantical quiz type."""
        self.assertFalse(PLURAL.is_quiz_type(ANTONYM))

    def test_composite_is_quiz_type(self):
        """Test that a composite grammatical quiz type is indeed a grammatical quiz type."""
        self.assertTrue(GrammaticalQuizType(quiz_types=frozenset((PLURAL, THIRD_PERSON))).is_quiz_type(PLURAL))

    def test_composite_is_not_quiz_type(self):
        """Test a composite grammatical quiz type is not a semantical quiz type."""
        self.assertFalse(GrammaticalQuizType(quiz_types=frozenset((PLURAL, THIRD_PERSON))).is_quiz_type(ANTONYM))

    def test_leaf_quiz_type_is_registered(self):
        """Test that a leaf quiz type is registered."""
        self.assertEqual((THIRD_PERSON,), QuizType.actions.get_values("third person"))

    def test_non_leaf_quiz_type_is_not_registered(self):
        """Test that a non-leaf quiz type is not registered."""
        QuizType()
        self.assertEqual((), QuizType.actions.get_values(""))


class QuizTypeNotesTest(ToistoTestCase):
    """Unit tests for the quiz type notes."""

    def test_default_notes(self):
        """Test that the quiz type notes are the question notes by default."""
        self.assertEqual(("note",), ANTONYM.notes(Label(EN, "label", notes=("note",)), Labels()))

    def test_grammatical_notes(self):
        """Test that the quiz type notes include grammatical notes."""
        table = Label(EN, "table", grammatical_form=GrammaticalForm("table", "singular"))
        tables = Label(EN, "tables", grammatical_form=GrammaticalForm("table", "plural"))
        table.other_grammatical_categories["plural"] = tables
        tables.other_grammatical_categories["singular"] = table
        table_note = quoted(linkified("table"))
        tables_note = quoted(linkified("tables"))
        self.assertEqual((f"The plural of {table_note} is {tables_note}.",), ANTONYM.notes(table, Labels()))
        self.assertEqual((f"The singular of {tables_note} is {table_note}.",), ANTONYM.notes(tables, Labels()))

    def test_omit_grammatical_notes(self):
        """Test that the quiz type notes do not include grammatical notes for the grammatical quiz."""
        table = Label(EN, "table", grammatical_form=GrammaticalForm("table", "singular"))
        tables = Label(EN, "tables", grammatical_form=GrammaticalForm("table", "plural"))
        table.other_grammatical_categories["plural"] = tables
        tables.other_grammatical_categories["singular"] = table
        self.assertEqual((), PLURAL.notes(table, Labels()))
        self.assertEqual((), SINGULAR.notes(tables, Labels()))

    def test_grammatical_notes_for_equal_labels(self):
        """Test that 'also' is inserted if both labels in the grammatical note are equal."""
        sheep_singular = Label(EN, "sheep", grammatical_form=GrammaticalForm("sheep", "singular"))
        sheep_plural = Label(EN, "sheep", grammatical_form=GrammaticalForm("sheep", "plural"))
        sheep_singular.other_grammatical_categories["plural"] = sheep_plural
        sheep_plural.other_grammatical_categories["singular"] = sheep_singular
        sheep = quoted(linkified("sheep"))
        self.assertEqual((f"The plural of {sheep} is also {sheep}.",), ANTONYM.notes(sheep_singular, Labels()))
        self.assertEqual((f"The singular of {sheep} is also {sheep}.",), ANTONYM.notes(sheep_plural, Labels()))


class QuizTypeOtherAnswersTest(ToistoTestCase):
    """Unit tests for the other answers method."""

    def setUp(self) -> None:
        """Extend to set up test fixtures."""
        super().setUp()
        load_spelling_alternatives(EN_NL)
        self.table = Label(EN, "table")
        self.chart = Label(EN, "chart")
        self.tafel = Label(NL, "de tafel")
        self.wrong_answer = Label(EN, "tabel")

    def test_one_answer_answered_correctly(self):
        """Test that having one answer being answered correcty means there are no other answers."""
        self.assertEqual((), READ.other_answers(self.table, Labels([self.table])))

    def test_one_answer_answered_incorrectly(self):
        """Test that having one answer being answered incorrecty means there is one other answer."""
        self.assertEqual((self.table,), READ.other_answers(self.wrong_answer, Labels([self.table])))

    def test_two_answers_answered_correctly(self):
        """Test that having two answers, one of them being given as answer means there is one other answer."""
        self.assertEqual((self.table,), READ.other_answers(self.chart, Labels([self.chart, self.table])))

    def test_two_answers_answered_incorrectly(self):
        """Test that having two answers, and an incorrect answer, means there are two other answers."""
        self.assertEqual(
            (self.chart, self.table),
            READ.other_answers(self.wrong_answer, Labels([self.chart, self.table])),
        )

    def test_one_answer_with_spelling_alternative_answered_correctly(self):
        """Test one answer with spelling alternative being answered correcty."""
        answer = Label(NL, "de tafel")
        self.assertEqual((), READ.other_answers(answer, Labels([self.tafel])))

    def test_one_answer_with_spelling_alternative_answered_correctly_with_alternative(self):
        """Test one answer with spelling alternative being answered correcty with the spelling alternative."""
        answer = Label(NL, "tafel")
        self.assertEqual((), READ.other_answers(answer, Labels([self.tafel])))
