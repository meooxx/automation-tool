"""Strip Windows Mark-of-the-Web so pythonnet can load Python.Runtime.dll.

Downloaded zips (GitHub Actions artifacts) attach Zone.Identifier; .NET then
refuses the bundled managed DLL. Local builds usually do not have that mark.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _is_packaged() -> bool:
    if getattr(sys, "frozen", False):
        return True
    main = sys.modules.get("__main__")
    return bool(main is not None and hasattr(main, "__compiled__"))


def clear_mark_of_the_web() -> None:
    if sys.platform != "win32" or not _is_packaged():
        return
    roots = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        roots.append(Path(meipass))
    roots.append(Path(sys.executable).resolve().parent)
    seen: set[Path] = set()
    for root in roots:
        try:
            root = root.resolve()
        except OSError:
            continue
        if root in seen or not root.is_dir():
            continue
        seen.add(root)
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            ads = f"{path}:Zone.Identifier"
            try:
                os.remove(ads)
            except FileNotFoundError:
                continue
            except OSError:
                continue
