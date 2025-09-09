"""Quiz type unit tests."""

from toisto.model.language import EN
from toisto.model.language.grammatical_form import GrammaticalForm
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz_type import ANTONYM, PLURAL, SINGULAR, THIRD_PERSON, GrammaticalQuizType, QuizType
from toisto.ui.dictionary import linkified
from toisto.ui.format import quoted

from ....base import ToistoTestCase


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
