"""Integration tests for the concepts."""

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.model.language import FI, NL
from toisto.persistence.concept_loader import ConceptLoader

from ...base import ToistoTestCase

CONCEPT_FILE = """
{
    "concepts": {
        "concept_id1": {},
        "concept_id2": {}
    },
    "labels": {
        "fi": [{"concept": "concept_id1", "label": "Label1"}],
        "nl": [{"concept": ["concept_id1", "concept_id2"], "label": "Label2"}]
    }
}
"""


class LoadConceptsTest(ToistoTestCase):
    """Unit tests for loading the concepts."""

    def setUp(self) -> None:
        """Set up the test fixtures."""
        super().setUp()
        self.loader = ConceptLoader(ArgumentParser())

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_non_existing_file(self, stderr_write: Mock) -> None:
        """Test that an error message is given when the concept file does not exist."""
        self.assertRaises(SystemExit, self.loader.load_concepts, Path("file-doesnt-exist"))
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
            '{"concepts": {"concept_id": {}}}\n',
            '{"concepts": {"concept_id": {}}}\n',
        ]
        self.assertRaises(SystemExit, self.loader.load_concepts, Path("file1"), Path("file2"))
        self.assertIn(
            f"Toisto cannot read file {Path('file2')}: concept identifier 'concept_id' also occurs in "
            f"file {Path('file1')}.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_concepts(self, path_open: Mock) -> None:
        """Test that the concepts are read."""
        path_open.return_value.__enter__.return_value.read.side_effect = [CONCEPT_FILE]
        concept1 = self.create_concept(
            "concept_id1", labels=[{"label": "Label1", "language": FI}, {"label": "Label2", "language": NL}]
        )
        concept2 = self.create_concept("concept_id2", labels=[{"label": "Label2", "language": NL}])
        self.assertEqual({concept1, concept2}, self.loader.load_concepts(Path("filename")))

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.is_dir", Mock(side_effect=[True, False]))
    @patch("pathlib.Path.rglob", Mock(return_value=[Path("filename")]))
    @patch("pathlib.Path.open")
    def test_load_concepts_from_folder(self, path_open: Mock) -> None:
        """Test that the concepts are read from folders."""
        path_open.return_value.__enter__.return_value.read.side_effect = [CONCEPT_FILE]
        concept1 = self.create_concept(
            "concept_id1", labels=[{"label": "Label1", "language": FI}, {"label": "Label2", "language": NL}]
        )
        concept2 = self.create_concept("concept_id2", labels=[{"label": "Label2", "language": NL}])
        self.assertEqual({concept1, concept2}, self.loader.load_concepts(Path("folder")))
