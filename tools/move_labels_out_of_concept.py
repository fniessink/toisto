"""Script to move labels out of the concept object.

Invoke from the root folder:
$ python tools/move_labels_out_of_concept.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    labels = []
    for concept in contents["concepts"].values():
        labels.extend(concept.get("labels", []))
        if "labels" in concept:
            del concept["labels"]
    contents["labels"] = labels
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
