"""Self commands."""

from argparse import ArgumentParser
from collections.abc import Callable
from subprocess import check_output  # nosec import_subprocess
from typing import NoReturn

from toisto.metadata import NAME, installation_tool, latest_version
from toisto.ui.text import version_message


class Self:
    """Self commands."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.tool = installation_tool()
        self.program_name = NAME.lower()

    def uninstall(self) -> NoReturn:
        """Uninstall the program and exit."""
        command = ["pip", "uninstall", "--yes"] if self.tool == "pip" else [*self.tool.split(" "), "uninstall"]
        self._run_command([*command, self.program_name])

    def upgrade(self) -> NoReturn:
        """Upgrade the program and exit."""
        command = ["pip", "install", "--upgrade"] if self.tool == "pip" else [*self.tool.split(" "), "upgrade"]
        self._run_command([*command, self.program_name])

    def version(self, console_print: Callable[..., None]) -> NoReturn:
        """Print the program's version and exit."""
        console_print(version_message(latest_version()))
        self.argument_parser.exit()

    def _run_command(self, command: list[str]) -> NoReturn:
        """Run the command and exit."""
        check_output(command)  # noqa: S603 # nosec
        self.argument_parser.exit()
