"""Script to make meaning its own key in label objects.

Invoke from the root folder:
$ python tools/give_meaning_key.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for label in contents["labels"]:
        if isinstance(label["label"], str) and (label_string := label["label"]).startswith("("):
            label["label"] = label_string.lstrip("(").rstrip(")")
            label["meaning-only"] = True
        elif isinstance(label["label"], dict):
            for key, value in label["label"].items():
                if isinstance(value, str) and value.startswith("("):
                    label["label"][key] = value.lstrip("(").rstrip(")")
                    if "meaning-only" not in label:
                        label["meaning-only"] = True
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
