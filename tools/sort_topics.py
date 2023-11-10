"""Script to sort the list of concepts in JSON topic files.

Invoke from the root folder:
$ python tools/sort_topics.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/topics").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    contents["concepts"] = sorted(contents["concepts"])
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
