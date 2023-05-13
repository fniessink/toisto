"""Unit tests for concepts."""

from toisto.model.language.concept import Concept
from toisto.model.language.concept_factory import create_concept

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertEqual((), concept.labels("fi"))
        self.assertEqual((), concept.meanings("fi"))
        self.assertIsNone(concept.level)
        self.assertEqual({"<unknown topic>"}, concept.topics)
        self.assertEqual((), concept.answers)
        self.assertFalse(concept.answer_only)
        self.assertEqual((), concept.roots("fi"))
        self.assertIsNone(concept.parent)
        self.assertEqual((), concept.constituents)
        self.assertEqual((), concept.antonyms)

    def test_level(self):
        """Test that the level of a concept is the maximum of the available levels."""
        concept = create_concept("one", dict(level=dict(A1="EP", A2="OD"), fi="kolmekymmentä", nl="dertig"))
        self.assertEqual("A2", concept.level)

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = create_concept("one", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances["one"])
