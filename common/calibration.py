"""Calibration module to persist and version-control per-project servo limits.

Multiple physical units of the same project (e.g. two skeletons 3D-printed at
different times) can end up with different servo limits due to print tolerances
and servo wear. To support that, calibration data is stored per physical unit:
each project's servo_calibration.json holds one profile per unit, keyed by a
unique hash. Which profile a given unit uses is recorded in its own local .env
file (CALIBRATION_HASH), so a single servo_calibration.json (checked into git)
can serve every physical unit of a project without them overwriting each other.
"""

import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime

from dotenv import find_dotenv, load_dotenv, set_key

from common.logger import Logger

logger = Logger("Calibration")

# Loaded here (rather than relying solely on Project.__init__) because project
# config modules read CALIBRATION_HASH while building their servo list at import
# time, which happens before Project.__init__ ever runs.
load_dotenv()

CALIBRATION_HASH_ENV_KEY = "CALIBRATION_HASH"


def _calibration_path(project_id: str) -> str:
    return f"projects/{project_id}/servo_calibration.json"


def _generate_calibration_hash() -> str:
    """Generate a short hash identifying one physical unit's calibration profile."""
    seed = f"{uuid.uuid4()}-{datetime.now().isoformat()}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def get_or_create_calibration_hash() -> str:
    """Return this physical unit's calibration hash from .env, generating and
    persisting a new one the first time this unit is ever calibrated."""
    calibration_hash = os.getenv(CALIBRATION_HASH_ENV_KEY)
    if calibration_hash:
        return calibration_hash

    calibration_hash = _generate_calibration_hash()
    dotenv_path = find_dotenv() or ".env"
    set_key(dotenv_path, CALIBRATION_HASH_ENV_KEY, calibration_hash)
    os.environ[CALIBRATION_HASH_ENV_KEY] = calibration_hash
    logger.info(f"Generated new calibration hash for this unit: {calibration_hash}")
    return calibration_hash


def _load_profiles(project_id: str) -> dict:
    """Load every physical unit's calibration profile for a project, keyed by
    hash. Returns {} if the file is missing or contains invalid JSON."""
    path = _calibration_path(project_id)
    try:
        with open(path, encoding="utf-8") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_calibration(project_id: str) -> dict:
    """Load this physical unit's saved calibration data, selected by the
    CALIBRATION_HASH in .env. Returns {} if there's no hash yet, the file is
    missing/invalid, or this hash has no saved profile yet."""
    calibration_hash = os.getenv(CALIBRATION_HASH_ENV_KEY)
    if not calibration_hash:
        return {}
    return _load_profiles(project_id).get(calibration_hash, {})


def save_calibration(project_id: str, data: dict) -> None:
    """Merge `data` into this physical unit's calibration profile (generating and
    persisting a CALIBRATION_HASH on first save) and write it back, pretty-printed
    with sorted keys for stable diffs."""
    path = _calibration_path(project_id)
    profiles = _load_profiles(project_id)

    calibration_hash = get_or_create_calibration_hash()
    profile = profiles.get(calibration_hash, {})
    profile.update(data)
    profiles[calibration_hash] = profile

    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(profiles, json_file, indent=2, sort_keys=True)
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
