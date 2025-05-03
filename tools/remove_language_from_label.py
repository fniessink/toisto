"""Script to remove language from label objects and make it a key under the labels key.

Invoke from the root folder:
$ python tools/remove_language_from_label.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    labels = contents["labels"]
    contents["labels"] = {}
    for label in labels:
        language = label["language"]
        del label["language"]
        if language in contents["labels"]:
            contents["labels"][language].append(label)
        else:
            contents["labels"][language] = [label]
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
