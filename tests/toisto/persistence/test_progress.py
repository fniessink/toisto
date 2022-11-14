"""Unit tests for the persistence module."""

import unittest
from unittest.mock import patch, MagicMock, Mock

from toisto.metadata import NAME
from toisto.model import Progress, QuizProgress
from toisto.persistence import load_progress, save_progress
from toisto.persistence.progress import PROGRESS_JSON


class ProgressPersistenceTest(unittest.TestCase):
    """Test loading and saving the progress."""

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("pathlib.Path.open", MagicMock())
    def test_load_non_existing_progress(self):
        """Test that the default value is returned when the progress cannot be loaded."""
        self.assertEqual({}, load_progress().as_dict())

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("sys.stderr.write")
    @patch("pathlib.Path.open")
    def test_load_invalid_progress(self, path_open, stderr_write):
        """Test that the the program exists if the progress cannot be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = ""
        self.assertRaises(SystemExit, load_progress)
        stderr_write.assert_called_with(
            f"{NAME} cannot parse the progress information in {PROGRESS_JSON}: Expecting value: line 1 column 1 "
            f"(char 0).\nTo fix this, remove or rename {PROGRESS_JSON} and start {NAME} again. Unfortunately, this "
            "will reset your progress.\nPlease consider opening a bug report at https://github.com/fniessink/toisto. "
            "Be sure to attach the invalid\nprogress file to the issue.\n"
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_existing_progress(self, path_open):
        """Test that the progress can be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz": {"count": 0}}'
        self.assertEqual(dict(quiz=QuizProgress().as_dict()), load_progress().as_dict())

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_progress_with_answer_lists(self, path_open):
        """Test that the progress format where answers were lists can be loaded."""
        old_key = "Quiz(question_language='fi', answer_language='fi', _question='Kirkko', _answers=['Kirkot'], " \
            "quiz_type='pluralize')"
        new_key = "Quiz(question_language='fi', answer_language='fi', _question='Kirkko', _answers=('Kirkot',), " \
            "quiz_type='pluralize')"
        silence_until = "2022-11-14T15:27:44.020854"
        json_text = f'{{"{old_key}": {{"count": 15, "silence_until": "{silence_until}"}}}}'
        path_open.return_value.__enter__.return_value.read.return_value = json_text
        self.assertEqual({new_key: dict(count=15, silence_until=silence_until)}, load_progress().as_dict())

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
