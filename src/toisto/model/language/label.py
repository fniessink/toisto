"""Labels."""

from __future__ import annotations


class Label(str):
    """Class representing labels for concepts."""

    HINT_SEP = ";"
    SPELLING_ALTERNATIVES_SEP = "|"

    def __eq__(self, other: object) -> bool:
        """Ignore hints when determining equality."""
        return self.without_hint == Label(other).without_hint

    def __ne__(self, other: object) -> bool:
        """Return whether the labels are not equal."""
        return not self == other

    def __hash__(self) -> int:
        """Return the hash of the label, ignoring hints."""
        return hash(self.without_hint)

    @property
    def spelling_alternatives(self) -> Labels:
        """Extract the spelling alternatives from the label."""
        return label_factory(self.without_hint.split(self.SPELLING_ALTERNATIVES_SEP))

    @property
    def hint(self) -> str:
        """Return the label hint, if any."""
        return self.split(self.HINT_SEP)[1] if self.HINT_SEP in self else ""

    @property
    def without_hint(self) -> str:
        """Return the label without the hint."""
        return self.split(self.HINT_SEP)[0]


Labels = tuple[Label, ...]


def label_factory(string: str | list[str]) -> Labels:
    """Instantiate the labels from a string or list of strings."""
    labels = string if isinstance(string, list) else [string]
    return tuple(Label(label) for label in labels if not label.startswith("("))


def meaning_factory(string: str | list[str]) -> Labels:
    """Instantiate the meanings from a string or list of strings."""
    meanings = string if isinstance(string, list) else [string]
    return (Label(meanings[0].strip("(").strip(")")),) if meanings else Labels()
