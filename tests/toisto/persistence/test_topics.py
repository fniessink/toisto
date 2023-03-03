"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from typing import get_args
from unittest.mock import Mock, patch

from toisto.model.language.cefr import CommonReferenceLevel
from toisto.model.language.concept import ConceptId
from toisto.persistence.topics import load_topics

from ...base import ToistoTestCase


class LoadTopicsTest(ToistoTestCase):
    """Unit tests for loading the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        concept = self.create_concept(ConceptId("welcome"))
        self.quiz = self.create_quiz(concept, "fi", "nl", "Tervetuloa", ["Welkom"])
        self.levels = get_args(CommonReferenceLevel)

    def test_load_topic_by_name(self):
        """Test that a subset of the built-in topics can be loaded by name."""
        self.assertNotIn(self.quiz, load_topics("fi", "nl", self.levels, ["family"], [], ArgumentParser()).quizzes)

    def test_load_topic_by_level(self):
        """Test that a subset of the built-in concepts can be loaded by level."""
        all_topics = load_topics("fi", "nl", self.levels[0:1], ["family"], [], ArgumentParser())
        for topic in all_topics:
            for concept in topic.concepts:
                self.assertEqual(self.levels[0], concept.level)

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_topic_by_filename(self, stderr_write: Mock):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(SystemExit, load_topics, "fi", "nl", self.levels, [], ["file-doesnt-exist"], ArgumentParser())
        self.assertIn(
            "cannot read topic file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("sys.stderr.write")
    def test_load_topics_with_same_concept_id(self, stderr_write: Mock, path_open: Mock):
        """Test that an error message is given when a topic file contains the same concept id as another topic file."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concept_id": {"fi": "label1", "nl": "Label2"}}\n',
            '{"concept_id": {"fi": "Label3", "nl": "Label4"}}\n',
        ]
        self.assertRaises(SystemExit, load_topics, "fi", "nl", [], [], ["file1", "file2"], ArgumentParser())
        self.assertIn(
            "Toisto cannot read topic file2: concept identifier 'concept_id' also occurs in topic 'file1'.\n",
            stderr_write.call_args_list[1][0][0],
        )
