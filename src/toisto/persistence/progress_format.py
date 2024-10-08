"""Progress format types."""

from typing import TypedDict


class RetentionDict(TypedDict, total=False):
    """Retention dict."""

    count: int
    skip_until: str
    start: str
    end: str


ProgressDict = dict[str, RetentionDict]
