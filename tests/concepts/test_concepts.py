"""Integration tests for the concepts."""

from argparse import ArgumentParser
from typing import ClassVar

from toisto.metadata import BUILT_IN_LANGUAGES, CONCEPT_JSON_FILES
from toisto.model.language.concept import Concept, ConceptId
from toisto.persistence.loader import Loader

from ..base import ToistoTestCase


class ConceptsTest(ToistoTestCase):
    """Integration tests for the concepts."""

    concepts: ClassVar[set[Concept]]

    @classmethod
    def setUpClass(cls) -> None:
        """Extend to set up test fixtures."""
        super().setUpClass()
        cls.concepts = Loader(ArgumentParser()).load(*CONCEPT_JSON_FILES)

    def test_load_concepts(self):
        """Test that the concepts can be loaded."""
        self.assertEqual(1, len(Concept.instances.get_values(ConceptId("welcome"))))

    def test_roots_exist(self):
        """Test that all roots use existing concept ids."""
        for concept in self.concepts:
            for root in concept.roots(self.fi):
                self.assertIn(root, Concept.instances.get_values(root.concept_id))

    def test_examples_exist(self):
        """Test that all examples use existing concept ids."""
        for concept in self.concepts:
            for example in concept.get_related_concepts("example"):
                self.assertIn(example, Concept.instances.get_values(example.concept_id))

    def test_that_not_all_labels_of_a_concept_are_spoken_language(self):
        """Test that not all labels of a concept are spoken language."""
        for concept in self.concepts:
            for language in BUILT_IN_LANGUAGES:
                for leaf_concept in concept.leaf_concepts(language):
                    labels = leaf_concept.labels(language)
                    if labels and all(label.is_colloquial for label in labels):
                        self.fail(f"{leaf_concept} has only colloquial labels")
