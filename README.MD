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

The application stores settings next to the executable:

```text
<application directory>\config\settings.json
```

Source development uses the repository `config\settings.json` as well. The
application directory must be writable by the current user; if an output
directory is not writable, the application reports an error and asks the user
to choose another directory.

### Quick start from a Windows source checkout

Open PowerShell in the repository root:

```powershell
cd C:\path\to\automation-tool
```

Create the virtual environment and install Python dependencies:

```powershell
# real installed python version
# py -3.11, py -3.14 ....
py -3.14 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install the frontend dependencies and build the SSG frontend. Use the
explicit `.cmd` commands on managed computers where PowerShell blocks
`npm.ps1` or `yarn.ps1`:

```powershell
corepack.cmd enable
corepack.cmd prepare yarn@stable --activate
cd ui\pytool-ui
yarn.cmd install
yarn.cmd build
cd ..\..
```

Run the source application:

```powershell
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python.exe -m pytool
```

The source application uses the frontend URL configured by `UI_URL` (or
`http://localhost:3000` by default when using the development environment).
For a production-style local run, build the frontend first and start the
Python application without the `development` argument.

### Build and run the Windows package

From the repository root, after installing the dependencies:

```powershell
.venv\Scripts\python.exe scripts\build_package.py
```

The complete one-folder package is created at:

```text
dist\pytool\
├── pytool.exe
└── _internal\
```

Run it with:

```powershell
dist\pytool\pytool.exe
```

Keep the complete `dist\pytool` directory together. Do not copy only
`pytool.exe`; the `_internal` directory contains the Python runtime, pywebview
dependencies, frontend files, and other required resources.

If the computer reports that `npm.ps1` or `yarn.ps1` cannot be loaded because
script execution is disabled, use `npm.cmd` or `yarn.cmd` explicitly. This is
a PowerShell policy issue, not a project error. WebView2 Runtime is normally
available on Windows 11 and many Windows 10 systems, but the target computer
must have it installed for the packaged desktop application.

## Windows release process

Pushes to `dev` create a test Artifact. Version tags create both the Windows
Artifact and a GitHub Release with the ZIP attached.

Create a release from the branch you want to publish:

```bash
git switch dev
git pull
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Tags must use the `vMAJOR.MINOR.PATCH` format, for example `v0.1.0`.
GitHub Actions then builds the Windows package and publishes:

```text
pytool-windows-x64-v0.1.0.zip
```

The release is created only after the Windows build and package verification
steps succeed. If the build fails, no release is published.
