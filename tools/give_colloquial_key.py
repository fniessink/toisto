"""Script to make colloquial its own key in label objects.

Invoke from the root folder:
$ python tools/give_colloquial_key.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for label in contents["labels"]:
        if isinstance(label["label"], str) and (label_string := label["label"]).endswith("*"):
            label["label"] = label_string.rstrip("*")
            label["colloquial"] = True
        elif isinstance(label["label"], dict):
            for key, value in label["label"].items():
                if isinstance(value, str) and value.endswith("*"):
                    label["label"][key] = value.rstrip("*")
                    if "colloquial" not in label:
                        label["colloquial"] = True
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
