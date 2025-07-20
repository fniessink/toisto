"""Unit tests for meta data functions."""

import unittest
from unittest.mock import Mock, patch

from toisto.metadata import installation_tool


class InstallationToolTests(unittest.TestCase):
    """Unit tests for the installation_tool method."""

    @patch("toisto.metadata.check_output", Mock(return_value="toisto"))
    def test_uv(self) -> None:
        """Test that the installation tool is uv."""
        self.assertEqual("uv tool", installation_tool())

    @patch("toisto.metadata.check_output", Mock(side_effect=["", "toisto"]))
    def test_pipx(self) -> None:
        """Test that the installation tool is pipx."""
        self.assertEqual("pipx", installation_tool())

    @patch("toisto.metadata.check_output", Mock(side_effect=["", ""]))
    def test_pip(self) -> None:
        """Test that the installation tool is pipx."""
        self.assertEqual("pip", installation_tool())
