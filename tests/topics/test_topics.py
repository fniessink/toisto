"""Integration tests for the topics."""

from argparse import ArgumentParser

from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import create_concept
from toisto.persistence.concepts import load_concepts

from ..base import ToistoTestCase


class TopicsTest(ToistoTestCase):
    """Integration tests for the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = create_concept(ConceptId("welcome"))
        self.concepts = load_concepts([], [], [], ArgumentParser())

    def test_load_concepts(self):
        """Test that the concepts can be loaded."""
        self.assertIn(self.concept.concept_id, [concept.concept_id for concept in self.concepts])

    def test_uses_exist(self):
        """Test that all roots use existing concept ids."""
        for concept in self.concepts:
            for root in concept.roots("fi"):
                self.assertIn(root.concept_id, Concept.instances)
