# GenerativeMovement

`GenerativeMovement` creates smooth, non-blocking servo motion for automatic or idle-mode behavior.

## What it does

It keeps a simple state machine with a waiting phase and a moving phase. Each cycle chooses a target angle, applies easing, and optionally returns to the servo rest position.

In project Auto mode, only servos explicitly listed in `generative_settings` on the client/Pi are enabled. Unlisted servos return to their calibrated neutral/rest position and stay there. An entry such as `"wings": {}` enables movement with default settings; remove the entry to disable that servo's automatic movement. Creating `GenerativeMovement(servo)` directly still uses defaults.

The project runs Auto updates in a background worker, leaving websocket reception available for `automatic-mode-stop`. Stop waits for any current update and the eased return to neutral to finish before the client sends its completion message.

## Configuration keys

The configuration dictionary may contain:

- `min_duration_ms`, `max_duration_ms`: movement time range.
- `min_wait_ms`, `max_wait_ms`: time between movements.
- `min_angle`, `max_angle`: target bounds in degrees.
- `random_factor`: how much of the allowed range is used.
- `min_range_fraction`, `max_range_fraction`: independent fractions of calibrated travel from neutral toward Min and Max. Each must be a finite number from `0.0` to `1.0`, with `1.0` (100%) as the default. `0.0` disables travel on that side; both zero target neutral. The allowed interval is `neutral - (neutral - min) * min_range_fraction` through `neutral + (max - neutral) * max_range_fraction`, rounded inward to integer degrees.
- `ease_in`, `ease_out`: easing strength.
- `return_to_rest`: whether the servo should return to its rest position after each movement. Returns use a non-blocking ease-in/ease-out phase with a duration chosen from the configured movement duration range, not an immediate position jump. The shared `AniServo.apply_easing()` formula uses 0.2 ease-in and ease-out for returns; outbound movements retain their configured easing factors.
- `rest_hold_ms`: hold duration at rest before the next move.

Angle overrides intersect the fractional interval; they cannot expand it. `random_factor` further narrows that interval using the existing centered-randomness behavior. For example, with Min 20, neutral 80, and Max 160, fractions `0.5` and `0.25` permit 50 through 100 degrees. Neutral must lie within the calibrated limits. Invalid fractions or disjoint angle overrides raise an error instead of silently allowing unsafe motion.

## Main methods

- `__init__(servo, config=None)`: creates the controller for one servo.
- `update()`: advances the movement state and moves the servo if needed.

## Example

```python
from common.generative import GenerativeMovement

controller = GenerativeMovement(
    servo,
    {
        "min_duration_ms": 150,
        "max_duration_ms": 600,
        "min_wait_ms": 100,
        "max_wait_ms": 500,
        "min_angle": 40,
        "max_angle": 140,
        "random_factor": 0.8,
        "min_range_fraction": 1.0,
        "max_range_fraction": 1.0,
        "ease_in": 0.2,
        "ease_out": 0.2,
        "return_to_rest": True,
        "rest_hold_ms": 200,
    },
)

while True:
    controller.update()
    time.sleep(0.02)
```
