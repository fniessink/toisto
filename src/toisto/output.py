"""Output for the user."""

from .color import grey
from .diff import colored_diff
from .model import Entry, Progress


def feedback(entry: Entry, correct: bool, guess: str, progress: Progress) -> str:
    """Create the user feedback."""
    if correct:
        progress_count = progress.get_progress(entry)
        multiple_times = grey(f", {progress_count} times in a row.") if progress_count > 1 else "."
        text = f"✅ Correct{multiple_times}"
    else:
        diff = colored_diff(guess, entry.get_answer())
        text = f'❌ Incorrect. The correct answer is "{diff}".'
    return text + "\n"
