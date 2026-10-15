# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH)
UI_DIST = ROOT / "ui" / "pytool-ui" / "dist"
WINDOWS_ICON = ROOT / "assets" / "pytool.ico"

datas = []
binaries = []
hiddenimports = [
    "pytool",
    "pytool.app",
    "pytool.js_api",
    "pytool.read_source_data",
    "pytool.paths",
    "pytool.win_motw",
    "webview",
    "webview.platforms",
    "webview.platforms.edgechromium",
    "webview.platforms.winforms",
    "webview.guilib",
    "openpyxl",
    "python_calamine",
    "dotenv",
    "clr",
    "clr_loader",
    "pythonnet",
]

if UI_DIST.is_dir():
    datas.append((str(UI_DIST), "ui/dist"))

for package in ("webview", "python_calamine", "pythonnet", "clr_loader"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    except Exception:
        continue
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

# UPX breaks pythonnet DLLs on Windows.
use_upx = sys.platform != "win32"

a = Analysis(
    [str(ROOT / "src" / "pytool" / "__main__.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe_options = dict(
    name="pytool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=use_upx,
    console=False,
    disable_windowed_traceback=False,
)
if sys.platform == "win32" and WINDOWS_ICON.is_file():
    exe_options["icon"] = str(WINDOWS_ICON)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    **exe_options,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=use_upx,
    name="pytool",
)
