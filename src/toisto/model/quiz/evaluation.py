"""Quiz answer evaluation."""

from enum import Enum


class Evaluation(Enum):
    """Quiz answer evaluation."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    SKIPPED = "skipped"
    TRY_AGAIN = "try again"
