"""Format the JSON files in the repository."""

import json
import logging
import sys
from pathlib import Path
from subprocess import check_output  # nosec


def format_json_file(json_file: Path, check_only: bool) -> int:  # noqa: FBT001
    """Format a JSON file."""
    if json_file.is_dir():
        return 0
    unformatted_content = json_file.read_text()
    formatted_content = json.dumps(json.loads(unformatted_content), ensure_ascii=False, indent=4)
    if unformatted_content == formatted_content:
        return 0
    logging.info("%s incorrectly formatted" if check_only else "%s formatted", json_file)
    if check_only:
        return 1
    json_file.write_text(formatted_content)
    return 0


def format_json_files(check_only: bool) -> int:  # noqa: FBT001
    """Format the JSON files."""
    exit_code = 0
    json_files = check_output("git ls-files -z 'src/concepts/**/*.json'", shell=True).decode()  # nosec # noqa: S602, S607
    for json_filename in json_files.split("\0"):
        json_file = Path(json_filename)
        exit_code = max(exit_code, format_json_file(json_file, check_only))
    return exit_code


if __name__ == "__main__":
    check_only = len(sys.argv) > 1 and sys.argv[1] == "--check-only"
    sys.exit(format_json_files(check_only))
