"""Unit tests for concepts."""

from typing import get_args

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept, ConceptId, ConceptRelation
from toisto.model.language.label import Label, Labels

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = self.create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertEqual((), concept.labels(FI))
        self.assertEqual((), concept.meanings(FI))
        self.assertFalse(concept.answer_only)
        for relation in get_args(ConceptRelation):
            self.assertEqual((), concept.get_related_concepts(relation))

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = self.create_concept(
            "thirty", labels=[{"label": "kolmekymmentä", "language": FI}, {"label": "dertig", "language": NL}]
        )
        self.assertEqual(concept, Concept.instances.get_values(ConceptId("thirty"))[0])

    def test_meaning(self):
        """Test the meaning of a concept."""
        concept = self.create_concept(
            "one", labels=[{"label": "yksi", "language": FI}, {"label": "een", "language": NL}]
        )
        self.assertEqual((Label(FI, "yksi"),), concept.labels(FI))
        self.assertEqual((Label(FI, "yksi"),), concept.meanings(FI))
        self.assertEqual((Label(NL, "een"),), concept.labels(NL))
        self.assertEqual((Label(NL, "een"),), concept.meanings(NL))
        self.assertEqual((), concept.labels(EN))
        self.assertEqual((), concept.meanings(EN))

    def test_meaning_only(self):
        """Test that a label can be meaning-only."""
        concept = self.create_concept(
            "mämmi",
            labels=[
                {"label": "mämmi", "language": FI},
                {"label": "Finse paascake", "language": NL, "meaning-only": True},
            ],
        )
        self.assertEqual((Label(FI, "mämmi"),), concept.labels(FI))
        self.assertEqual((Label(FI, "mämmi"),), concept.meanings(FI))
        self.assertEqual((), concept.labels(NL))
        self.assertEqual((Label(NL, "Finse paascake"),), concept.meanings(NL))
        self.assertEqual((), concept.labels(EN))
        self.assertEqual((), concept.meanings(EN))

    def test_meaning_with_composite_labels(self):
        """Test the meaning of a concept with composite labels."""
        concept = self.create_concept(
            "table",
            labels=[
                {"label": {"singular": "table", "plural": "tables"}, "language": EN},
                {"label": {"singular": "de tafel", "plural": "de tafels"}, "language": NL},
            ],
        )
        self.assertEqual((Label(EN, "table"), Label(EN, "tables")), concept.meanings(EN))
        self.assertEqual((Label(NL, "de tafel"), Label(NL, "de tafels")), concept.meanings(NL))
        self.assertEqual((), concept.meanings(FI))

    def test_meaning_mixed_concept(self):
        """Test the meaning of a concept that has a composite label in one language and not in another."""
        concept = self.create_concept(
            "to eat/third person",
            labels=[
                {"label": "hän syö", "language": FI},
                {"label": {"feminine": "zij eet", "masculine": "hij eet"}, "language": NL},
            ],
        )
        self.assertEqual((Label(FI, "hän syö"),), concept.meanings(FI))
        self.assertEqual((Label(NL, "zij eet"), Label(NL, "hij eet")), concept.meanings(NL))
        self.assertEqual((), concept.meanings(EN))

    def test_labels(self):
        """Test that the labels are returned, recursively."""
        concept = self.create_verb_with_grammatical_number_and_person()
        expected_labels = ("I have", "you have", "she has", "we have", "you have", "they have")
        self.assertEqual(Labels(Label(EN, label) for label in expected_labels), concept.labels(EN))

    def test_labels_for_invariant_noun(self):
        """Test that the labels are returned, recursively."""
        concept = self.create_noun_invariant_in_english()
        self.assertEqual((Label(EN, "means of transportation"),), concept.labels(EN))
        self.assertEqual((Label(NL, "het vervoersmiddel"), Label(NL, "de vervoersmiddelen")), concept.labels(NL))

    def test_homographs(self):
        """Test that notes are ignored when determining homographs."""
        bank = self.create_concept("bank", labels=[{"label": "de bank", "language": NL, "note": "some note"}])
        sofa = self.create_concept("sofa", labels=[{"label": "de bank", "language": NL}])
        self.assertEqual((bank,), sofa.get_homographs(Label(NL, "de bank")))

    def test_capitonyms(self):
        """Test that notes are ignored when determining capitonyms."""
        greece = self.create_concept("greece", labels=[{"label": "Kreikki", "language": FI}])
        greek = self.create_concept(
            "greek",
            labels=[
                {"label": "kreikki", "language": FI, "note": "In Finnish, the names of languages are not capitalized"}
            ],
        )
        self.assertEqual((greece,), greek.get_capitonyms(Label(FI, "kreikki")))

    def test_is_sentence(self):
        """Test the is-sentence property."""
        self.assertFalse(self.create_concept("sea", labels=[{"label": "sea", "language": EN}]).is_complete_sentence)
        self.assertFalse(
            self.create_concept("greece", labels=[{"label": "Greece", "language": EN}]).is_complete_sentence
        )
        self.assertTrue(self.create_concept("hi", labels=[{"label": "Hei!", "language": FI}]).is_complete_sentence)
        self.assertTrue(
            self.create_concept(
                "meaning only", labels=[{"label": "Hei!", "language": FI, "meaning-only": True}]
            ).is_complete_sentence
        )
        self.assertFalse(self.create_concept("involves only", {"involves": ["other concept"]}).is_complete_sentence)
        composite_concept = self.create_concept(
            "the house is big",
            labels=[{"label": {"singular": "The house is big.", "plural": "The houses are big."}, "language": EN}],
        )
        self.assertTrue(composite_concept.is_complete_sentence)
