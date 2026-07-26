"""Shared helper to read the project's version from the repo-root `.version` file."""

_VERSION_FILE = ".version"
_DEFAULT_VERSION = "0.0.0"


def get_version() -> str:
    """Return the project version string from `.version`, or a default if the
    file is missing (e.g. a stripped-down deployment)."""
    try:
        with open(_VERSION_FILE, encoding="utf-8") as version_file:
            version = version_file.read().strip()
    except FileNotFoundError:
        return _DEFAULT_VERSION
    return version or _DEFAULT_VERSION
