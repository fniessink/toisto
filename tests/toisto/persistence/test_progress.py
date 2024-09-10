"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from unittest.mock import MagicMock, Mock, patch

from toisto.model.language import FI, Language
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.retention import Retention
from toisto.persistence.progress import get_progress_filepath, load_progress, save_progress

from ...base import ToistoTestCase


class LoadProgressTest(ToistoTestCase):
    """Unit tests for loading progress."""

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("pathlib.Path.open", MagicMock())
    def test_load_non_existing_progress(self) -> None:
        """Test that the default value is returned when the progress cannot be loaded."""
        self.assertEqual({}, load_progress(FI, Quizzes(), ArgumentParser()).as_dict())

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("sys.stderr.write")
    @patch("pathlib.Path.open")
    def test_load_invalid_progress(self, path_open: Mock, stderr_write: Mock) -> None:
        """Test that the the program exists if the progress cannot be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = ""
        language = Language("en")
        self.assertRaises(SystemExit, load_progress, language, Quizzes(), ArgumentParser())
        progress_file = get_progress_filepath(language)
        self.assertIn(f"cannot parse the progress information in {progress_file}", stderr_write.call_args_list[1][0][0])

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_load_existing_progress(self, path_open: Mock) -> None:
        """Test that the progress can be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz:read": {}}'
        self.assertEqual(
            {"quiz:read": Retention().as_dict()}, load_progress(Language("nl"), Quizzes(), ArgumentParser()).as_dict()
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def test_invalid_actions_are_ignored(self, path_open: Mock) -> None:
        """Test that keys in the progress file with invalid actions are ignored."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz:read": {}, "quiz:invalid action": {}}'
        self.assertEqual(
            {"quiz:read": Retention().as_dict()}, load_progress(Language("nl"), Quizzes(), ArgumentParser()).as_dict()
        )


class SaveProgressTest(ToistoTestCase):
    """Unit tests for saving progress."""

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_empty_progress(self, dump: Mock, path_open: Mock) -> None:
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress({}, Language("fi"), Quizzes()))
        dump.assert_called_once_with({}, json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_incorrect_only_progress(self, dump: Mock, path_open: Mock) -> None:
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress({"quiz:read": {}}, Language("fi"), Quizzes()))
        dump.assert_called_once_with({"quiz:read": {}}, json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_progress(self, dump: Mock, path_open: Mock) -> None:
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress({"quiz:read": dict(skip_until="3000-01-01")}, Language("fi"), Quizzes()))
        dump.assert_called_once_with({"quiz:read": dict(skip_until="3000-01-01T00:00:00")}, json_file)
