"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.model.language.concept import ConceptId
from toisto.model.topic.topic import Topic
from toisto.persistence.topics import load_topics

from ...base import ToistoTestCase


class LoadTopicsTest(ToistoTestCase):
    """Unit tests for loading the topics."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.argument_parser = ArgumentParser()

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_topics_from_non_existing_file(self, stderr_write: Mock):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(SystemExit, load_topics, [Path("file-doesnt-exist")], self.argument_parser)
        self.assertIn(
            "cannot read topic file file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_topics(self, path_open: Mock):
        """Test that the topics are read."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"name": "topic", "concepts": ["to be"]}'
        self.assertSetEqual(
            {Topic("topic", frozenset([ConceptId("to be")]))},
            load_topics([Path("filename")], self.argument_parser),
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_composite_topics(self, path_open: Mock):
        """Test that the composite topics are read."""
        topic_json = '{"name": "topic", "concepts": ["to be"], "topics": ["other"]}'
        path_open.return_value.__enter__.return_value.read.return_value = topic_json
        self.assertSetEqual(
            {Topic("topic", frozenset([ConceptId("to be")]), frozenset(["other"]))},
            load_topics([Path("filename")], self.argument_parser),
        )
