"""Integration tests for the concepts."""

from argparse import ArgumentParser
from typing import ClassVar, get_args

from toisto.metadata import BUILT_IN_CONCEPT_JSON_FILES, BUILT_IN_LANGUAGES
from toisto.model.language.concept import Concept, ConceptId, NonInvertedConceptRelation
from toisto.persistence.concept_loader import ConceptLoader

from ..base import ToistoTestCase


class ConceptsTest(ToistoTestCase):
    """Integration tests for the concepts."""

    concepts: ClassVar[set[Concept]]

    @classmethod
    def setUpClass(cls) -> None:
        """Extend to set up test fixtures."""
        super().setUpClass()
        cls.concepts = ConceptLoader(ArgumentParser()).load_concepts(*BUILT_IN_CONCEPT_JSON_FILES)

    @classmethod
    def tearDownClass(cls) -> None:
        """Extend to clear the concept instances."""
        super().tearDownClass()
        Concept.instances.clear()

    def tearDown(self):
        """Override to not clear the concept instances after each test."""

    def test_load_concepts(self):
        """Test that the concepts can be loaded."""
        self.assertEqual(1, len(Concept.instances.get_values(ConceptId("welcome"))))

    def test_roots_exist(self):
        """Test that all roots use existing concept ids."""
        for concept in self.concepts:
            for language in BUILT_IN_LANGUAGES:
                for root in concept.roots(language):
                    self.assertIn(root, Concept.instances.get_values(root.concept_id))

    def test_related_concepts_exist(self):
        """Test that all related concepts use existing concept ids."""
        for concept in self.concepts:
            for relation in get_args(NonInvertedConceptRelation):
                for related_concept in concept.get_related_concepts(relation):
                    self.assertIn(related_concept, Concept.instances.get_values(related_concept.concept_id))

    def test_that_not_all_labels_of_a_concept_are_spoken_language(self):
        """Test that not all labels of a concept are spoken language."""
        for concept in self.concepts:
            for language in BUILT_IN_LANGUAGES:
                labels = concept.labels(language)
                if labels and all(label.colloquial for label in labels):
                    self.fail(f"{concept} has only colloquial labels in {language}")
