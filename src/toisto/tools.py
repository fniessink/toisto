"""Zip function that cycles shorter lists."""

from collections.abc import Iterator
from itertools import cycle
from typing import TypeVar

T = TypeVar("T")


def zip_and_cycle(*lists: list[T]) -> Iterator[tuple[T]]:
    """Zip the lists, while cycling lists that are shorter than the longest list."""
    max_len = max(len(lst) for lst in lists) if lists else 0
    cycled_lists = [cycle(lst) if len(lst) < max_len else lst for lst in lists]
    yield from zip(*cycled_lists, strict=False)
