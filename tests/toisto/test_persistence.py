"""Unit tests for the persistence module."""

import unittest
from unittest.mock import patch, MagicMock, Mock

from toisto.model import QuizProgress, Progress, Quiz
from toisto.persistence import dump_json, load_quizzes, load_json, load_progress, save_progress


class PersistenceTestCase(unittest.TestCase):
    """Base class for persistence unit tests."""

    def setUp(self):
        """Override to set up the file path."""
        self.file_path = MagicMock()
        self.contents = dict(foo="bar")


class LoadJSONTest(PersistenceTestCase):
    """Unit tests for loading JSON."""

    def test_return_default_if_file_does_not_exist(self):
        """Test that the default value is returned if the file does not exist."""
        self.file_path.exists.return_value = False
        self.assertEqual(self.contents, load_json(self.file_path, default=self.contents))

    def test_return_file_contents(self):
        """Test that the JSON contents are returned if the file exists."""
        self.file_path.exists.return_value = True
        self.file_path.open.return_value.__enter__.return_value.read.return_value = '{"foo": "bar"}'
        self.assertEqual(self.contents, load_json(self.file_path))


class DumpJSONTest(PersistenceTestCase):
    """Unit tests for dumping JSON."""

    @patch("json.dump")
    def test_dump(self, dump):
        """Test that the JSON is dumped."""
        self.file_path.open.return_value.__enter__.return_value = json_file = MagicMock()
        dump_json(self.file_path, self.contents)
        dump.assert_called_once_with(self.contents, json_file)


class LoadEntriesTest(unittest.TestCase):
    """Unit tests for loading the entries."""

    def test_load_entries(self):
        """Test that the entries can be loaded."""
        self.assertIn(Quiz("fi", "nl", "Tervetuloa", ["Welkom"]), load_quizzes("fi", []))

    def test_load_entries_by_name(self):
        """Test that a subsetof the entries can be loaded."""
        self.assertNotIn(Quiz("fi", "nl", "Tervetuloa", ["Welkom"]), load_quizzes("fi", ["family"]))


class ProgressPersistenceTest(unittest.TestCase):
    """Test loading and saving the progress."""

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("pathlib.Path.open", MagicMock())
    def test_load_non_existing_progress(self):
        """Test that the default value is returned when the progress cannot be loaded."""
        self.assertEqual({}, load_progress().progress_dict)

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("sys.stderr", Mock())
    @patch("pathlib.Path.open")
    def test_load_invalid_progress(self, path_open):
        """Test that the the program exists if the progress cannot be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = ""
        self.assertRaises(SystemExit, load_progress)

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_existing_progress(self, path_open):
        """Test that the progress can be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz": {"count": 0}}'
        self.assertEqual(dict(quiz=QuizProgress()), load_progress().progress_dict)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_empty_progress(self, dump, path_open):
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress({}))
        dump.assert_called_once_with({}, json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_incorrect_only_progress(self, dump, path_open):
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(dict(quiz=dict(count=0))))
        dump.assert_called_once_with(dict(quiz=dict(count=0)), json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_progress(self, dump, path_open):
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(dict(quiz=dict(count=5, silence_until="3000-01-01"))))
        dump.assert_called_once_with(dict(quiz=dict(count=5, silence_until="3000-01-01T00:00:00")), json_file)