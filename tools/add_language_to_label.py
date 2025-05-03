"""Script to add language to label objects in the concept files.

Invoke from the root folder:
$ python tools/add_language_to_label.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for concept in contents["concepts"].values():
        labels = concept["labels"]
        concept["labels"] = []
        for language, label in labels.items():
            new_label = {"label": label} if isinstance(label, str) else label
            new_label["language"] = language
            concept["labels"].append(new_label)
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
