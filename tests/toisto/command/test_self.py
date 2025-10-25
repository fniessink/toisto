"""Unit tests for the self commands."""

from argparse import ArgumentParser
from unittest.mock import Mock, patch

from toisto.command.self import Self
from toisto.metadata import VERSION

from ...base import ToistoTestCase


class SelfTestCase(ToistoTestCase):
    """Base class for installation command unit tests."""

    def setUp(self) -> None:
        """Set up Self fixture."""
        self.self = Self(ArgumentParser())


@patch("toisto.command.self.check_output")
class SelfUninstallTests(SelfTestCase):
    """Unit tests for the self uninstall command."""

    def test_uninstall_with_uv(self, check_output: Mock) -> None:
        """Test uninstall with uv."""
        self.self.tool = "uv tool"
        self.assertRaises(SystemExit, self.self.uninstall)
        check_output.assert_called_with(["uv", "tool", "uninstall", "toisto"])

    def test_uninstall_with_pipx(self, check_output: Mock) -> None:
        """Test uninstall with pipx."""
        self.self.tool = "pipx"
        self.assertRaises(SystemExit, self.self.uninstall)
        check_output.assert_called_with(["pipx", "uninstall", "toisto"])

    def test_uninstall_with_pip(self, check_output: Mock) -> None:
        """Test uninstall with pip."""
        self.self.tool = "pip"
        self.assertRaises(SystemExit, self.self.uninstall)
        check_output.assert_called_with(["pip", "uninstall", "--yes", "toisto"])


@patch("toisto.command.self.check_output")
class SelfUpgradeTests(SelfTestCase):
    """Unit tests for the self upgrade command."""

    def test_upgrade_with_uv(self, check_output: Mock) -> None:
        """Test upgrade with uv."""
        self.self.tool = "uv tool"
        self.assertRaises(SystemExit, self.self.upgrade)
        check_output.assert_called_with(["uv", "tool", "upgrade", "toisto"])

    def test_upgrade_with_pipx(self, check_output: Mock) -> None:
        """Test upgrade with pipx."""
        self.self.tool = "pipx"
        self.assertRaises(SystemExit, self.self.upgrade)
        check_output.assert_called_with(["pipx", "upgrade", "toisto"])

    def test_upgrade_with_pip(self, check_output: Mock) -> None:
        """Test upgrade with pip."""
        self.self.tool = "pip"
        self.assertRaises(SystemExit, self.self.upgrade)
        check_output.assert_called_with(["pip", "install", "--upgrade", "toisto"])


class SelfVersionTests(SelfTestCase):
    """Unit tests for the self version command."""

    @patch("toisto.command.self.latest_version", Mock(return_value="v9999"))
    def test_version(self) -> None:
        """Test that the current version is shown."""
        with patch("rich.console.Console.print") as patched_print:
            self.assertRaises(SystemExit, self.self.version)
        patched_print.assert_called_once_with(
            f"[white not bold]v{VERSION}[/white not bold] ([white not bold]v9999[/white not bold] is available, "
            "run [code]toisto self upgrade[/code] to install)"
        )
