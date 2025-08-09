"""Unit tests for labels."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label, Labels

from ....base import ToistoTestCase


class LabelTest(ToistoTestCase):
    """Unit tests for the Label class."""

    def test_equality(self):
        """Test that labels are not equal to non-labels."""
        label = same_label = Label(EN, "English")
        labels_equal = label == same_label
        self.assertTrue(labels_equal)
        labels_not_equal = label != same_label
        self.assertFalse(labels_not_equal)
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
        self.assertEqual((Label(NL, "de keuken"), Label(NL, "de kast")), label.roots)

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
        self.assertEqual((keukenkast, keuken, kast, deur), keukenkastdeur.roots)

    def test_recursive_compounds(self):
        """Test that getting the compounds is recursive."""
        keukenkastdeur = Label(NL, "de keukenkastdeur", roots=("de keukenkast", "de deur"))
        keukenkast = Label(NL, "de keukenkast", roots=("de keuken", "de kast"))
        keuken = Label(NL, "de keuken")
        kast = Label(NL, "de kast")
        deur = Label(NL, "de deur")
        self.assertEqual((keukenkastdeur, keukenkast), kast.compounds)
        self.assertEqual((keukenkastdeur, keukenkast), keuken.compounds)
        self.assertEqual((keukenkastdeur,), deur.compounds)
        self.assertEqual((keukenkastdeur,), keukenkast.compounds)

    def test_meaning_only(self):
        """Test that a label can be a meaning only."""
        mämmi = Label(NL, "Finse paascake", meaning_only=True)
        self.assertTrue(mämmi.meaning_only)

    def test_homonym_within_concept(self):
        """Test homonyms within one concept."""
        concept = self.create_verb_with_grammatical_number_and_person()
        i_read, you_read_singular, _, _, you_read_plural, _ = concept.labels(EN)
        self.assertEqual((), i_read.homographs)
        self.assertEqual((you_read_plural,), you_read_singular.homographs)
        self.assertEqual((you_read_singular,), you_read_plural.homographs)

    def test_homonym_between_concepts(self):
        """Test homonyms between concepts."""
        bank_concept = self.create_concept("bank", labels=[{"label": "de bank", "language": NL}])
        couch_concept = self.create_concept("couch", labels=[{"label": "de bank", "language": NL}])
        (bank,) = bank_concept.labels(NL)
        (couch,) = couch_concept.labels(NL)
        self.assertEqual((bank,), couch.homographs)
        self.assertEqual((couch,), bank.homographs)

    def test_capitonyms_within_concept(self):
        """Test capitonyms within one concept."""
        concept = self.create_concept(
            "to be",
            labels=[
                {
                    "label": {"singular": {"second person": "Te olette"}, "plural": {"second person": "te olette"}},
                    "language": FI,
                }
            ],
        )
        Te_olette, te_olette = concept.labels(FI)  # noqa: N806
        self.assertEqual((Te_olette,), te_olette.capitonyms)
        self.assertEqual((te_olette,), Te_olette.capitonyms)


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
