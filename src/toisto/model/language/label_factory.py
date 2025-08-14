"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NotRequired, Required, TypedDict, cast

from toisto.tools import first

from . import Language
from .concept import ConceptIdListOrString
from .grammar import GrammaticalCategory, GrammaticalForm
from .label import Label, Labels

JSONGrammar = dict[GrammaticalCategory, str]
JSONRecursiveGrammar = dict[GrammaticalCategory, JSONGrammar]

LabelJSON = TypedDict(
    "LabelJSON",
    {
        "colloquial": NotRequired[bool],
        "concept": Required[ConceptIdListOrString],
        "label": Required[str | list[str] | JSONGrammar | JSONRecursiveGrammar],
        "language": Required[Language],
        "meaning-only": NotRequired[bool],
        "note": NotRequired[str | list[str]],
        "roots": NotRequired[str | list[str]],
        "tip": NotRequired[str],
    },
    total=True,
)


@dataclass(frozen=True)
class LabelFactory:
    """Create Labels from the label JSON."""

    grammatical_base: str = ""

    def create_labels(self, json_labels: list[LabelJSON], *grammatical_categories: GrammaticalCategory) -> Labels:
        """Create labels from the list of JSON labels."""
        labels: list[Label] = []
        for json_label in json_labels:
            if isinstance(json_label["label"], (str, list)):
                labels.append(self._create_label(json_label, *grammatical_categories))
            else:
                grammatical_base_for_slices = self.grammatical_base or self.grammatical_base_for(json_label)
                factory = LabelFactory(grammatical_base_for_slices)
                for grammatical_category, json_label_value in json_label["label"].items():
                    json_label_slice = json_label.copy()
                    json_label_slice["label"] = json_label_value
                    slice_grammatical_categories = (*grammatical_categories, grammatical_category)
                    labels.extend(factory.create_labels([json_label_slice], *slice_grammatical_categories))
        return Labels(labels)

    def _create_label(self, label: LabelJSON, *grammatical_categories: GrammaticalCategory) -> Label:
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
            GrammaticalForm(self.grammatical_base, *grammatical_categories),
            notes,
            roots,
            tip,
            colloquial=colloquial,
            meaning_only=meaning_only,
        )

    @classmethod
    def grammatical_base_for(cls, json_label: LabelJSON) -> str:
        """Return the grammatical base of the JSON label."""
        if isinstance(json_label["label"], str):
            return json_label["label"]
        if isinstance(json_label["label"], list):
            return first(json_label["label"])
        json_label_slice = json_label.copy()
        json_label_slice["label"] = cast("str | JSONRecursiveGrammar", first(json_label["label"].values()))
        return cls.grammatical_base_for(json_label_slice)
