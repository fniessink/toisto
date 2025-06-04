"""Script to refactor synonyms.

Invoke from the root folder:
$ python tools/refactor_synonyms.py
"""

import json
import pathlib


def count_synonyms(label: str | list | dict) -> int:
    """Count the number of synonyms."""
    if isinstance(label, str):
        return 1
    if isinstance(label, list):
        return len(label)
    return count_synonyms(next(iter(label.values())))


def slice_label(label: str | list | dict, index: int) -> str | dict:
    """Slice the label."""
    if isinstance(label, str):
        return label
    if isinstance(label, list):
        return label[index]
    return {key: slice_label(value, index) for key, value in label.items()}


for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    labels = []
    for label in contents["labels"]:
        for index in range(count_synonyms(label["label"])):
            sliced_label = slice_label(label["label"], index)
            labels.append(dict(concept=label["concept"], label=sliced_label, language=label["language"]))
    contents["labels"] = labels
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
