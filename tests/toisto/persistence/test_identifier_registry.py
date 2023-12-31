"""Unit tests for the identifier registry class."""

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.persistence.identifier_registry import IdentifierRegistry

from ...base import ToistoTestCase


class IdentifierRegistryUnderTest(IdentifierRegistry[int]):
    """Indentifier registry with integers as identifiers."""

    def _identifier_name(self) -> str:
        """Override to return the identifier name."""
        return "integer"


class IdentifierRegistryTest(ToistoTestCase):
    """Unit tests for the identifier registry."""

    def setUp(self) -> None:
        """Set up the registry."""
        self.registry = IdentifierRegistryUnderTest(ArgumentParser())

    @patch("sys.stderr.write")
    def test_same_identifier_in_different_files(self, stderr_write: Mock):
        """Test that an error is thrown when the identifier has already been registered."""
        self.registry.check_and_register_identifiers((0, 1, 2), Path("foo"))
        self.assertRaises(SystemExit, self.registry.check_and_register_identifiers, (3, 2, 1), Path("bar"))
        self.assertIn(
            f"Toisto cannot read integer file {Path('bar')}: integer identifier '2' also occurs in "
            f"integer file {Path('foo')}.\n",
            stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.stderr.write")
    def test_same_identifier_multiple_times_in_one_file(self, stderr_write: Mock):
        """Test that an error is thrown when the identifier is registered multiple times for the same file."""
        self.assertRaises(SystemExit, self.registry.check_and_register_identifiers, (3, 2, 2, 1), Path("bar"))
        self.assertIn(
            f"Toisto cannot read integer file {Path('bar')}: integer identifier '2' occurs multiple times in "
            f"integer file {Path('bar')}.\n",
            stderr_write.call_args_list[1][0][0],
        )
