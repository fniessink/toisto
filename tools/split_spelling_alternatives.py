"""Script to split spelling alternatives into a list of strings.

Invoke from the root folder:
$ python tools/split_spelling_alternatives.py
"""

import json
import pathlib

Label = dict[str, "str | Label | list[str]"]


def split_spelling_alternatives(label: Label) -> None:
    """Split the spelling alternatives in a label dict into a list of strings."""
    for key, value in label.items():
        if isinstance(value, str) and "|" in value:
            label[key] = value.split("|")
        elif isinstance(value, dict):
            split_spelling_alternatives(value)


for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for label in contents["labels"]:
        if isinstance(label["label"], str) and "|" in (label_string := label["label"]):
            label["label"] = label_string.split("|")
        elif isinstance(label["label"], dict):
            split_spelling_alternatives(label["label"])
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
