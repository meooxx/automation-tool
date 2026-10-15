"""Build frontend, then package the desktop app.

Default packager: PyInstaller (fast).
Optional: Nuitka via --nuitka (slower; macOS uses --mode=app).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "ui" / "pytool-ui"
UI_INDEX = UI_DIR / "dist" / "client" / "index.html"
UI_DIST = UI_DIR / "dist"
SPEC = ROOT / "pytool.spec"
ENTRY = ROOT / "packaging" / "entry.py"
WINDOWS_ICON = ROOT / "assets" / "pytool.ico"
DIST_DIR = ROOT / "dist"
OUT_NAME = "pytool"


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


def run(command: list[str], cwd: Path, env: dict | None = None) -> None:
    print(f"> {' '.join(command)}", flush=True)
    merged = os.environ.copy()
    if env:
        merged.update(env)
    subprocess.run(command, cwd=cwd, check=True, env=merged)


def ensure_packaging_imports(python: str, packager: str) -> None:
    required = ["webview", "openpyxl", "python_calamine", "dotenv"]
    if packager == "pyinstaller":
        required.append("PyInstaller")
    else:
        required.append("nuitka")
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
            + ("[nuitka]" if packager == "nuitka" else "")
        )


def build_frontend() -> None:
    yarn = shutil.which("yarn.cmd") or shutil.which("yarn")
    if yarn is None:
        raise RuntimeError("yarn is required to build the frontend before packaging.")
    run([yarn], UI_DIR)
    run([yarn, "run", "build"], UI_DIR)
    if not UI_INDEX.is_file():
        raise RuntimeError(
            f"Frontend build did not create {UI_INDEX}. Packaging stopped."
        )


def package_pyinstaller(python: str) -> Path:
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
    out = DIST_DIR / OUT_NAME
    print(f"Packaged application (PyInstaller): {out}", flush=True)
    return out


def nuitka_command(python: str) -> list[str]:
    # Do NOT --include-package=webview (conflicts with Nuitka pywebview plugin).
    # macOS: Cocoa/Foundation requires --mode=app.
    # Windows: --standalone + pythonnet/WebView2.
    if sys.platform == "darwin":
        mode_opts = ["--mode=app"]
    else:
        mode_opts = ["--standalone"]

    cmd = [
        python,
        "-m",
        "nuitka",
        *mode_opts,
        "--assume-yes-for-downloads",
        "--enable-plugin=pywebview",
        f"--output-dir={DIST_DIR}",
        f"--output-filename={OUT_NAME}",
        "--include-package=pytool",
        "--include-package=openpyxl",
        "--include-package=python_calamine",
        "--include-package-data=python_calamine",
        "--include-package=dotenv",
        "--include-package=dateutil",
        f"--include-data-dir={UI_DIST}={Path('ui') / 'dist'}",
        str(ENTRY),
    ]
    if sys.platform == "win32":
        cmd.extend(
            [
                "--mingw64",
                "--windows-console-mode=disable",
                "--include-package-data=clr_loader",
                "--include-package-data=pythonnet",
                "--include-module=clr",
            ]
        )
        if WINDOWS_ICON.is_file():
            cmd.append(f"--windows-icon-from-ico={WINDOWS_ICON}")
    return cmd


def normalize_nuitka_dist() -> Path:
    dest = DIST_DIR / OUT_NAME

    app_candidates = [
        DIST_DIR / f"{OUT_NAME}.app",
        DIST_DIR / "entry.app",
        *sorted(DIST_DIR.glob("*.app"), key=lambda p: p.stat().st_mtime, reverse=True),
    ]
    for app_bundle in app_candidates:
        if not app_bundle.is_dir():
            continue
        if dest.exists():
            shutil.rmtree(dest)
        if app_bundle.resolve() != dest.resolve():
            app_bundle.rename(dest)
        print(f"macOS app bundle: {dest}", flush=True)
        return dest

    candidates = [
        DIST_DIR / f"{OUT_NAME}.dist",
        DIST_DIR / "entry.dist",
        DIST_DIR / "__main__.dist",
        DIST_DIR / "pytool.dist",
    ]
    if not any(p.is_dir() for p in candidates):
        found = sorted(
            DIST_DIR.glob("*.dist"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if found:
            candidates.insert(0, found[0])

    src = next((p for p in candidates if p.is_dir()), None)
    if src is None:
        raise RuntimeError(
            f"Nuitka did not create a .dist/.app folder under {DIST_DIR}"
        )

    if dest.exists():
        shutil.rmtree(dest)
    if src.resolve() != dest.resolve():
        src.rename(dest)

    exe_name = f"{OUT_NAME}.exe" if sys.platform == "win32" else OUT_NAME
    exe = dest / exe_name
    if not exe.is_file():
        pattern = "*.exe" if sys.platform == "win32" else "*"
        alts = [
            p for p in dest.glob(pattern)
            if p.is_file() and os.access(p, os.X_OK)
        ]
        if not alts:
            raise RuntimeError(f"Packaged executable missing under {dest}")
        alts[0].rename(exe)
    print(f"Packaged application (Nuitka): {dest}", flush=True)
    return dest


def package_nuitka(python: str) -> Path:
    if not ENTRY.is_file():
        raise RuntimeError(f"Nuitka entry missing: {ENTRY}")
    run([python, "-m", "pip", "install", "-e", "."], ROOT)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    run(nuitka_command(python), ROOT, env={"PYTHONPATH": str(ROOT / "src")})
    return normalize_nuitka_dist()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build UI and package desktop app.")
    parser.add_argument(
        "--nuitka",
        action="store_true",
        help="Use Nuitka instead of PyInstaller (slower).",
    )
    parser.add_argument(
        "--packager",
        choices=("pyinstaller", "nuitka"),
        default=None,
        help="Packager to use (default: pyinstaller).",
    )
    args = parser.parse_args()
    packager = args.packager or ("nuitka" if args.nuitka else "pyinstaller")

    python = python_executable()
    ensure_packaging_imports(python, packager)
    build_frontend()

    if packager == "nuitka":
        package_nuitka(python)
    else:
        package_pyinstaller(python)


if __name__ == "__main__":
    main()
