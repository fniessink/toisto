"""Test loading the IANA language subtag registry."""

import unittest
from unittest.mock import Mock, patch

from toisto.persistence.iana_language_subtag_registry import load_languages


@patch("toisto.persistence.iana_language_subtag_registry.Path.open")
class TestLoadLanguages(unittest.TestCase):
    """Test loading the languages."""

    def test_empty_file(self, path_open: Mock) -> None:
        """Test loading an empty file."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = ""
        self.assertEqual({}, load_languages())

    def test_one_language(self, path_open: Mock) -> None:
        """Test loading one language."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = [
            "%%\n",
            "Type: language\n",
            "Subtag: fi\n",
            "Description: Finnish\n",
            "Added: 2005-10-16\n",
            "Suppress-Script: Latn\n",
            "%%\n",
        ]
        self.assertEqual({"fi": "Finnish"}, load_languages())

    def test_multiple_languages(self, path_open: Mock) -> None:
        """Test loading multiple languages."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = [
            "%%\n",
            "Type: language\n",
            "Subtag: fi\n",
            "Description: Finnish\n",
            "Added: 2005-10-16\n",
            "Suppress-Script: Latn\n",
            "%%\n",
            "Type: language\n",
            "Subtag: nl\n",
            "Description: Dutch\n",
            "Description: Flemish\n",
            "Added: 2005-10-16\n",
            "Suppress-Script: Latn\n",
            "%%\n",
        ]
        self.assertEqual({"fi": "Finnish", "nl": "Dutch"}, load_languages())

    def test_line_continuation(self, path_open: Mock) -> None:
        """Test loading a language with a continuation line."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = [
            "%%\n",
            "Type: language\n",
            "Subtag: ia\n",
            "Description: Interlingua (International Auxiliary Language\n",
            "  Association)\n",
            "Added: 2005-10-16\n",
            "%%\n",
        ]
        self.assertEqual({"ia": "Interlingua (International Auxiliary Language Association)"}, load_languages())

    def test_retain_colon(self, path_open: Mock) -> None:
        """Test that colons in the description are retained."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = [
            "%%\n",
            "Type: language\n",
            "Subtag: ia\n",
            "Description: Interlingua: International Auxiliary Language\n",
            "  Association\n",
            "Added: 2005-10-16\n",
            "%%\n",
        ]
        self.assertEqual({"ia": "Interlingua: International Auxiliary Language Association"}, load_languages())
