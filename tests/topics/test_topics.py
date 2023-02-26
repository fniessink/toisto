"""Integration tests for the topics."""

from argparse import ArgumentParser

from toisto.model.language import Language
from toisto.model.language.concept import Concept, ConceptId
from toisto.persistence.topics import load_topics

from ..base import ToistoTestCase


class TopicsTest(ToistoTestCase):
    """Integration tests for the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        concept = self.create_concept(ConceptId("welcome"))
        self.quiz = self.create_quiz(concept, "fi", "nl", "Tervetuloa", ["Welkom"])
        self.topics = load_topics(Language("fi"), Language("nl"), [], [], [], ArgumentParser())

    def test_load_topics(self):
        """Test that the topics can be loaded."""
        self.assertIn(self.quiz, self.topics.quizzes)

    def test_uses_exist(self):
        """Test that all roots use existing concept ids."""
        for topic in self.topics:
            for concept in topic.concepts:
                for root in concept.roots("fi"):
                    self.assertIn(root.concept_id, Concept.instances)
