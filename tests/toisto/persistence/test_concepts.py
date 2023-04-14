"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from typing import get_args
from unittest.mock import Mock, patch

from toisto.model.language.cefr import CommonReferenceLevel
from toisto.model.language.concept import ConceptId
from toisto.model.language.concept_factory import create_concept
from toisto.persistence.concepts import load_concepts

from ...base import ToistoTestCase


class LoadConceptsTest(ToistoTestCase):
    """Unit tests for loading the concepts."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = create_concept(ConceptId("welcome"))
        self.levels = get_args(CommonReferenceLevel)

    def test_load_concepts_by_name(self):
        """Test that a subset of the built-in concepts can be loaded by name."""
        concepts = load_concepts(self.levels, ["family"], [], ArgumentParser())
        self.assertNotIn(self.concept.concept_id, [concept.concept_id for concept in concepts])

    def test_load_concepts_by_level(self):
        """Test that a subset of the built-in concepts can be loaded by level."""
        concepts = load_concepts(self.levels[0:1], ["family"], [], ArgumentParser())
        for concept in concepts:
            self.assertEqual(self.levels[0], concept.level)

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_concepts_by_filename(self, stderr_write: Mock):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(SystemExit, load_concepts, self.levels, [], ["file-doesnt-exist"], ArgumentParser())
        self.assertIn(
            "cannot read topic file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("sys.stderr.write")
    def test_load_concepts_with_same_concept_id(self, stderr_write: Mock, path_open: Mock):
        """Test that an error message is given when a topic file contains the same concept id as another topic file."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concept_id": {"fi": "label1", "nl": "Label2"}}\n',
            '{"concept_id": {"fi": "Label3", "nl": "Label4"}}\n',
        ]
        self.assertRaises(SystemExit, load_concepts, [], [], ["file1", "file2"], ArgumentParser())
        self.assertIn(
            "Toisto cannot read topic file2: concept identifier 'concept_id' also occurs in topic 'file1'.\n",
            stderr_write.call_args_list[1][0][0],
        )
