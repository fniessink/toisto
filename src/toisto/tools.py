"""Utitity functions."""

from collections.abc import Callable, Iterable
from typing import Generic, TypeVar

T = TypeVar("T")


def first(sequence: Iterable[T], where: Callable[[T], bool] = lambda _item: True) -> T:
    """Return the first item in the sequence."""
    return next(item for item in sequence if where(item))


Key = TypeVar("Key")
Value = TypeVar("Value")


class Registry(Generic[Key, Value]):
    """Registry for looking up values by their key."""

    def __init__(self) -> None:
        self.__items: dict[Key, Value] = {}

    def add_item(self, key: Key, value: Value) -> None:
        """Register the item."""
        self.__items[key] = value

    def get_values(self, *keys: Key) -> tuple[Value, ...]:
        """Return the values with the given keys."""
        return tuple(self.__items[key] for key in keys)

    def get_all_values(self) -> tuple[Value, ...]:
        """Return all values."""
        return tuple(self.__items.values())

    def clear(self) -> None:
        """Clear the registry."""
        self.__items.clear()
