"""Unit tests for labels."""

from itertools import permutations

from toisto.model.language import EN, FI, NL
from toisto.model.language.grammatical_form import GrammaticalForm
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
        label = Label(EN, "Christmas", notes=(note,))
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
        cake = Label(NL, "Finse paascake", meaning_only=True)
        self.assertTrue(cake.meaning_only)

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
            "olla",
            labels=[
                {
                    "label": {"singular": {"second person": "Te olette"}, "plural": {"second person": "te olette"}},
                    "language": FI,
                }
            ],
        )
        singular, plural = concept.labels(FI)
        self.assertEqual((singular,), plural.capitonyms)
        self.assertEqual((plural,), singular.capitonyms)

    def test_grammatical_form(self):
        """Test grammatical form."""
        house = Label(EN, "house")
        mouse = Label(EN, "mouse")
        self.assertTrue(mouse.has_same_grammatical_form(house))
        mouse = Label(EN, "mouse", GrammaticalForm("mouse", "singular"))
        mice = Label(EN, "mice", GrammaticalForm("mouse", "plural"))
        self.assertFalse(mouse.has_same_grammatical_form(mice))

    def test_grammatical_form_diminutive(self):
        """Test the grammatical form of diminutives."""
        mouse = Label(EN, "mouse", GrammaticalForm("mouse", "singular"))
        mice = Label(EN, "mice", GrammaticalForm("mouse", "plural"))
        muis = Label(NL, "de muis", GrammaticalForm("de muis", "root", "singular"))
        muisje = Label(NL, "het muisje", GrammaticalForm("de muis", "diminutive", "singular"))
        muizen = Label(NL, "de muizen", GrammaticalForm("de muis", "root", "plural"))
        muisjes = Label(NL, "de muisjes", GrammaticalForm("de muis", "diminutive", "plural"))
        for labels in ((mouse, mice), (muis, muizen, muisje, muisjes)):
            for form1, form2 in permutations(labels, r=2):
                self.assertFalse(form1.has_same_grammatical_form(form2))
        for diminutive in (muisje, muisjes):
            for root in (mouse, mice):
                self.assertFalse(diminutive.has_same_grammatical_form(root))
                self.assertFalse(root.has_same_grammatical_form(diminutive))
        self.assertTrue(muis.has_same_grammatical_form(mouse))
        self.assertTrue(mouse.has_same_grammatical_form(muis))
        self.assertTrue(muizen.has_same_grammatical_form(mice))
        self.assertTrue(mice.has_same_grammatical_form(muizen))

    def test_grammatical_form_abbreviation(self):
        """Test the grammatical form of abbeviations."""
        onder_andere = Label(NL, "onder andere", GrammaticalForm("onder andere", "full form"))
        o_a = Label(NL, "o.a.", GrammaticalForm("onder andere", "abbreviation"))
        among_others = Label(EN, "among others")
        self.assertFalse(onder_andere.has_same_grammatical_form(o_a))
        self.assertFalse(o_a.has_same_grammatical_form(onder_andere))
        self.assertTrue(onder_andere.has_same_grammatical_form(among_others))
        self.assertTrue(among_others.has_same_grammatical_form(onder_andere))
        self.assertFalse(among_others.has_same_grammatical_form(o_a))
        self.assertFalse(o_a.has_same_grammatical_form(among_others))


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
