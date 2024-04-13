"""Integration tests for the concepts."""

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.model.language import FI, NL
from toisto.persistence.loader import Loader

from ...base import ToistoTestCase


class LoadConceptsTest(ToistoTestCase):
    """Unit tests for loading the concepts."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        super().setUp()
        self.loader = Loader(ArgumentParser())

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_non_existing_file(self, stderr_write: Mock) -> None:
        """Test that an error message is given when the concept file does not exist."""
        self.assertRaises(SystemExit, self.loader.load, Path("file-doesnt-exist"))
        self.assertIn(
            "cannot read file file-doesnt-exist: [Errno 2] No such file or directory: 'file-doesnt-exist'.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("sys.stderr.write")
    def test_load_concepts_with_same_concept_id(self, stderr_write: Mock, path_open: Mock) -> None:
        """Test that an error message is given when a concept file contains the same concept id as another file."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concept_id": {"fi": "label1", "nl": "Label2"}}\n',
            '{"concept_id": {"fi": "Label3", "nl": "Label4"}}\n',
        ]
        self.assertRaises(SystemExit, self.loader.load, Path("file1"), Path("file2"))
        self.assertIn(
            f"Toisto cannot read file {Path('file2')}: concept identifier 'concept_id' also occurs in "
            f"file {Path('file1')}.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_concepts(self, path_open: Mock) -> None:
        """Test that the concepts are read."""
        path_open.return_value.__enter__.return_value.read.side_effect = [
            '{"concept_id": {"fi": "Label1", "nl": "Label2"}}\n',
        ]
        concept = self.create_concept("concept_id", {FI: "Label1", NL: "Label2"})
        self.assertEqual({concept}, self.loader.load(Path("filename")))
