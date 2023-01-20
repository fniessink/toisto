"""Unit tests for the persistence module."""

import unittest
from argparse import ArgumentParser
from unittest.mock import patch, MagicMock, Mock

from toisto.model import Progress, Retention, Topics
from toisto.persistence import load_progress, save_progress
from toisto.persistence.progress import PROGRESS_JSON


class ProgressPersistenceTest(unittest.TestCase):
    """Test loading and saving the progress."""

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("pathlib.Path.open", MagicMock())
    def test_load_non_existing_progress(self):
        """Test that the default value is returned when the progress cannot be loaded."""
        self.assertEqual({}, load_progress(Topics(set()), ArgumentParser()).as_dict())

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("sys.stderr.write")
    @patch("pathlib.Path.open")
    def test_load_invalid_progress(self, path_open, stderr_write):
        """Test that the the program exists if the progress cannot be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = ""
        self.assertRaises(SystemExit, load_progress, Topics(set()), ArgumentParser())
        self.assertIn(f"cannot parse the progress information in {PROGRESS_JSON}", stderr_write.call_args_list[1][0][0])

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_existing_progress(self, path_open):
        """Test that the progress can be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz": {}}'
        self.assertEqual(dict(quiz=Retention().as_dict()), load_progress(Topics(set()), ArgumentParser()).as_dict())

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_empty_progress(self, dump, path_open):
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress({}, Topics(set())))
        dump.assert_called_once_with({}, json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_incorrect_only_progress(self, dump, path_open):
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(dict(quiz={}), Topics(set())))
        dump.assert_called_once_with(dict(quiz={}), json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_progress(self, dump, path_open):
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(dict(quiz=dict(skip_until="3000-01-01")), Topics(set())))
        dump.assert_called_once_with(dict(quiz=dict(skip_until="3000-01-01T00:00:00")), json_file)
