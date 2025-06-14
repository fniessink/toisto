"""Script to give tips their own key in label objects.

Invoke from the root folder:
$ python tools/give_tip_key.py
"""

import json
import pathlib

HAS_TIP = 1

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for label in contents["labels"]:
        if isinstance(label["label"], str) and (label_string := label["label"]).count(";") == HAS_TIP:
            label["label"], label["tip"] = label_string.split(";")
        elif isinstance(label["label"], dict):
            for key, value in label["label"].items():
                if isinstance(value, str) and value.count(";") == HAS_TIP:
                    actual_label, tip = value.split(";")
                    label["label"][key] = actual_label
                    if "tip" not in label:
                        label["tip"] = tip

    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
