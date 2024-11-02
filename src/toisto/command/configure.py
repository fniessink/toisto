"""Configure command."""

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser

from rich.panel import Panel
from rich.syntax import Syntax

from toisto.persistence.config import CONFIG_FILENAME, write_config
from toisto.ui.text import console


def configure(argument_parser: ArgumentParser, config: ConfigParser, args: Namespace) -> None:
    """Configure the options."""
    for language in ("target_language", "source_language"):
        if language in args and getattr(args, language):
            ensure_section(config, "languages")
            config.set("languages", language.split("_")[0], getattr(args, language))
    if "progress_folder" in args:
        ensure_section(config, "progress")
        config.set("progress", "folder", str(args.progress_folder))
    if "progress_update" in args:
        ensure_section(config, "practice")
        config.set("practice", "progress_update", str(args.progress_update))
    if "mp3player" in args:
        ensure_section(config, "commands")
        config.set("commands", "mp3player", args.mp3player)
    if "extra" in args and args.extra:
        ensure_section(config, "files")
        for path in args.extra:
            config.set("files", str(path), "")
    write_config(argument_parser, config, CONFIG_FILENAME)
    show_config_file()


def ensure_section(config: ConfigParser, section: str) -> None:
    """Ensure that the config has the section."""
    if not config.has_section(section):
        config.add_section(section)


def show_config_file() -> None:
    """Show the config file."""
    with CONFIG_FILENAME.open("rt") as config_file:
        config_file_contents = Syntax(config_file.read(), "ini")
    console.print(Panel(config_file_contents, title=str(CONFIG_FILENAME)))
