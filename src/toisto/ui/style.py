"""Text styles."""

from rich.theme import Theme

theme = Theme(
    {
        "deleted": "underline bright_red",
        "inserted": "bright_green",
        "language": "light_goldenrod2 bold",
        "progress": "light_sky_blue3",
        "quiz": "medium_purple1",
        "secondary": "grey69",
        "retention": "grey50",
    }
)
