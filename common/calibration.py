"""Calibration module to persist and version-control per-project servo limits.

Multiple physical units of the same project (e.g. two skeletons 3D-printed at
different times) can end up with different servo limits due to print tolerances
and servo wear. To support that, each physical unit gets its own calibration file
(projects/<project_id>/servo_calibration/<calibration_id>.json) instead of every
unit sharing and editing one file - this keeps units from ever needing to merge
their calibration changes against each other in git. Which file a given unit
uses is recorded in its own local .env file (CALIBRATION_ID).
"""

import json
import os
import subprocess
import uuid
from datetime import datetime

from dotenv import find_dotenv, load_dotenv, set_key

from common.logger import Logger

logger = Logger("Calibration")

# Loaded here (rather than relying solely on Project.__init__) because project
# config modules read CALIBRATION_ID while building their servo list at import
# time, which happens before Project.__init__ ever runs.
load_dotenv()

CALIBRATION_ID_ENV_KEY = "CALIBRATION_ID"


def _calibration_dir(project_id: str) -> str:
    return f"projects/{project_id}/servo_calibration"


def _calibration_file_path(project_id: str, calibration_id: str) -> str:
    return os.path.join(_calibration_dir(project_id), f"{calibration_id}.json")


def _generate_calibration_id() -> str:
    """Generate a UUIDv4 identifying one physical unit's calibration file."""
    return str(uuid.uuid4())


def get_or_create_calibration_id() -> str:
    """Return this physical unit's calibration id from .env, generating and
    persisting a new UUIDv4 the first time this unit is ever calibrated."""
    calibration_id = os.getenv(CALIBRATION_ID_ENV_KEY)
    if calibration_id:
        return calibration_id

    calibration_id = _generate_calibration_id()
    dotenv_path = find_dotenv() or ".env"
    set_key(dotenv_path, CALIBRATION_ID_ENV_KEY, calibration_id)
    os.environ[CALIBRATION_ID_ENV_KEY] = calibration_id
    logger.info(f"Generated new calibration id for this unit: {calibration_id}")
    return calibration_id


def load_calibration(project_id: str) -> dict:
    """Load this physical unit's saved calibration data, from the file selected
    by the CALIBRATION_ID in .env. Returns {} if there's no id yet, or this
    unit's calibration file is missing/invalid."""
    calibration_id = os.getenv(CALIBRATION_ID_ENV_KEY)
    if not calibration_id:
        return {}
    path = _calibration_file_path(project_id, calibration_id)
    try:
        with open(path, encoding="utf-8") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def has_calibration(project_id: str) -> bool:
    """Whether this physical unit already has saved calibration data for this
    project. Used to gate movement features (play/generative/xbox/evaluate)
    until the unit has actually been calibrated."""
    return bool(load_calibration(project_id))


def save_calibration(project_id: str, data: dict) -> None:
    """Merge `data` into this physical unit's own calibration file (generating
    and persisting a CALIBRATION_ID on first save) and write it back,
    pretty-printed with sorted keys for stable diffs."""
    calibration_id = get_or_create_calibration_id()
    path = _calibration_file_path(project_id, calibration_id)
    os.makedirs(_calibration_dir(project_id), exist_ok=True)

    calibration = {}
    try:
        with open(path, encoding="utf-8") as json_file:
            calibration = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        calibration = {}

    calibration.update(data)
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(calibration, json_file, indent=2, sort_keys=True)
        json_file.write("\n")


def _run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True)


def git_commit_and_push(project_id: str) -> bool:
    """Commit this physical unit's own calibration file on a fresh, timestamped
    branch and push it - calibration changes are never committed directly on
    `main`. Always attempts to switch back to `main` afterward, even on
    failure. Any git error is logged as a warning and never raised (calibration
    must not crash the client). Returns True if a commit was actually pushed."""
    calibration_id = os.getenv(CALIBRATION_ID_ENV_KEY)
    if not calibration_id:
        logger.warning(f"No calibration id set; nothing to commit for {project_id}")
        return False

    path = _calibration_file_path(project_id, calibration_id)
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
