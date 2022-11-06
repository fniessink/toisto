"""Labels."""

from typing import cast


class Label(str):
    """Class representing labels for concepts."""
    def __eq__(self, other) -> bool:
        """Ignore hints when determining equality."""
        return self.split(";", maxsplit=1)[0] == other.split(";", maxsplit=1)[0]

    def __ne__(self, other) -> bool:
        """Return whether the labels are not equal."""
        return not self == other

    def spelling_alternatives(self) -> "Labels":
        """Extract the spelling alternatives from the label."""
        return [self.__class__(label) for label in self.split(";", maxsplit=1)[0].split("|")]

    def first_spelling_alternative(self) -> "Label":
        """Extract the first spelling alternative from the label."""
        return self.spelling_alternatives()[0]

    def hint(self) -> str:
        """Return the label hint, if any."""
        return self.split(";")[1] if ";" in self else ""


Labels = list[Label]


def label_factory(string: str | list[str]) -> Labels:
    """Instantiate the labels from a string or list of strings."""
    labels = string if isinstance(string, list) else [string]
    return cast(Labels, [Label(label) for label in labels])
