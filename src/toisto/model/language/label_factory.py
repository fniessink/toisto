"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NotRequired, Required, TypedDict, cast

from toisto.tools import first

from . import Language
from .concept import ConceptIdListOrString
from .grammatical_category import GrammaticalCategory
from .grammatical_form import GrammaticalForm
from .label import Label, Labels

JSONGrammar = str | list[str] | dict[GrammaticalCategory, "JSONGrammar"]

LabelJSON = TypedDict(
    "LabelJSON",
    {
        "cloze": NotRequired[JSONGrammar],
        "colloquial": NotRequired[bool],
        "concept": Required[ConceptIdListOrString],
        "label": Required[JSONGrammar],
        "language": Required[Language],
        "meaning-only": NotRequired[bool],
        "note": NotRequired[JSONGrammar],
        "roots": NotRequired[str | list[str]],
        "tip": NotRequired[JSONGrammar],
    },
    total=True,
)


@dataclass(frozen=True)
class LabelFactory:
    """Create Labels from the label JSON."""

    grammatical_base: str = ""

    def create_labels(self, json_labels: list[LabelJSON], *grammatical_categories: GrammaticalCategory) -> Labels:
        """Create labels from the list of JSON labels."""
        label_list: list[Label] = []
        for json_label in json_labels:
            if isinstance(json_label["label"], (str, list)):
                label_list.append(self._create_label(json_label, *grammatical_categories))
            else:
                grammatical_base_for_slices = self.grammatical_base or self.grammatical_base_for(json_label)
                factory = LabelFactory(grammatical_base_for_slices)
                for grammatical_category in json_label["label"]:
                    json_label_slice = self._slice_json_label(json_label, grammatical_category)
                    slice_grammatical_categories = (*grammatical_categories, grammatical_category)
                    label_list.extend(factory.create_labels([json_label_slice], *slice_grammatical_categories))
        labels = Labels(label_list)
        labels.register_other_grammatical_categories()
        return labels

    def _slice_json_label(self, json_label: LabelJSON, grammatical_category: GrammaticalCategory) -> LabelJSON:
        """Return the slice of the JSON label by grammatical category."""
        json_label_slice = json_label.copy()
        for attribute in ("label", "note", "tip", "cloze"):
            if (value := json_label.get(attribute)) and isinstance(value, dict):
                json_label_slice[attribute] = value.get(grammatical_category, [])
        return json_label_slice

    def _create_label(self, label: LabelJSON, *grammatical_categories: GrammaticalCategory) -> Label:
        """Create a label from the label JSON."""
        value = cast("str | list[str]", label["label"])
        note = label.get("note", [])
        notes = tuple([note] if isinstance(note, str) else note)
        tip = label.get("tip", [])
        tips = tuple([tip] if isinstance(tip, str) else tip)
        cloze_test = label.get("cloze", [])
        cloze_tests = tuple([cloze_test] if isinstance(cloze_test, str) else cloze_test)
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
            tips,
            cloze_tests,
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
        json_label_slice["label"] = first(json_label["label"].values())
        return cls.grammatical_base_for(json_label_slice)
