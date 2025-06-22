"""Script to add the concepts key to concept files.

Invoke from the root folder:
$ python tools/add_concept_object.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/concepts").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    if "concepts" in contents:
        continue
    contents = {"concepts": contents}
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
