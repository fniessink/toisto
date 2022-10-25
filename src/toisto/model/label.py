"""Label type."""

from typing import NewType


Label = NewType("Label", str)
Labels = list[Label]
