"""Labels."""

from __future__ import annotations

from typing import cast


class Label(str):
    """Class representing labels for concepts."""
    def __eq__(self, other) -> bool:
        """Ignore hints when determining equality."""
        return self.split(";", maxsplit=1)[0] == other.split(";", maxsplit=1)[0]

    def __ne__(self, other) -> bool:
        """Return whether the labels are not equal."""
        return not self == other

    def __hash__(self) -> int:
        """Return the hash of the label, ignoring hints."""
        return hash(self.split(";", maxsplit=1)[0])

    def spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label."""
        return tuple(self.__class__(label) for label in self.split(";", maxsplit=1)[0].split("|"))

    def first_spelling_alternative(self) -> Label:
        """Extract the first spelling alternative from the label."""
        return self.spelling_alternatives()[0]

    def hint(self) -> str:
        """Return the label hint, if any."""
        return self.split(";")[1] if ";" in self else ""


Labels = tuple[Label, ...]


def label_factory(string: str | list[str]) -> Labels:
    """Instantiate the labels from a string or list of strings."""
    labels = string if isinstance(string, list) else [string]
    return cast(Labels, tuple(Label(label) for label in labels))
