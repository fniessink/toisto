"""Unit tests."""

import logging
import pathlib
import sys

logging.getLogger().setLevel(logging.ERROR)

src_folder = pathlib.Path(__file__).parent / ".." / "src"
sys.path.insert(0, str(src_folder.resolve()))
