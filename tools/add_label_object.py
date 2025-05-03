"""Script to move the labels to a separate object in the concept files.

Invoke from the root folder:
$ python tools/add_label_object.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    if "labels" in contents:
        continue
    contents["labels"] = []
    for concept_key, concept in contents["concepts"].items():
        labels = concept["labels"]
        labels["concept"] = concept_key
        contents["labels"].append(labels)
        del concept["labels"]
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
