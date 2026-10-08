# Project

The `Project` class loads project-specific servo data, animations, calibration, and automatic behavior. It is the main object used by [client.py](../../client.py) to act on messages received from the server.

## What it does

It ties together the selected project configuration (`PROJECT_ID`), the servo definitions and their per-unit [calibration](calibration.md), animation playback, generative mode, and Xbox controller mode.

## Main methods

- `__init__(init_servos=True)`: loads the project from the `PROJECT_ID` environment variable and initializes the servos.
- `get_servos_data()`: returns the `AniServo` objects for the current project.
- `get_servo_summary()`: returns `[{"name", "pin", "min", "max", "rest"}, ...]` for every servo - sent to the server on the client-ready handshake so it can build the calibration menu without importing any project-specific config.
- `get_capabilities()`: returns `{"animation", "generative", "xbox", "calibrated"}` booleans describing which optional features this project's configuration/calibration supports, so the server only offers options the client can actually run.
- `load_animation(animation_name)`: loads an animation JSON file from the project folder into memory (missing file just disables animation features instead of crashing).
- `evaluate()`: checks the loaded animation against each servo's calibrated limits and logs an error report.
- `play()`: plays the loaded animation and returns to neutral with easing on completion or failure.
- `auto_start()` / `auto_stop()`: start/stop generative (idle) movement for servos explicitly listed in the project's `generative_settings`. Unlisted servos return to their calibrated neutral/rest position when Auto mode starts and do not receive random movements.

  Auto movement runs in a managed background thread so the client can keep receiving websocket messages, including `automatic-mode-stop`. Repeated starts do not create duplicate workers. Stop signals and joins the worker, including its eased return to neutral, before returning. Standby, animation playback, calibration movement/saving, and Xbox mode stop Auto before taking control of the servos. Worker failures are logged, return to neutral where possible, and are raised by `auto_stop()` rather than acknowledged as success. The client returns to neutral when its receive loop exits or fails, and on Ctrl+C or SIGTERM.
- `calibrate_neutral(servo_pin)`: eases just the selected servo to its saved rest position at the start of calibration.
- `calibrate_move(servo_pin, position)`: live-preview a servo position while searching for new calibration bounds, bypassing its currently configured limits.
- `calibrate_save(servo_pin, neutral, min_val, max_val)`: apply new calibration values to a servo immediately and stage them for the next `calibrate_commit()`.
- `calibrate_commit()`: persist all staged calibration values to this unit's own local calibration file (see [calibration.md](calibration.md); these files are gitignored and never committed/pushed automatically).
- `standby()`: stops Auto and returns all servos to rest with ease-in/ease-out over one second per moving servo. Servos return sequentially.
- `xbox_start()` / `xbox_update(raw_axes)` / `xbox_stop()`: start Xbox controller mode, apply a new set of raw axis values received from the server, and stop the mode with an eased return to neutral.

## Example

```python
import os
from common.project import Project

os.environ["PROJECT_ID"] = "skeleton"
project = Project()
project.load_animation("animation")
project.play()
```

## Notes

- Per-project generative and Xbox settings can be defined in the project config module, for example under `projects/skeleton/config.py` or `projects/seagull/config.py` (`generative_settings` / `xbox_settings` dicts keyed by servo name).
- Neutral returns reuse `AniServo.move_to_angle_eased()` with its default one-second duration and easing factors of 0.2. No angular-speed limit or separate movement settings are used.
- `init_servos=False` disables hardware initialization for tests. Servo positions are not saved or restored after restart.
- `get_capabilities()["calibrated"]` is `False` until this physical unit has saved calibration data (see [calibration.md](calibration.md)); the server hides movement-related menu options (play/auto/xbox/evaluate) until it becomes `True`.
