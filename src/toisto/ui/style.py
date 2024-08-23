"""Text styles."""

from rich.theme import Theme

theme = Theme(
    {
        "deleted": "underline bright_red",
        "inserted": "bright_green",
        "language": "light_goldenrod2 bold",
        "quiz": "medium_purple1",
        "secondary": "grey69",
    }
)
