"""Utitity functions."""

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def first(sequence: Iterable[T], where: Callable[[T], bool] = lambda _item: True) -> T:
    """Return the first item in the sequence."""
    return next(item for item in sequence if where(item))
