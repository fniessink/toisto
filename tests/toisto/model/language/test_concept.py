"""Unit tests for concepts."""

from typing import get_args

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept, ConceptId, ConceptRelation
from toisto.model.language.label import Label

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = self.create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertIsNone(concept.parent)
        self.assertEqual((), concept.constituents)
        self.assertEqual((), concept.labels(FI))
        self.assertEqual((), concept.meanings(FI))
        self.assertEqual((), concept.roots(FI))
        self.assertEqual((), concept.compounds(FI))
        self.assertFalse(concept.answer_only)
        for relation in get_args(ConceptRelation):
            self.assertEqual((), concept.get_related_concepts(relation))

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = self.create_concept("thirty", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances.get_values(ConceptId("thirty"))[0])

    def test_meaning_leaf_concept(self):
        """Test the meaning of a leaf concept."""
        concept = self.create_concept("one", dict(fi="yksi", nl="een"))
        self.assertEqual((Label(FI, "yksi"),), concept.meanings(FI))
        self.assertEqual((Label(NL, "een"),), concept.meanings(NL))
        self.assertEqual((), concept.meanings(EN))

    def test_meaning_composite_concept(self):
        """Test the meaning of a composite concept."""
        concept = self.create_concept(
            "table",
            dict(singular=dict(en="table", nl="de tafel"), plural=dict(en="tables", nl="de tafels")),
        )
        self.assertEqual((Label(EN, "table"), Label(EN, "tables")), concept.meanings(EN))
        self.assertEqual((Label(NL, "de tafel"), Label(NL, "de tafels")), concept.meanings(NL))
        self.assertEqual((), concept.meanings(FI))

    def test_meaning_mixed_concept(self):
        """Test the meaning of a concept that is leaf in one language and composite in another."""
        concept = self.create_concept(
            "to eat/third person",
            dict(fi="hän syö", female=dict(nl="zij eet"), male=dict(nl="hij eet")),
        )
        self.assertEqual((Label(FI, "hän syö"),), concept.meanings(FI))
        self.assertEqual((Label(NL, "zij eet"), Label(NL, "hij eet")), concept.meanings(NL))
        self.assertEqual((), concept.meanings(EN))
