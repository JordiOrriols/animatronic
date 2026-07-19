# GenerativeMovement

`GenerativeMovement` creates smooth, non-blocking servo motion for automatic or idle-mode behavior.

## What it does

It keeps a simple state machine with a waiting phase and a moving phase. Each cycle chooses a target angle, applies easing, and optionally returns to the servo rest position.

## Configuration keys

The configuration dictionary may contain:

- `min_duration_ms`, `max_duration_ms`: movement time range.
- `min_wait_ms`, `max_wait_ms`: time between movements.
- `min_angle`, `max_angle`: target bounds in degrees.
- `random_factor`: how much of the allowed range is used.
- `ease_in`, `ease_out`: easing strength.
- `return_to_rest`: whether the servo should return to its rest position after each movement.
- `rest_hold_ms`: hold duration at rest before the next move.

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
