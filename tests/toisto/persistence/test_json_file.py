"""Unit tests for the persistence module."""

import unittest
from unittest.mock import MagicMock, Mock, patch

from toisto.persistence.json_file import dump_json, load_json


class PersistenceTestCase(unittest.TestCase):
    """Base class for persistence unit tests."""

    def setUp(self):
        """Override to set up the file path."""
        self.file_path = MagicMock()
        self.contents = {"foo": "bar"}


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
    def test_dump(self, dump: Mock) -> None:
        """Test that the JSON is dumped."""
        self.file_path.open.return_value.__enter__.return_value = json_file = MagicMock()
        dump_json(self.file_path, self.contents)
        dump.assert_called_once_with(self.contents, json_file)
