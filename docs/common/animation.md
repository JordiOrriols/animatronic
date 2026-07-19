# Animation

The `Animation` class loads animation data from a JSON-style dictionary and helps you advance it frame by frame.

## What it does

It stores the animation timing, frame positions, and can interpolate servo positions between frames.

## Main methods

- `__init__(data)`: stores the animation payload and computes timing values.
- `start()`: resets the internal timer and marks the animation as running.
- `refresh()`: advances the animation clock by one refresh tick.
- `end()`: stops the animation and logs summary metrics.
- `get_positions()`: returns the full position map for every servo.
- `get_current_position(servo)`: returns the interpolated position for a given servo.
- `in_progress()`: returns whether the animation is still running.

## Example

```python
from common.animation import Animation

animation_data = {
    "fps": 2,
    "frames": 3,
    "positions": {
        "head": [0, 10, 20],
    },
}

animation = Animation(animation_data)
animation.start()

while animation.in_progress():
    animation.refresh()
    position = animation.get_current_position(servo)
    servo.move_to_angle(int(position))

animation.end()
```
