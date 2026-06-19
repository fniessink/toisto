"""Validate that concept references resolve to defined concepts.

Checks that every concept relation target (antonym, answer, example, holonym, hypernym, involves) refers to a
defined concept, and that every label's concept is declared in some concepts block.
"""

import json
import sys
from pathlib import Path
from typing import Any

CONCEPTS_DIR = Path(__file__).parent.parent / "src" / "concepts"
RELATION_KEYS = ("antonym", "answer", "example", "holonym", "hypernym", "involves")


def as_str_list(value: Any) -> list[str]:  # noqa: ANN401
    """Return the value as a list of strings, wrapping non-list values."""
    return [str(item) for item in value] if isinstance(value, list) else [str(value)]


def validate_concept_references() -> int:
    """Validate concept references across all concept files. Return the number of errors."""
    concept_ids: set[str] = set()
    relation_refs: list[tuple[Path, str, str, str]] = []  # file, concept, relation, target
    label_refs: dict[str, Path] = {}  # concept -> first file referencing it from a label
    for path in sorted(CONCEPTS_DIR.glob("**/*.json")):
        data: Any = json.loads(path.read_text(encoding="utf-8"))
        for concept_id, concept in data.get("concepts", {}).items():
            concept_ids.add(str(concept_id))
            for relation in RELATION_KEYS:
                if isinstance(concept, dict) and relation in concept:
                    relation_refs += [
                        (path, str(concept_id), relation, target) for target in as_str_list(concept[relation])
                    ]
        for language_labels in data.get("labels", {}).values():
            for label in language_labels:
                for concept in as_str_list(label.get("concept")):
                    label_refs.setdefault(concept, path)
    errors = [
        f"{path}: concept '{concept_id}' has {relation} -> '{target}' which is not a defined concept"
        for path, concept_id, relation, target in relation_refs
        if target not in concept_ids
    ]
    errors += [
        f"{path}: label refers to concept '{concept}' which is not defined"
        for concept, path in label_refs.items()
        if concept not in concept_ids
    ]
    for error in sorted(errors):
        sys.stdout.write(error + "\n")
    sys.stdout.write(f"{len(errors)} concept reference error(s)\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(validate_concept_references())
