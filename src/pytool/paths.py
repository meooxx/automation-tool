"""Resolve files the same way in source and in a frozen Windows exe."""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    # PyInstaller sets sys.frozen; Nuitka injects __compiled__ into modules.
    if bool(getattr(sys, "frozen", False)):
        return True
    return "__compiled__" in globals()


def app_root() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_dir() -> Path:
    if is_frozen():
        # PyInstaller onefile uses _MEIPASS; Nuitka standalone uses exe dir.
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return app_root()


def ui_index() -> Path:
    if is_frozen():
        return resource_dir() / "ui" / "dist" / "client" / "index.html"
    return app_root() / "ui" / "pytool-ui" / "dist" / "client" / "index.html"
