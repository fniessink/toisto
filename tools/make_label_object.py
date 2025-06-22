"""Script to add label keys to concepts in the concept files.

Invoke from the root folder:
$ python tools/add_concept_object.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for concept_id, concept in contents["concepts"].items():
        for language, label in concept["labels"].items():
            concept["labels"][language] = {"concept": concept_id, "label": label}
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
