"""Zip function that cycles shorter lists."""

from itertools import cycle


def zip_and_cycle(*lists):
    """Zip the lists, while cycling lists that are shorter than the longest list."""
    max_len = max(len(l) for l in lists) if lists else 0
    lists = [cycle(l) if len(l) < max_len else l for l in lists]
    return zip(*lists)
