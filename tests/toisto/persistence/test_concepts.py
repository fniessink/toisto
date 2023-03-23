"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.persistence.concepts import ConceptIdRegistry, load_concepts

from ...base import ToistoTestCase


class LoadConceptsTest(ToistoTestCase):
    """Unit tests for loading the concepts."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.argument_parser = ArgumentParser()
        self.concept_id_registry = ConceptIdRegistry(self.argument_parser)

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_concepts_by_filename(self, stderr_write: Mock):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(
            SystemExit,
            load_concepts,
            [Path("file-doesnt-exist")],
            self.concept_id_registry,
            self.argument_parser,
        )
        self.assertIn(
            "cannot read topic file file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
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
        self.assertRaises(
            SystemExit,
            load_concepts,
            [Path("file1"), Path("file2")],
            self.concept_id_registry,
            self.argument_parser,
        )
        self.assertIn(
            f"Toisto cannot read topic file {Path('file2')}: concept identifier 'concept_id' also occurs in "
            f"topic file {Path('file1')}.\n",
            stderr_write.call_args_list[1][0][0],
        )
