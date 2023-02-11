"""Integration tests for the topics."""

from argparse import ArgumentParser
from itertools import permutations
from typing import get_args

from toisto.metadata import SUPPORTED_LANGUAGES
from toisto.model.language.cefr import CommonReferenceLevel
from toisto.model.language.concept import Concept
from toisto.model.model_types import ConceptId
from toisto.persistence.topics import load_topics

from ..base import ToistoTestCase


class TopicsTest(ToistoTestCase):
    """Integration tests for the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        concept = self.create_concept(ConceptId("welcome"))
        self.quiz = self.create_quiz(concept, "fi", "nl", "Tervetuloa", ["Welkom"])
        self.levels = get_args(CommonReferenceLevel)

    def test_load_topics(self):
        """Test that the topics can be loaded."""
        self.assertIn(self.quiz, load_topics("fi", "nl", self.levels, [], [], ArgumentParser()).quizzes)

    def test_uses_exist(self):
        """Test that all uses relations use existing concept ids."""
        all_topics = load_topics("fi", "nl", self.levels, [], [], ArgumentParser())
        for topic in all_topics:
            for concept in topic.concepts:
                for uses in concept._used_concepts.get("fi", ()):  # noqa: SLF001
                    self.assertIn(uses, Concept.instances)

    def test_instructions(self):
        """Test that an instruction can be created for all quizzes."""
        for language1, language2 in permutations(SUPPORTED_LANGUAGES.keys(), r=2):
            for quiz in load_topics(language1, language2, self.levels, [], [], ArgumentParser()).quizzes:
                quiz.instruction()  # This raises KeyError if types of the quiz are not present in the instructions
