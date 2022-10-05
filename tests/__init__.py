"""Unit tests."""

import pathlib
import sys


src_folder = pathlib.Path(__file__).parent / ".." / "src"
sys.path.insert(0, str(src_folder.resolve()))
