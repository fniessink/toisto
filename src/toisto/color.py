"""Colored text."""

RED = "\033[38;2;255;0;0m"
GREEN = "\033[38;2;0;255;0m"
WHITE = "\033[38;2;255;255;255m"
GREY = "\033[38;2;160;160;160m"
PURPLE = "\033[38;2;190;140;190m"


def red(text: str) -> str:
    """Return the text in red."""
    return f"{RED}{text}{WHITE}"


def green(text: str) -> str:
    """Return the text in green."""
    return f"{GREEN}{text}{WHITE}"


def grey(text: str) -> str:
    """Return the text in grey."""
    return f"{GREY}{text}{WHITE}"


def purple(text: str) -> str:
    """Return the text in purple."""
    return f"{PURPLE}{text}{WHITE}"
