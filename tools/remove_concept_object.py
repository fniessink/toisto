"""Script to remove the concepts key from concept files.

Invoke from the root folder:
$ python tools/remove_concept_object.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    if "concepts" not in contents:
        continue
    contents = contents["concepts"]
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
