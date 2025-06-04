"""Script to add concept keys to labels in the concept files.

Invoke from the root folder:
$ python tools/add_concept_key_to_label.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    contents["labels"] = {}
    for concept_key, concept in contents["concepts"].items():
        for language, label in concept["labels"].items():
            if language not in contents["labels"]:
                contents["labels"][language] = []
            contents["labels"][language].append({"label": label, "concept": concept_key})
        del concept["labels"]
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
