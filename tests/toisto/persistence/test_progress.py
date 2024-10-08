"""Unit tests for the persistence module."""

from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from toisto.model.language import FI, Language
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.retention import Retention
from toisto.persistence.progress import load_progress, save_progress, update_progress_dict
from toisto.persistence.progress_format import ProgressDict

from ...base import ToistoTestCase


class ProgressTestCase(ToistoTestCase):
    """Base class for unit tests that test loading and saving progress."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigParser()
        self.config.add_section("identity")
        self.config["identity"]["uuid"] = "uuid"
        self.config.add_section("progress")
        self.config["progress"]["folder"] = "/home/user"


class LoadProgressTest(ProgressTestCase):
    """Unit tests for loading progress."""

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("pathlib.Path.open", MagicMock())
    def test_load_non_existing_progress(self) -> None:
        """Test that the default value is returned when the progress cannot be loaded."""
        self.assertEqual({}, load_progress(FI, Quizzes(), ArgumentParser(), self.config).as_dict())

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.glob", Mock(return_value=[Path("/home/user/.toisto-uuid-progress-en.json")]))
    @patch("sys.stderr.write")
    @patch("pathlib.Path.open")
    def test_load_invalid_progress(self, path_open: Mock, stderr_write: Mock) -> None:
        """Test that the the program exists if the progress cannot be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = "invalid"
        self.assertRaises(SystemExit, load_progress, Language("en"), Quizzes(), ArgumentParser(), self.config)
        self.assertIn("cannot parse the progress information in /home/user", stderr_write.call_args_list[1][0][0])

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.glob", Mock(return_value=[Path("/home/user/.toisto-uuid-progress-en.json")]))
    @patch("pathlib.Path.open")
    def test_load_existing_progress(self, path_open: Mock) -> None:
        """Test that the progress can be loaded."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz:read": {}}'
        self.assertEqual(
            {"quiz:read": Retention().as_dict()},
            load_progress(Language("nl"), Quizzes(), ArgumentParser(), self.config).as_dict(),
        )

    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.glob", Mock(return_value=[Path("/home/user/.toisto-uuid-progress-en.json")]))
    @patch("pathlib.Path.open")
    def test_invalid_actions_are_ignored(self, path_open: Mock) -> None:
        """Test that keys in the progress file with invalid actions are ignored."""
        path_open.return_value.__enter__.return_value.read.return_value = '{"quiz:read": {}, "quiz:invalid action": {}}'
        self.assertEqual(
            {"quiz:read": Retention().as_dict()},
            load_progress(Language("nl"), Quizzes(), ArgumentParser(), self.config).as_dict(),
        )


class SaveProgressTest(ProgressTestCase):
    """Unit tests for saving progress."""

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_empty_progress(self, dump: Mock, path_open: Mock) -> None:
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(Language("fi"), Quizzes(), {}), self.config)
        dump.assert_called_once_with({}, json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_incorrect_only_progress(self, dump: Mock, path_open: Mock) -> None:
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(Language("fi"), Quizzes(), {"quiz:read": {}}), self.config)
        dump.assert_called_once_with({"quiz:read": {}}, json_file)

    @patch("pathlib.Path.open")
    @patch("json.dump")
    def test_save_progress(self, dump: Mock, path_open: Mock) -> None:
        """Test that the progress can be saved."""
        path_open.return_value.__enter__.return_value = json_file = MagicMock()
        save_progress(Progress(Language("fi"), Quizzes(), {"quiz:read": dict(skip_until="3000-01-01")}), self.config)
        dump.assert_called_once_with({"quiz:read": dict(skip_until="3000-01-01T00:00:00")}, json_file)


class UpdateProgressTest(ToistoTestCase):
    """Unit tests for the update progress method."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.grey: ProgressDict = {
            "grey:nl:fi:grijs:write": {
                "start": "2023-03-06T22:29:25",
                "end": "2024-01-07T11:57:10",
                "skip_until": "2028-03-19T07:15:58",
                "count": 5,
            }
        }
        self.friday_key = "friday:fi:nl:perjantai:read"
        self.friday: ProgressDict = {
            self.friday_key: {
                "start": "2023-03-06T22:29:47",
                "end": "2023-12-03T13:53:57",
                "skip_until": "2027-08-22T18:54:49",
                "count": 5,
            }
        }
        self.friday2: ProgressDict = {
            self.friday_key: {
                "start": "2023-03-06T22:29:47",
                "end": "2023-12-04T13:53:57",
                "skip_until": "2027-09-22T18:54:49",
                "count": 6,
            }
        }
        self.friday_paused: ProgressDict = {
            self.friday_key: {
                "skip_until": "2028-09-21T18:00:00",
            }
        }
        self.friday_paused2: ProgressDict = {
            self.friday_key: {
                "skip_until": "2020-09-21T18:00:00",
            }
        }

    def test_updating_an_empty_progress_dict_with_no_other_progress_dicts(self):
        """Test that updating an empty progress without other progress dicts leaves the progress dict unchanged."""
        empty: ProgressDict = {}
        update_progress_dict(empty)
        self.assertEqual({}, empty)

    def test_updating_an_empty_progress_dict_with_an_empty_progress_dict(self):
        """Test that updating an empty progress dict with an empty progress dict results in an empty progress dict."""
        empty: ProgressDict = {}
        update_progress_dict(empty, {})
        self.assertEqual({}, empty)

    def test_updating_a_progress_dict_with_no_other_progress_dict(self):
        """Test that updating a progress dict without other progress dicts leaves the progress dict unchanged."""
        expected = self.grey.copy()
        update_progress_dict(self.grey)
        self.assertEqual(expected, self.grey)

    def test_updating_with_self(self):
        """Test that updating a progress dict with copy of itself leaves the progress dict unchanged."""
        expected = self.grey.copy()
        update_progress_dict(self.grey, self.grey.copy())
        self.assertEqual(expected, self.grey)

    def test_updating_an_empty_progress_dict(self):
        """Test that updating an empty progress dict with a non-empty one results in the non-empty progress dict."""
        empty: ProgressDict = {}
        update_progress_dict(empty, self.friday)
        self.assertEqual({self.friday_key: {"skip_until": self.friday[self.friday_key].get("skip_until", "")}}, empty)

    def test_updating_with_an_empty_progress_dict(self):
        """Test that updating an non-empty progress dict with an empty one results in the non-empty progress dict."""
        expected = self.grey.copy()
        update_progress_dict(self.grey, {})
        self.assertEqual(expected, self.grey)

    def test_updating_a_progress_dict_with_a_different_progress_dict(self):
        """Test that updating a progress dict with a different one results in a combined progress dict."""
        expected = {**self.grey, self.friday_key: {"skip_until": self.friday[self.friday_key].get("skip_until", "")}}
        update_progress_dict(self.grey, self.friday)
        self.assertEqual(expected, self.grey)

    def test_update_with_later_skip_until(self):
        """Test updating a retention with a later skip_until."""
        expected = self.friday.copy()
        expected[self.friday_key]["skip_until"] = self.friday2[self.friday_key].get("skip_until", "")
        update_progress_dict(self.friday, self.friday2)
        self.assertEqual(expected, self.friday)

    def test_update_with_earlier_skip_until(self):
        """Test updating a retention with an earlier skip_until."""
        expected = self.friday2.copy()
        update_progress_dict(self.friday2, self.friday)
        self.assertEqual(expected, self.friday2)

    def test_update_with_skipped_concept(self):
        """Test that updating an existing retention retains the start, end, and count of the existing retention."""
        expected: ProgressDict = {
            self.friday_key: {
                "start": "2023-03-06T22:29:47",
                "end": "2023-12-03T13:53:57",
                "skip_until": self.friday_paused[self.friday_key].get("skip_until") or "",
                "count": 5,
            }
        }
        update_progress_dict(self.friday, self.friday_paused)
        self.assertEqual(expected, self.friday)

    def test_update_skipped_concept_with_earlier_skip_until(self):
        """Test updating a skipped retention with an earlier skip_until."""
        expected = self.friday_paused.copy()
        update_progress_dict(self.friday_paused, self.friday)
        self.assertEqual(expected, self.friday_paused)

    def test_update_skipped_concept_with_later_skip_until(self):
        """Test updating a skipped retention with a later skip_until."""
        expected: ProgressDict = {
            self.friday_key: {"skip_until": self.friday2[self.friday_key].get("skip_until") or ""}
        }
        update_progress_dict(self.friday_paused2, self.friday2)
        self.assertEqual(expected, self.friday_paused2)
