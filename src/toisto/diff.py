"""Create a colored diff."""

import difflib


RED = "\033[38;2;255;0;0m"
GREEN = "\033[38;2;0;255;0m"
WHITE = "\033[38;2;255;255;255m"


def red(text: str) -> str:
    """Return the text in red."""
    return f"{RED}{text}{WHITE}"

def green(text: str) -> str:
    """Return the text in green."""
    return f"{GREEN}{text}{WHITE}"


def colored_diff(old_text: str, new_text: str) -> str:
    """Return a colored string showing the diffs between old and new text."""
    matcher = difflib.SequenceMatcher(a=old_text.lower(), b=new_text.lower())
    if matcher.ratio() < 0.6:
        return green(new_text)
    result = ""
    for operator, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        old_fragment, new_fragment = old_text[old_start:old_end], new_text[new_start:new_end]
        if operator == "delete":
            result += red(old_fragment)
        elif operator == "insert":
            result += green(new_fragment)
        elif operator == "replace":
            if len(old_fragment) == len(new_fragment) == 1:
                result += (red(old_fragment) + green(new_fragment))
            else:
                result += green(new_fragment)
        else:
            result += new_fragment
    return result