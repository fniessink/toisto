"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Required, TypedDict, cast

from . import Language
from .concept import ConceptIdListOrString
from .grammar import GrammaticalCategory
from .label import Label, Labels

JSONGrammar = dict[GrammaticalCategory, str]
JSONRecursiveGrammar = dict[GrammaticalCategory, JSONGrammar]

LabelJSON = TypedDict(
    "LabelJSON",
    {
        "colloquial": bool,
        "concept": Required[ConceptIdListOrString],
        "label": Required[str | list[str] | JSONGrammar | JSONRecursiveGrammar],
        "language": Required[Language],
        "meaning-only": bool,
        "note": str | list[str],
        "roots": str | list[str],
        "tip": str,
    },
    total=False,
)


@dataclass(frozen=True)
class LabelFactory:
    """Create Labels from the label JSON."""

    labels: list[LabelJSON]

    def create_labels(self) -> Labels:
        """Create labels from the list of JSON labels."""
        return Labels([self._create_label(label) for label in self.labels if self._is_label(label)])

    def create_meanings(self) -> Labels:
        """Create meanings from the list of JSON labels."""
        return Labels([self._create_meaning(label) for label in self.labels if self._is_meaning(label)])

    def _is_label(self, label: LabelJSON) -> bool:
        """Return whether the JSON label is a label, meaning it is a leaf label and not meaning-only."""
        return self._is_leaf_label(label) and not label.get("meaning-only", False)

    def _is_meaning(self, label: LabelJSON) -> bool:
        """Return whether the JSON label is a meaning, so it can be used to explain the meaning of a concept."""
        return self._is_leaf_label(label) and not label.get("colloquial", False)

    def _is_leaf_label(self, label: LabelJSON) -> bool:
        """Return whether the label is a leaf label, meaning it has no grammar."""
        return isinstance(label["label"], (str, list))

    def _create_label(self, label: LabelJSON) -> Label:
        """Create a label from the label JSON."""
        value = cast("str | list[str]", label["label"])
        note = label.get("note", [])
        notes = tuple([note] if isinstance(note, str) else note)
        tip = label.get("tip", "")
        colloquial = label.get("colloquial", False)
        root_or_roots = label.get("roots", [])
        roots = tuple([root_or_roots] if isinstance(root_or_roots, str) else root_or_roots)
        return Label(label["language"], value, notes, roots, tip, colloquial=colloquial)

    def _create_meaning(self, label: LabelJSON) -> Label:
        """Create a meaning label from the label JSON."""
        return Label(label["language"], cast("str | list[str]", label["label"]))
