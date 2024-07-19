"""Format the JSON files in the repository."""

import json
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
    if check_only:
        sys.stdout.write(f"{json_file} incorrectly formatted\n")
        return 1
    json_file.write_text(formatted_content)
    sys.stdout.write(f"{json_file} formatted\n")
    return 0


def format_json_files(check_only: bool) -> int:  # noqa: FBT001
    """Format the JSON files."""
    list_files_command = "git ls-files -z -- *.json"
    json_filenames = check_output(list_files_command, shell=True).decode().split("\0")  # nosec # noqa: S602
    return max([format_json_file(Path(json_filename), check_only) for json_filename in json_filenames], default=0)


if __name__ == "__main__":
    check_only = len(sys.argv) > 1 and sys.argv[1] == "--check-only"
    sys.exit(format_json_files(check_only))
