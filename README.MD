Automation Tool

buit for workflow automation at Georgian College

## Build the packaged application

Run the packaging command from the repository root:

```bash
python scripts/build_package.py
```

The command builds the frontend first, verifies that
`ui/pytool-ui/dist/client/index.html`
exists, and only then runs PyInstaller. If the frontend artifact is missing,
packaging stops instead of producing an unusable application.

The packaged application serves the frontend through a temporary HTTP server
bound to `127.0.0.1` and opens that URL in pywebview. It does not load the
frontend through `file://`. The server uses an ephemeral port and stops when
the application window closes.

For Windows builds, place the application icon at
`assets/pytool.ico` before packaging. The icon is included in the `.exe` when
that file exists. The Windows icon is optional on other platforms.

## Windows requirements

### Running the packaged application

End users do not need Python, Node.js, npm, Yarn, pip, or the frontend
dependencies. Distribute the complete PyInstaller folder, including
`pytool.exe` and `_internal`.

The Windows build uses the Edge WebView2 runtime through pywebview. WebView2
is normally included with Windows 11 and is also preinstalled on many current
Windows 10 systems, but its presence is not guaranteed on every Windows
installation (for example, older, enterprise-managed, or stripped-down
systems). The installer or deployment process should check for WebView2 and
install the Evergreen WebView2 Runtime when it is missing. The application
should not assume that copying `pytool.exe` alone is sufficient.

### Building from source on Windows

Install:

- Windows 10 or Windows 11;
- Python 3.11 or the version used by the project;
- Node.js LTS;
- Corepack/Yarn;
- WebView2 Runtime for testing the desktop application.

Then run in PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

corepack enable
corepack prepare yarn@stable --activate

cd ui\pytool-ui
yarn install # or yarn.cmd
cd ..\..

.venv\Scripts\python.exe scripts\build_package.py
```

The packaged application is created at:

```text
dist\pytool\pytool.exe
```

Node.js, Yarn, and the Python build dependencies are only required to build
the application; they are not required on the end user's computer.
