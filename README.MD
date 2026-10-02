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
