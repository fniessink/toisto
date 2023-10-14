"""Integration tests for the concepts."""

from argparse import ArgumentParser
from typing import cast

from toisto.metadata import CONCEPT_JSON_FILES
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.persistence.concepts import ConceptIdRegistry, load_concepts

from ..base import ToistoTestCase


class ConceptsTest(ToistoTestCase):
    """Integration tests for the concepts."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = create_concept(ConceptId("welcome"), cast(ConceptDict, {}))
        argument_parser = ArgumentParser()
        self.concepts = load_concepts(CONCEPT_JSON_FILES, ConceptIdRegistry(argument_parser), argument_parser)

    def test_load_concepts(self):
        """Test that the concepts can be loaded."""
        self.assertIn(self.concept.concept_id, [concept.concept_id for concept in self.concepts])

    def test_uses_exist(self):
        """Test that all roots use existing concept ids."""
        for concept in self.concepts:
            for root in concept.roots("fi"):
                self.assertIn(root.concept_id, Concept.instances)
