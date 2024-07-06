"""Unit tests for labels."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label

from ....base import ToistoTestCase


class LabelTest(ToistoTestCase):
    """Unit tests for the Label class."""

    def test_equality(self):
        """Test that labels are not equal to non-labels."""
        label = Label(EN, "English")
        equal_to_object = label == object()
        self.assertFalse(equal_to_object)
        not_equal_to_object = label != object()
        self.assertTrue(not_equal_to_object)

    def test_complete_sentence(self):
        """Test that a colloquial sentence is recognized."""
        label = Label(FI, "Kiitti!*")
        self.assertTrue(label.is_complete_sentence)

    def test_homonym(self):
        """Test that labels that are the same are homonyms."""
        financial_institution = Label(NL, "de bank")
        self.assertFalse(financial_institution.has_homonym)
        furniture = Label(NL, "de bank")
        self.assertTrue(financial_institution.has_homonym)
        self.assertTrue(furniture.has_homonym)

    def test_homonym_with_different_notes(self):
        """Test that labels that are the same and have different notes are homonyms."""
        financial_institution = Label(NL, "de bank;note")
        furniture = Label(NL, "de bank")
        self.assertTrue(financial_institution.has_homonym)
        self.assertTrue(furniture.has_homonym)
