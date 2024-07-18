#/bin/bash

ruff check --fix .; ruff format .; fixit fix .; python tools/format_json.py
