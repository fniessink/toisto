"""Unit tests for concepts."""

from itertools import product
from typing import TYPE_CHECKING, cast, get_args

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept, ConceptId, ConceptRelation
from toisto.model.language.label import Label

from ....base import ToistoTestCase

if TYPE_CHECKING:
    from toisto.model.language.grammar import GrammaticalCategory


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
        table = Label(EN, "table", grammatical_categories=("singular",))
        tables = Label(EN, "tables", grammatical_categories=("plural",))
        self.assertEqual((table, tables), concept.meanings(EN))
        tafel = Label(NL, "de tafel", grammatical_categories=("singular",))
        tafels = Label(NL, "de tafels", grammatical_categories=("plural",))
        self.assertEqual((tafel, tafels), concept.meanings(NL))
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
        zij_eet = Label(NL, "zij eet", grammatical_categories=("feminine",))
        hij_eet = Label(NL, "hij eet", grammatical_categories=("masculine",))
        self.assertEqual((zij_eet, hij_eet), concept.meanings(NL))
        self.assertEqual((), concept.meanings(EN))

    def test_labels(self):
        """Test that the labels are returned, recursively."""
        concept = self.create_verb_with_grammatical_number_and_person()
        expected_label_values = ("I have", "you have", "she has", "we have", "you have", "they have")
        grammatical_categories = product(("singular", "plural"), ("first person", "second person", "third person"))
        expected_labels = tuple(
            Label(EN, label, grammatical_categories=cast("tuple[GrammaticalCategory]", grammatical_categories))
            for label, grammatical_categories in zip(expected_label_values, grammatical_categories, strict=False)
        )
        self.assertEqual(expected_labels, concept.labels(EN))

    def test_labels_for_invariant_noun(self):
        """Test that the labels are returned, recursively."""
        concept = self.create_noun_invariant_in_english()
        self.assertEqual((Label(EN, "means of transportation"),), concept.labels(EN))
        vervoersmiddel = Label(NL, "het vervoersmiddel", grammatical_categories=("singular",))
        vervoersmiddelen = Label(NL, "de vervoersmiddelen", grammatical_categories=("plural",))
        self.assertEqual((vervoersmiddel, vervoersmiddelen), concept.labels(NL))

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
        self.assertFalse(
            self.create_concept("involves only", {"involves": ConceptId("other concept")}).is_complete_sentence
        )
        composite_concept = self.create_concept(
            "the house is big",
            labels=[{"label": {"singular": "The house is big.", "plural": "The houses are big."}, "language": EN}],
        )
        self.assertTrue(composite_concept.is_complete_sentence)
