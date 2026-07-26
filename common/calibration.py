"""Calibration module to persist and version-control per-project servo limits."""

import json
import subprocess
from datetime import datetime

from common.logger import Logger

logger = Logger("Calibration")


def _calibration_path(project_id: str) -> str:
    return f"projects/{project_id}/servo_calibration.json"


def load_calibration(project_id: str) -> dict:
    """Load the saved calibration data for a project. Returns {} if the file is
    missing or contains invalid JSON."""
    path = _calibration_path(project_id)
    try:
        with open(path, encoding="utf-8") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_calibration(project_id: str, data: dict) -> None:
    """Merge `data` into the project's calibration file and write it back,
    pretty-printed with sorted keys for stable diffs."""
    path = _calibration_path(project_id)
    calibration = load_calibration(project_id)
    calibration.update(data)
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(calibration, json_file, indent=2, sort_keys=True)
        json_file.write("\n")


def _run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True)


def git_commit_and_push(project_id: str) -> bool:
    """Commit the project's calibration file on a fresh, timestamped branch and
    push it - calibration changes are never committed directly on `main`. Always
    attempts to switch back to `main` afterward, even on failure. Any git error
    is logged as a warning and never raised (calibration must not crash the
    client). Returns True if a commit was actually pushed."""
    path = _calibration_path(project_id)
    branch = f"calibration/{project_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    committed = False
    try:
        _run_git("checkout", "-b", branch)
        _run_git("add", path)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
        if diff.returncode == 0:
            logger.info("No calibration changes to commit for", project_id)
        else:
            _run_git("commit", "-m", f"Calibrate servos for {project_id}")
            _run_git("push", "-u", "origin", branch)
            committed = True
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        logger.warning(f"Calibration git commit/push failed: {error}")
    finally:
        try:
            _run_git("checkout", "main")
        except (subprocess.CalledProcessError, FileNotFoundError) as error:
            logger.warning(f"Failed to switch back to main branch: {error}")
    return committed
