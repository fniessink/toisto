"""Move concept files into per-initial-letter subfolders under a src/concepts/<category>/ directory."""

import shutil
import sys
from pathlib import Path
from subprocess import run  # nosec import_subprocess

CONCEPTS_DIR = Path(__file__).parent.parent / "src" / "concepts"


def tracked_files(directory: Path) -> set[Path]:
    """Return the resolved paths of the git-tracked files under the directory."""
    git_ls_files = ["git", "ls-files", "-z"]
    output = run(git_ls_files, capture_output=True, check=True, cwd=directory).stdout.decode()  # nosec # noqa: S603
    return {(directory / name).resolve() for name in output.split("\0") if name}


def move_file(json_file: Path, target_dir: Path, tracked: set[Path]) -> None:
    """Move the file into the target directory, using git mv when the file is tracked."""
    target_dir.mkdir(exist_ok=True)
    target = target_dir / json_file.name
    if json_file.resolve() in tracked:
        run(["git", "mv", str(json_file), str(target)], check=True)  # nosec # noqa: S603, S607
    else:
        shutil.move(str(json_file), str(target))


def organize(directory: Path) -> int:
    """Move each JSON file directly under the directory into a subfolder named after its first letter."""
    tracked = tracked_files(directory)
    moved = skipped = 0
    for json_file in sorted(directory.glob("*.json")):  # Files already in subfolders are not matched
        first_letter = json_file.name[0].lower()
        if not ("a" <= first_letter <= "z"):
            sys.stdout.write(f"Skipping {json_file.name}: does not start with a letter a-z\n")
            skipped += 1
            continue
        move_file(json_file, directory / first_letter, tracked)
        moved += 1
    sys.stdout.write(f"Moved {moved} file(s); skipped {skipped}.\n")
    return 0


if __name__ == "__main__":
    try:
        _, category = sys.argv
    except ValueError:
        sys.exit("Usage: organize_concepts.py <category>  (e.g. nouns, verbs)")
    category_dir = CONCEPTS_DIR / category
    if not category_dir.is_dir():
        sys.exit(f"No such concept category directory: {category_dir}")
    sys.exit(organize(category_dir))
