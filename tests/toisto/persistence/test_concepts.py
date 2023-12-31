"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.persistence.concepts import ConceptLoader

from ...base import ToistoTestCase


class LoadConceptsTest(ToistoTestCase):
    """Unit tests for loading the concepts."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        self.concept_loader = ConceptLoader(ArgumentParser())

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_concepts_by_filename(self, stderr_write: Mock):
        """Test that an error message is given when the concept file does not exist."""
        self.assertRaises(SystemExit, self.concept_loader.load, [Path("file-doesnt-exist")])
        self.assertIn(
            "cannot read concept file file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("sys.stderr.write")
    def test_load_concepts_with_same_concept_id(self, stderr_write: Mock, path_open: Mock):
        """Test that an error message is given when a concept file contains the same concept id as another file."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concept_id": {"fi": "label1", "nl": "Label2"}}\n',
            '{"concept_id": {"fi": "Label3", "nl": "Label4"}}\n',
        ]
        self.assertRaises(SystemExit, self.concept_loader.load, [Path("file1"), Path("file2")])
        self.assertIn(
            f"Toisto cannot read concept file {Path('file2')}: concept identifier 'concept_id' also occurs in "
            f"concept file {Path('file1')}.\n",
            stderr_write.call_args_list[1][0][0],
        )
