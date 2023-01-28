"""Unit tests for concepts."""

from ...base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_level(self):
        """Test that the level of a concept is the maximum of the available levels."""
        concept = self.create_concept("one", dict(level=dict(EP="A1", OD="A2"), fi="Kolmekymmentä", nl="Dertig"))
        self.assertEqual("A2", concept.level)
