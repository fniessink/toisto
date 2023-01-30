"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from itertools import permutations
from unittest.mock import Mock, patch

from toisto.model.model_types import ConceptId
from toisto.persistence.topics import load_topics

from ..base import ToistoTestCase


class LoadTopicsTest(ToistoTestCase):
    """Unit tests for loading the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        concept = self.create_concept(ConceptId("welcome"))
        self.quiz = self.create_quiz(concept, "fi", "nl", "Tervetuloa", ["Welkom"])

    def test_load_topics(self):
        """Test that the topics can be loaded."""
        self.assertIn(self.quiz, load_topics("fi", "nl", [], [], ArgumentParser()).quizzes)

    def test_uses_exist(self):
        """Test that all uses relations use existing concept ids."""
        all_topics = load_topics("fi", "nl", [], [], ArgumentParser())
        all_concept_ids = {concept.concept_id for topic in all_topics for concept in topic.concepts}
        for topic in all_topics:
            for concept in topic.concepts:
                for uses in concept.used_concepts("fi"):
                    self.assertIn(uses, all_concept_ids)

    def test_instructions(self):
        """Test that an instruction can be created for all quizzes."""
        for language1, language2 in permutations(["en", "fi", "nl"], r=2):
            for quiz in load_topics(language1, language2, [], [], ArgumentParser()).quizzes:
                quiz.instruction()  # This raises KeyError if types of the quiz are not present in the instructions

    def test_load_topic_by_name(self):
        """Test that a subset of the builtin topics can be loaded by name."""
        self.assertNotIn(self.quiz, load_topics("fi", "nl", ["family"], [], ArgumentParser()).quizzes)

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_topic_by_filename(self, stderr_write: Mock):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(SystemExit, load_topics, "fi", "nl", [], ["file-does-not-exist"], ArgumentParser())
        self.assertIn(
            "cannot read topic file-does-not-exist: [Errno 2] No such file or directory: 'file-does-not-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )
