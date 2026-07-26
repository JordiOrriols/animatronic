# Calibration

The `calibration` module persists and version-controls per-project servo limits, one file per physical unit.

## What it does

Multiple physical units of the same project (e.g. two skeletons 3D-printed at different times) can end up with different servo limits due to print tolerances and servo wear. To support that, each physical unit gets its **own** calibration file:

```
projects/<project_id>/servo_calibration/<calibration_id>.json
```

instead of every unit sharing and editing one file - this keeps units from ever needing to merge their calibration changes against each other in git. Which file a given unit uses is recorded in its own local `.env` file, under `CALIBRATION_ID`.

A unit's `.version` copy, `.env`, and calibration files are all local/gitignored except the calibration JSON files themselves, which are committed (see `git_commit_and_push` below).

## Main functions

- `get_or_create_calibration_id()`: returns this physical unit's calibration id from `.env`, generating and persisting a new UUIDv4 the first time this unit is ever calibrated.
- `load_calibration(project_id)`: loads this unit's saved calibration data from its `servo_calibration/<CALIBRATION_ID>.json` file. Returns `{}` if there's no id yet, or the file is missing/invalid.
- `has_calibration(project_id)`: whether this unit already has saved calibration data for `project_id`. Used by `Project.get_capabilities()` to gate movement features (play/generative/xbox/evaluate) until the unit has actually been calibrated.
- `save_calibration(project_id, data)`: merges `data` (a `{servo_name: {"min", "max", "rest"}}` dict) into this unit's own calibration file, generating a `CALIBRATION_ID` on first save, and writes it back pretty-printed with sorted keys for stable diffs.
- `git_commit_and_push(project_id)`: commits this unit's own calibration file on a fresh, timestamped branch (`calibration/<project_id>-<timestamp>`) and pushes it - calibration changes are never committed directly on `main`. Always attempts to switch back to `main` afterward, even on failure. Any git error is logged as a warning and never raised, since calibration must not crash the client. Returns `True` if a commit was actually pushed.

## Example

```python
from common.calibration import has_calibration, load_calibration, save_calibration, git_commit_and_push

project_id = "skeleton"

if not has_calibration(project_id):
    print("This unit has not been calibrated yet")

save_calibration(project_id, {"head": {"min": 10, "max": 170, "rest": 90}})
git_commit_and_push(project_id)

print(load_calibration(project_id))
```

## Notes

- `CALIBRATION_ID_ENV_KEY` is `"CALIBRATION_ID"`. Set it to `default` to use the file seeded with a project's original hardcoded values, leave it unset on a brand new unit to have a UUIDv4 generated automatically on first calibration, or set it manually if you want to reuse/copy an existing unit's file.
- `load_dotenv()` is called at **module import time** (not only inside `Project.__init__()`), because project config modules (e.g. `projects/skeleton/config.py`) read `CALIBRATION_ID` while building their servo list at import time, which happens before `Project.__init__()` ever runs.
- The calibration flow itself (interactive Neutral/Min/Max prompts over the CLI) lives in `server.py`'s `calibrate()`/`_calibrate_servo()`/`_adjust_value()` functions, which drive `Project.calibrate_move()` / `calibrate_save()` / `calibrate_commit()` on the client through websocket messages.
