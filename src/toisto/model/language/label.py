"""Labels."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final


class Label(str):
    """Class representing labels for concepts."""

    __slots__ = ()

    # Labels can have one question note and multiple answer notes. The question note is shown before a quiz is
    # presented to the user. The answer notes are shown afterwards. The format is:
    # 'label;question note;answer note 1;answer note 2;...'
    NOTE_SEP: Final = ";"
    QUESTION_NOTE_INDEX: Final = 1
    ANSWER_NOTE_INDEX: Final = 2
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
    def question_note(self) -> str:
        """Return the label question note."""
        has_question_note = self.count(self.NOTE_SEP) >= self.QUESTION_NOTE_INDEX
        return self.split(self.NOTE_SEP)[self.QUESTION_NOTE_INDEX] if has_question_note else ""

    @property
    def answer_notes(self) -> Sequence[str]:
        """Return the label answer notes."""
        has_answer_notes = self.count(self.NOTE_SEP) >= self.ANSWER_NOTE_INDEX
        return self.split(self.NOTE_SEP)[self.ANSWER_NOTE_INDEX :] if has_answer_notes else ()

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
