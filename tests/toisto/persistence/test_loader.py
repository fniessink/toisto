"""Integration tests for the concepts."""

from argparse import ArgumentParser
from pathlib import Path
from typing import cast
from unittest.mock import Mock, patch

from toisto.model.language.concept import ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.topic.topic import Topic, TopicId
from toisto.persistence.loader import Loader

from ...base import ToistoTestCase


class LoadConceptsTest(ToistoTestCase):
    """Unit tests for loading the concepts."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.loader = Loader(ArgumentParser())

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_non_existing_file(self, stderr_write: Mock):
        """Test that an error message is given when the concept file does not exist."""
        self.assertRaises(SystemExit, self.loader.load, [Path("file-doesnt-exist")])
        self.assertIn(
            "cannot read file file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("sys.stderr.write")
    def test_load_concepts_with_same_concept_id(self, stderr_write: Mock, path_open: Mock):
        """Test that an error message is given when a concept file contains the same concept id as another file."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concepts": {"concept_id": {"fi": "label1", "nl": "Label2"}}}\n',
            '{"concepts": {"concept_id": {"fi": "Label3", "nl": "Label4"}}}\n',
        ]
        self.assertRaises(SystemExit, self.loader.load, [Path("file1"), Path("file2")])
        self.assertIn(
            f"Toisto cannot read file {Path('file2')}: concept identifier 'concept_id' also occurs in "
            f"file {Path('file1')}.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("sys.stderr.write")
    def test_load_topic_with_same_topic_id(self, stderr_write: Mock, path_open: Mock):
        """Test that an error message is given when a concept file contains the same concept id as another file."""
        topics_json = '{"topics": {"topic": {"concepts": ["to be"]}}}'
        path_open.return_value.__enter__.return_value.read.return_value = topics_json
        self.loader.load([Path("filename")])
        self.assertRaises(SystemExit, self.loader.load, [Path("filename")])
        self.assertIn(
            f"Toisto cannot read file {Path('filename')}: topic identifier 'topic' occurs multiple times in "
            f"file {Path('filename')}.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_concepts(self, path_open: Mock):
        """Test that the concepts are read."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concepts": {"concept_id": {"fi": "Label1", "nl": "Label2"}}}\n',
        ]
        concept = create_concept(ConceptId("concept_id"), cast(ConceptDict, {"fi": "Label1", "nl": "Label2"}))
        self.assertEqual(({concept}, set()), self.loader.load([Path("filename")]))

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_topics(self, path_open: Mock):
        """Test that the topics are read."""
        topics_json = '{"topics": {"topic": {"concepts": ["to be"]}}}'
        path_open.return_value.__enter__.return_value.read.return_value = topics_json
        self.assertEqual(
            (set(), {Topic(TopicId("topic"), frozenset([ConceptId("to be")]))}),
            self.loader.load([Path("filename")]),
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_composite_topics(self, path_open: Mock):
        """Test that composite topics are read."""
        topics_json = '{"topics": {"topic": {"concepts": ["to be"], "topics": ["other"]}}}'
        path_open.return_value.__enter__.return_value.read.return_value = topics_json
        self.assertEqual(
            (set(), {Topic(TopicId("topic"), frozenset([ConceptId("to be")]), frozenset([TopicId("other")]))}),
            self.loader.load([Path("filename")]),
        )
