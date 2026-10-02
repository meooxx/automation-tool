from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "ui" / "pytool-ui"
UI_INDEX = UI_DIR / "dist" / "client" / "index.html"
SPEC = ROOT / "pytool.spec"


def python_executable() -> str:
    candidates = (
        ROOT / ".venv" / "bin" / "python",
        Path(sys.prefix) / "bin" / "python",
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def run(command: list[str], cwd: Path) -> None:
    print(f"> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    yarn = shutil.which("yarn")
    if yarn is None:
        raise RuntimeError("yarn is required to build the frontend before packaging.")

    run([yarn, "run", "build"], UI_DIR)
    if not UI_INDEX.is_file():
        raise RuntimeError(
            f"Frontend build did not create {UI_INDEX}. "
            "Packaging stopped before PyInstaller was run."
        )
    run(
        [
            python_executable(),
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            str(SPEC),
        ],
        ROOT,
    )


if __name__ == "__main__":
    main()
