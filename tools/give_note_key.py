"""Script to give notes their own key in label objects.

Invoke from the root folder:
$ python tools/give_note_key.py
"""

import json
import pathlib

HAS_NOTE = 2

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for label in contents["labels"]:
        if isinstance(label["label"], str) and (label_string := label["label"]).count(";") == HAS_NOTE:
            actual_label, tip, note = label_string.split(";")
            label["label"] = f"{actual_label};{tip}" if tip else actual_label
            label["note"] = note
        elif isinstance(label["label"], dict):
            for key, value in label["label"].items():
                if isinstance(value, str) and value.count(";") == HAS_NOTE:
                    actual_label, tip, note = value.split(";")
                    label["label"][key] = f"{actual_label};{tip}" if tip else actual_label
                    if "note" not in label:
                        label["note"] = note

    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
