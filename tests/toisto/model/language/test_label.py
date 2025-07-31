"""Unit tests for labels."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label, Labels

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
        label = Label(FI, "Kiitti!", colloquial=True)
        self.assertTrue(label.is_complete_sentence)

    def test_repr(self):
        """Test the representation of a label."""
        self.assertEqual("English", repr(Label(EN, "English")))

    def test_word_count(self):
        """Test the label word count."""
        self.assertEqual(1, Label(EN, "English").word_count)
        self.assertEqual(2, Label(EN, "English language").word_count)
        self.assertEqual(5, Label(EN, "The English language is beautiful.").word_count)
        self.assertEqual(4, Label(EN, "North-America is one word.").word_count)

    def test_random_order(self):
        """Test that the label can be returned in random word order."""
        label = Label(EN, "The English language is beautiful.")
        self.assertEqual(sorted(str(label).split(" ")), sorted(str(label.random_order).split(" ")))

    def test_note(self):
        """Test that the label can have a note."""
        note = "In English, the names of holidays are capitalized"
        label = Label(EN, "Christmas", (note,))
        self.assertEqual((note,), label.notes)

    def test_spelling_alternatives(self):
        """Test that the label can have spelling alternatives."""
        label = Label(EN, ["Christmas", "Xmas"])
        self.assertEqual((Label(EN, "Christmas"), Label(EN, "Xmas")), label.spelling_alternatives)

    def test_roots(self):
        """Test that the label can have roots."""
        label = Label(NL, "de keukenkast", roots=("de keuken", "de kast"))
        self.assertEqual(Labels([Label(NL, "de keuken"), Label(NL, "de kast")]), label.roots)

    def test_compounds(self):
        """Test that the label can have compounds."""
        kast = Label(NL, "de kast")
        keuken = Label(NL, "de keuken")
        keukenkast = Label(NL, "de keukenkast", roots=("de keuken", "de kast"))
        self.assertEqual((keukenkast,), kast.compounds)
        self.assertEqual((keukenkast,), keuken.compounds)

    def test_recursive_roots(self):
        """Test that getting the roots is recursive."""
        keukenkastdeur = Label(NL, "de keukenkastdeur", roots=("de keukenkast", "de deur"))
        keukenkast = Label(NL, "de keukenkast", roots=("de keuken", "de kast"))
        keuken = Label(NL, "de keuken")
        kast = Label(NL, "de kast")
        deur = Label(NL, "de deur")
        self.assertEqual(Labels([keukenkast, keuken, kast, deur]), keukenkastdeur.roots)

    def test_recursive_compounds(self):
        """Test that getting the compounds is recursive."""
        keukenkastdeur = Label(NL, "de keukenkastdeur", roots=("de keukenkast", "de deur"))
        keukenkast = Label(NL, "de keukenkast", roots=("de keuken", "de kast"))
        keuken = Label(NL, "de keuken")
        kast = Label(NL, "de kast")
        deur = Label(NL, "de deur")
        self.assertEqual(Labels([keukenkastdeur, keukenkast]), kast.compounds)
        self.assertEqual(Labels([keukenkastdeur, keukenkast]), keuken.compounds)
        self.assertEqual(Labels([keukenkastdeur]), deur.compounds)
        self.assertEqual(Labels([keukenkastdeur]), keukenkast.compounds)


class LabelsTest(ToistoTestCase):
    """Unit tests for the Labels class."""

    def test_repr(self):
        """Test the representation of multiple labels."""
        self.assertEqual("('English', 'Nederlands')", repr(Labels([Label(EN, "English"), Label(NL, "Nederlands")])))

    def test_compounds(self):
        """Test that all compounds of all labels are returned."""
        raam = Label(NL, "het raam")
        zolder = Label(NL, "de zolder")
        zolderraam = Label(NL, "het zolderraam", roots=("de zolder", "het raam"))
        self.assertEqual((zolderraam,), Labels([raam]).compounds)
        self.assertEqual((zolderraam,), Labels([zolder]).compounds)
