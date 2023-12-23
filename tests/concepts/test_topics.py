"""Integration tests for the topics."""

from argparse import ArgumentParser

from toisto.metadata import CONCEPT_JSON_FILES, TOPIC_FILES
from toisto.persistence.concepts import ConceptIdRegistry, load_concepts
from toisto.persistence.topics import load_topics

from ..base import ToistoTestCase


class TopicsTest(ToistoTestCase):
    """Integration tests for the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        argument_parser = ArgumentParser()
        self.concepts = load_concepts(CONCEPT_JSON_FILES, ConceptIdRegistry(argument_parser), argument_parser)
        self.all_concept_ids = {concept.concept_id for concept in self.concepts}
        self.topics = load_topics(TOPIC_FILES, argument_parser)

    def test_all_concepts_have_at_least_one_topic(self):
        """Test that all concepts have at least one topic."""
        concept_ids_with_topics = set()
        for topic in self.topics:
            concept_ids_with_topics |= topic.concepts
        self.assertSetEqual(set(), concept_ids_with_topics - self.all_concept_ids)

    def test_all_topic_concepts_exist(self):
        """Test that all topic concepts exist."""
        for topic in self.topics:
            self.assertTrue(topic.concepts.issubset(self.all_concept_ids))
