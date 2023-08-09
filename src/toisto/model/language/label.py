"""Labels."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final


class Label(str):
    """Class representing labels for concepts."""

    __slots__ = ()

    NOTE_SEP: Final = ";"
    SPELLING_ALTERNATIVES_SEP: Final = "|"

    def __eq__(self, other: object) -> bool:
        """Ignore notes when determining equality."""
        return self.without_notes == Label(other).without_notes

    def __ne__(self, other: object) -> bool:
        """Return whether the labels are not equal."""
        return self.without_notes != Label(other).without_notes

    @property
    def spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label."""
        return label_factory(self.without_notes.split(self.SPELLING_ALTERNATIVES_SEP))

    @property
    def notes(self) -> Sequence[str]:
        """Return the label notes."""
        return self.split(self.NOTE_SEP)[1:] if self.NOTE_SEP in self else ()

    @property
    def without_notes(self) -> str:
        """Return the label without the notes."""
        return self.split(self.NOTE_SEP)[0]


Labels = tuple[Label, ...]


def label_factory(string: str | list[str]) -> Labels:
    """Instantiate the labels from a string or list of strings."""
    labels = string if isinstance(string, list) else [string]
    return tuple(Label(label) for label in labels if not label.startswith("("))


def meaning_factory(string: str | list[str]) -> Labels:
    """Instantiate the meanings from a string or list of strings."""
    meanings = string if isinstance(string, list) else [string]
    return (Label(meanings[0].removeprefix("(").removesuffix(")")),) if meanings else Labels()
