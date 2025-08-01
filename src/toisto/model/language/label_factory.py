"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Required, TypedDict, cast
from uuid import uuid4

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

    json_labels: list[LabelJSON]

    def create_labels(
        self, grammatical_categories: tuple[GrammaticalCategory, ...] = (), grammatical_base: str = ""
    ) -> Labels:
        """Create labels from the list of JSON labels."""
        labels: list[Label] = []
        for json_label in self.json_labels:
            if isinstance(json_label["label"], (str, list)):
                labels.append(self._create_label(json_label, grammatical_categories, grammatical_base))
            else:
                grammatical_base_for_slices = grammatical_base or str(uuid4())
                for grammatical_category, json_label_value in json_label["label"].items():
                    json_label_slice = json_label.copy()
                    json_label_slice["label"] = json_label_value
                    labels.extend(
                        LabelFactory([json_label_slice]).create_labels(
                            (*grammatical_categories, grammatical_category), grammatical_base_for_slices
                        )
                    )
        return Labels(labels)

    def _create_label(
        self, label: LabelJSON, grammatical_categories: tuple[GrammaticalCategory, ...], grammatical_base: str
    ) -> Label:
        """Create a label from the label JSON."""
        value = cast("str | list[str]", label["label"])
        note = label.get("note", [])
        notes = tuple([note] if isinstance(note, str) else note)
        tip = label.get("tip", "")
        colloquial = label.get("colloquial", False)
        meaning_only = label.get("meaning-only", False)
        root_or_roots = label.get("roots", [])
        roots = tuple([root_or_roots] if isinstance(root_or_roots, str) else root_or_roots)
        return Label(
            label["language"],
            value,
            notes,
            roots,
            tip,
            grammatical_base,
            grammatical_categories,
            colloquial=colloquial,
            meaning_only=meaning_only,
        )
