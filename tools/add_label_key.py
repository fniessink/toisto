"""Script to add label keys to concepts in the concept files.

Invoke from the root folder:
$ python tools/add_concept_object.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    for concept in contents["concepts"].values():
        concept["labels"] = {}
        for language in ["en", "fi", "nl"]:
            if language in concept:
                concept["labels"][language] = concept[language]
                del concept[language]
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
