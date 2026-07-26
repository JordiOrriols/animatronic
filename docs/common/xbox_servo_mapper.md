# XboxServoMapper

`XboxServoMapper` runs on the **client** (which owns the physical servos) and maps raw Xbox controller axis values received from the server into target servo angles.

## What it does

It takes a project's `xbox_settings` config (per-servo axis mapping, similar in spirit to `generative_settings`) and maps the raw values produced by [`XboxInputReader`](xbox_input.md) into target servo angles, applying a small amount of smoothing so movement isn't jittery while still feeling near real-time.

## Configuration keys

Config dictionary supported keys per servo, keyed by servo name (all but `input` are optional):

- `input`: axis name (see `common.xbox_input.AXIS_INDEX`) that drives this servo (required).
- `invert`: bool, flips the axis direction.
- `min_angle`, `max_angle`: bounds (degrees) to use for targets, clipped to the servo's calibrated limits.
- `smoothing`: `0.0..1.0` fraction of the remaining distance covered per update (higher = snappier/less eased, lower = smoother/more lag). Default `0.35`.

## Main methods

- `__init__(servos_data, xbox_settings=None)`: creates the mapper for a list of `AniServo` and a project's `xbox_settings`.
- `reset()`: seeds internal smoothing state from each mapped servo's current position.
- `update(raw_axes)`: advances every mapped servo towards its new target based on `raw_axes` (as produced by `XboxInputReader.poll_axes()`). Non-blocking; safe to call every time a new position message is received.

## Example

```python
from common.xbox_servo_mapper import XboxServoMapper

xbox_settings = {
    "head": {"input": "left_stick_x", "invert": False, "smoothing": 0.3},
}

mapper = XboxServoMapper(servos_data, xbox_settings)
mapper.update({"left_stick_x": 0.5})
```

## Notes

`Project.xbox_start()` creates the mapper (seeded at current positions), `xbox_update(raw_axes)` forwards each incoming message to `update()`, and `xbox_stop()` discards it - servos hold their last commanded position.
