"""Validate that every ```json code block in tracked markdown files parses as JSON."""

import json
import sys
from pathlib import Path
from subprocess import check_output  # nosec import_subprocess


def validate_markdown_file(md_file: Path) -> int:
    """Validate every JSON code block in the markdown file. Return the number of invalid blocks."""
    lines = md_file.read_text().splitlines()
    in_block = False
    block_start = 0
    buffer: list[str] = []
    invalid = 0
    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_block and stripped == "```json":
            in_block = True
            block_start = line_no + 1
            buffer = []
        elif in_block and stripped == "```":
            try:
                json.loads("\n".join(buffer))
            except json.JSONDecodeError as exc:
                sys.stdout.write(f"{md_file}:{block_start + exc.lineno - 1}: invalid JSON block: {exc.msg}\n")
                invalid += 1
            in_block = False
        elif in_block:
            buffer.append(line)
    if in_block:
        sys.stdout.write(f"{md_file}:{block_start - 1}: unterminated ```json code block\n")
        invalid += 1
    return invalid


def validate_markdown_files() -> int:
    """Validate every JSON block in tracked markdown files. Return the total number of invalid blocks."""
    list_files_command = "git ls-files -z -- '*.md'"
    output = check_output(list_files_command, shell=True).decode()  # nosec # noqa: S602
    md_filenames = [name for name in output.split("\0") if name]
    return sum(validate_markdown_file(Path(name)) for name in md_filenames)


if __name__ == "__main__":
    sys.exit(0 if validate_markdown_files() == 0 else 1)
