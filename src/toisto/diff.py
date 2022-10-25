"""Create a colored diff."""

import difflib


def inserted(new_text: str) -> str:
    """Return the annotated text."""
    return f"[inserted]{new_text}[/inserted]"


def deleted(old_text: str) -> str:
    """Return the annotated text."""
    return f"[deleted]{old_text}[/deleted]"


def colored_diff(old_text: str, new_text: str) -> str:
    """Return a colored string showing the diffs between old and new text."""
    matcher = difflib.SequenceMatcher(a=old_text.lower(), b=new_text.lower())
    if matcher.ratio() < 0.6:
        return inserted(new_text)
    result = ""
    for operator, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        old_fragment, new_fragment = old_text[old_start:old_end], new_text[new_start:new_end]
        if operator == "delete":
            result += deleted(old_fragment)
        elif operator == "insert":
            result += inserted(new_fragment)
        elif operator == "replace":
            if len(old_fragment) == len(new_fragment) == 1:
                result += (deleted(old_fragment) + inserted(new_fragment))
            else:
                result += inserted(new_fragment)
        else:
            result += new_fragment
    return result
