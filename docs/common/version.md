# Version

The `version` module reads the project's version number from a single repo-root source of truth: the `.version` file.

## What it does

`.version` is a plain text file at the repository root (e.g. containing `0.0.5`) that is bumped by hand whenever a release is cut. Both [server.py](../../server.py) and [client.py](../../client.py) read it through `get_version()` so the version is only ever defined in one place.

## Main function

- `get_version() -> str`: returns the version string from `.version` (whitespace-stripped), or `"0.0.0"` if the file is missing or empty (e.g. a stripped-down deployment).

## Example

```python
from common.version import get_version

print(get_version())  # "0.0.5"
```

## Notes

- The server prints the version in its startup banner (`_print_banner()` in `server.py`):

  ```
  ┌────────────────────────────────┐
  │ Animatronics Controller V0.0.5 │
  │ by Jordi Orriols                │
  └────────────────────────────────┘
  ```

- The client sends its own version in the `capabilities`/`servos` handshake payload (`{"version": get_version(), ...}`) when it connects (see `client.py`'s `main()` and [websocket.md](websocket.md)). The server logs a success message (`Client connected - running version <version>`) when it receives it, in `handler()`.
- `get_version()` uses a path relative to the current working directory, consistent with how the rest of the codebase resolves project-relative paths (e.g. `common/calibration.py`, `common/project.py`'s `load_animation`) - always run `server.py`/`client.py` from the repository root.
