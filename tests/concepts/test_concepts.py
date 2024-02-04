"""Integration tests for the concepts."""

from argparse import ArgumentParser

from toisto.model.language.concept import Concept
from toisto.persistence.loader import Loader

from ..base import ToistoTestCase


class ConceptsTest(ToistoTestCase):
    """Integration tests for the concepts."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        self.concept = self.create_concept("welcome", {})
        self.concepts = Loader(ArgumentParser()).load()

    def test_load_concepts(self):
        """Test that the concepts can be loaded."""
        self.assertIn(self.concept.concept_id, [concept.concept_id for concept in self.concepts])

    def test_uses_exist(self):
        """Test that all roots use existing concept ids."""
        for concept in self.concepts:
            for root in concept.roots(self.fi):
                self.assertIn(root.concept_id, Concept.instances)
