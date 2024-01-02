"""Script to add the topics key to topic files.

Invoke from the root folder:
$ python tools/add_topics_object.py
"""

import json
import pathlib

for json_filename in pathlib.Path("src/topics").glob("**/*.json"):
    with json_filename.open("r", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    if "name" not in contents:
        continue
    topic = dict(concepts=sorted(contents["concepts"]))
    if "topics" in contents:
        topic["topics"] = sorted(contents["topics"])  # Subtopics
    contents = dict(topics={contents["name"]: topic})
    with json_filename.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")
