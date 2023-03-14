"""Unit tests for concepts."""

from toisto.model.language.concept import Concept

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_level(self):
        """Test that the level of a concept is the maximum of the available levels."""
        concept = self.create_concept("one", dict(level=dict(A1="EP", A2="OD"), fi="kolmekymmentä", nl="dertig"))
        self.assertEqual("A2", concept.level)

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = self.create_concept("one", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances["one"])
