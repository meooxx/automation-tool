# Automation Tool

Desktop app for processing
Excel export, pick Lead Source columns, and generate a **Channel Performance**
workbook.
**Stack:** Python (`pywebview` + openpyxl / python-calamine) · React/Vite UI ·
packaged with **PyInstaller** by default (optional **Nuitka**).

---

## What it does

1. Open a Master Report (`.xlsx`).
2. Scan **Lead Source - Most Recent**; you choose which values become report columns.
3. Unselected values → **Other**; empty → **Blank**.
4. Apply mailable filters (when columns exist) and count **Total mailable** for the
   selected month (Joined in that month).
5. Write Channel Performance Excel to the chosen output folder.

Settings live in `config/settings.json` (field mapping, mailable conditions, IC
postal prefixes, selected Lead Sources, report directory).

---

## Requirements

| | Development | End user (packaged app) |
|--|-------------|-------------------------|
| OS | macOS or Windows 10/11 | Same |
| Python | 3.11+ | Not needed |
| Node.js + Yarn | Yes (UI) | Not needed |
| WebView | macOS WKWebView / Windows **WebView2** | Same (Windows needs WebView2 Runtime) |

---

## Development

### 1. Clone and Python env

**macOS**

```bash
cd automation-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Windows (PowerShell)**

```powershell
cd automation-tool
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
```

If PowerShell blocks `yarn.ps1` / `npm.ps1`, use `yarn.cmd` / `npm.cmd`.

### 2. Frontend

**macOS**

```bash
corepack enable
corepack prepare yarn@stable --activate
cd ui/pytool-ui
yarn install
yarn build          # production-style UI into dist/
# or for hot reload:
yarn dev            # typically http://localhost:3000
```

**Windows**

```powershell
corepack.cmd enable
corepack.cmd prepare yarn@stable --activate
cd ui\pytool-ui
yarn.cmd install
yarn.cmd build
# or: yarn.cmd dev
```

### 3. Run the app from source

**Development UI (Vite):**

```bash
# terminal 1 — UI
cd ui/pytool-ui && yarn dev

# terminal 2 — Python (macOS, from repo root)
export PYTHONPATH="$PWD/src"
.venv/bin/python -m pytool development
```

```powershell
# Windows — terminal 2 (repo root)
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python.exe -m pytool development
```

`development` loads `UI_URL` (default `http://localhost:3000`).

**Production-style local run** (built UI served by the app):

```bash
# after yarn build
export PYTHONPATH="$PWD/src"
.venv/bin/python -m pytool
```

```powershell
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python.exe -m pytool
```

---

## Packaging

Default packager is **PyInstaller** (faster). **Nuitka** remains available via a flag.

### PyInstaller (default)

```bash
# macOS
.venv/bin/python scripts/build_package.py
# same as:
.venv/bin/python scripts/build_package.py --packager pyinstaller
```

```powershell
# Windows
.venv\Scripts\python.exe scripts\build_package.py
```

Output:

```text
dist/pytool/
├── pytool          # or pytool.exe on Windows
└── _internal/      # runtime, UI, DLLs — keep together
```

### Nuitka (optional, slower)

```bash
pip install -e ".[nuitka]"   # or: pip install 'nuitka>=2.5' ordered-set zstandard
.venv/bin/python scripts/build_package.py --nuitka
```

| Platform | Nuitka mode | Notes |
|----------|-------------|--------|
| Windows | `--standalone` | MinGW downloaded by Nuitka; needs WebView2 at runtime |
| macOS | `--mode=app` | Required for Cocoa / `Foundation` |

Entry script: `packaging/entry.py`.

Optional Windows icon: `assets/pytool.ico`.

**Distribute the whole `dist/pytool` folder**, not only the executable.

### Run packaged app

**Windows**

```powershell
dist\pytool\pytool.exe
```

Needs **WebView2 Runtime** (usually present on Win11 / many Win10 PCs).

If the zip was **downloaded** (e.g. GitHub Actions) and startup fails on
`Python.Runtime.dll` / pythonnet, unblock then retry:

```powershell
Get-ChildItem -Recurse .\pytool | Unblock-File
```

(The app also clears Mark-of-the-Web on startup.)

**macOS**

```bash
dist/pytool/pytool
# or open the app if you wrap it later
```

First launch of an unsigned download may need **System Settings → Privacy & Security**.

---

## GitHub Actions (Windows release)

- Push to `dev` → Windows artifact zip  
- Tag `vMAJOR.MINOR.PATCH` → artifact + GitHub Release  

```bash
git switch dev
git pull
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Artifact name example: `pytool-windows-x64-v0.1.0.zip`.

CI builds on `windows-latest`. Package on a Mac with the same
`scripts/build_package.py` when you need a macOS build.

---

## Project layout (short)

```text
src/pytool/          Python app (webview, Excel read/write, JS API)
ui/pytool-ui/        React UI
config/              settings.json
scripts/build_package.py
pytool.spec          PyInstaller spec
data/                sample Master files (local testing)
```

---

## Notes

- Master reads use **python-calamine** (fast); report writes use **openpyxl**.
- Config and logs are written under the app directory; that folder must be writable.
- Prefer shipping the full `dist/pytool` directory to end users.
