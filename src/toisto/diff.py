"""Create a colored diff."""

import difflib

from .color import red, green


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
