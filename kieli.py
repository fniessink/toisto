import difflib
import json
import pathlib
import string


red = lambda text: f"\033[38;2;255;0;0m{text}\033[38;2;255;255;255m"
green = lambda text: f"\033[38;2;0;255;0m{text}\033[38;2;255;255;255m"


def get_edits_string(old: str, new: str) -> str:
    """Return a colored edit string."""
    result = ""
    codes = difflib.SequenceMatcher(a=old, b=new).get_opcodes()
    for operator, i1, i2, j1, j2 in codes:
        old_fragment = old[i1:i2]
        new_fragment = new[j1:j2]
        if operator == "equal" or (operator == "replace" and old_fragment.lower() == new_fragment.lower()):
            result += old_fragment
        elif operator == "delete":
            result += red(old_fragment)
        elif operator == "insert":
            result += green(new_fragment)
        elif operator == "replace":
            result += (red(old_fragment) + green(new_fragment))
    return result


def without_punctuation(text: str) -> str:
    """Remove text without punctuation."""
    return ''.join(char for char in text if char not in string.punctuation)


def match(text1: str, text2: str) -> bool:
    """Return whether the texts match."""
    return without_punctuation(text1.strip().lower()) == without_punctuation(text2.strip().lower())


def load_json(json_file_path: pathlib.Path, default=None):
    """Load the JSON from the file. Return default if file does not exist."""
    if json_file_path.exists():
        with json_file_path.open(encoding="utf-8") as fd:
            return json.load(fd)
    return default


def dump_json(json_file_path: pathlib.Path, contents) -> None:
    """Dump the JSON into the file."""
    with json_file_path.open("w", encoding="utf-8") as fd:
        json.dump(contents, fd)


def sorted_entries(entries, progress):
    """Sort the entries from low to high retention."""
    sortable_entries = [(progress.get(str(entry), 0), entry) for entry in entries]
    sortable_entries.sort()
    return [entry[1] for entry in sortable_entries]


PROGRESS_JSON = pathlib.Path(".kieli-progress.json")

entries = []
for deck in pathlib.Path(".").glob("deck-*.json"):
    for entry in load_json(deck):
        translations = tuple(entry.values())
        entries.extend([translations, tuple(reversed(translations))])

progress = load_json(PROGRESS_JSON, default={})

try:
    for entry in sorted_entries(entries, progress):
        print(entry[0])
        guess = input("> ")
        correct = match(guess, entry[1])
        key = str(entry)
        progress[key] = progress.setdefault(key, 0) + 1 if correct else 0
        diff = get_edits_string(guess, entry[1])
        print(("✅ Correct" if correct else f'❌ Incorrect. The correct answer is "{diff}"') + ".\n")
except (KeyboardInterrupt, EOFError):
    print()  # Make sure the shell prompt is displayed on a new line
finally:
    dump_json(PROGRESS_JSON, progress)

