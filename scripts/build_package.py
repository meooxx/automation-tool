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
        ROOT / ".venv" / "Scripts" / "python.exe",
        Path(sys.prefix) / "bin" / "python",
        Path(sys.prefix) / "Scripts" / "python.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def run(command: list[str], cwd: Path) -> None:
    print(f"> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def ensure_packaging_imports(python: str) -> None:
    """Fail early if the packaging env is missing modules the frozen app needs."""
    required = ("webview", "openpyxl", "python_calamine", "dotenv")
    script = (
        "import importlib.util\n"
        f"missing=[m for m in {required!r} if importlib.util.find_spec(m) is None]\n"
        "raise SystemExit(', '.join(missing) if missing else 0)\n"
    )
    result = subprocess.run(
        [python, "-c", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        missing = (result.stdout or result.stderr or "").strip() or "unknown"
        raise RuntimeError(
            "Packaging environment is missing required modules: "
            f"{missing}. Install with: pip install -r requirements.txt"
        )


def main() -> None:
    python = python_executable()
    ensure_packaging_imports(python)
    yarn = shutil.which("yarn.cmd") or shutil.which("yarn")
    if yarn is None:
        raise RuntimeError("yarn is required to build the frontend before packaging.")
    run([yarn], UI_DIR)
    run([yarn, "run", "build"], UI_DIR)
    if not UI_INDEX.is_file():
        raise RuntimeError(
            f"Frontend build did not create {UI_INDEX}. "
            "Packaging stopped before PyInstaller was run."
        )
    run(
        [
            python,
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
