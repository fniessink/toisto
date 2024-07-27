"""Utitity functions."""

from collections.abc import Callable, Iterable
from itertools import chain
from typing import Generic, TypeVar

T = TypeVar("T")


def first(sequence: Iterable[T], where: Callable[[T], bool] = lambda _item: True) -> T:
    """Return the first item in the sequence."""
    return next(item for item in sequence if where(item))


Key = TypeVar("Key")
Value = TypeVar("Value")


class Registry(Generic[Key, Value]):
    """Registry for looking up values by their key."""

    def __init__(self, key_transformer: Callable[[Key], Key] = lambda key: key) -> None:
        self.__items: dict[Key, list[Value]] = {}
        self.__transform = key_transformer
        self.items = self.__items

    def add_item(self, key: Key, value: Value) -> None:
        """Register the item."""
        self.__items.setdefault(self.__transform(key), []).append(value)

    def get_values(self, *keys: Key) -> tuple[Value, ...]:
        """Return the values with the given keys."""
        return tuple(value for key in keys for value in self.__items[self.__transform(key)])

    def get_all_values(self) -> tuple[Value, ...]:
        """Return all values."""
        return tuple(chain(*self.__items.values()))

    def clear(self) -> None:
        """Clear the registry."""
        self.__items.clear()
