"""Create a colored diff."""

from difflib import SequenceMatcher

from .dictionary import linkified


def show_whitespace(text: str) -> str:
    """Make whitespace visible so it can be colored."""
    return "_" * len(text) if all(char.isspace() for char in text) else text


def inserted(new_text: str) -> str:
    """Return the annotated text."""
    return f"[inserted]{new_text}[/inserted]"


def deleted(old_text: str) -> str:
    """Return the annotated text."""
    return f"[deleted]{show_whitespace(old_text)}[/deleted]"


def colored_diff(old_text: str, new_text: str, min_ratio_for_diff: float = 0.6) -> str:
    """Return a colored string showing the diffs between old and new text."""
    matcher = SequenceMatcher(a=old_text.lower(), b=new_text.lower())
    if matcher.ratio() < min_ratio_for_diff:
        return inserted(linkified(new_text))
    result = ""
    for operator, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        old_fragment, new_fragment = (old_text[old_start:old_end], new_text[new_start:new_end])
        if operator == "delete":
            result += deleted(old_fragment)
        elif operator == "insert":
            result += inserted(new_fragment)
        elif operator == "replace":
            if len(old_fragment) == len(new_fragment) == 1:
                result += f"{deleted(old_fragment)}{inserted(new_fragment)}"
            else:
                result += inserted(new_fragment)
        else:
            result += new_fragment
    return result
