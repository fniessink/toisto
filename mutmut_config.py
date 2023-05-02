"""Mutmut configuration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mutmut import Context
else:
    Context = object


def init() -> None:
    """Initialize the mutmut configuration."""


def pre_mutation(context: Context) -> None:
    """Skip certain mutations."""
    current_line = context.current_source_line.strip()
    for text in (
        "@dataclass(frozen=True)",
        "NewType(",
        "TypeVar(",
        " = tuple[",
        " = dict[",
        " = list[",
        ": Final =",
        " = Literal[",
    ):
        if text in current_line:
            context.skip = True
            return
