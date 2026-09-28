# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH)
UI_DIST = ROOT / "ui" / "pytool-ui" / "dist"

datas = []
binaries = []
hiddenimports = [
    "pytool",
    "pytool.app",
    "pytool.js_api",
    "pytool.read_source_data",
    "pytool.paths",
    "webview",
    "openpyxl",
    "dotenv",
]

if UI_DIST.is_dir():
    datas.append((str(UI_DIST), "ui/dist"))

webview_datas, webview_binaries, webview_hidden = collect_all("webview")
datas += webview_datas
binaries += webview_binaries
hiddenimports += webview_hidden

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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pytool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="pytool",
)
