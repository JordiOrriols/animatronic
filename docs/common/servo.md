# AniServo

`AniServo` represents a single servo and handles its physical limits, rest position, and movement commands.

## Main methods

- `__init__(name, pin, servo_type, min_val, max_val, rest_position)`: creates the servo object with hardware metadata and calls `set_calibration()` to set its initial limits.
- `get_name()`, `get_pin()`: return the servo identity.
- `get_physical_limit_min()`, `get_physical_limit_max()`: return the currently calibrated angle limits.
- `get_rest_position()`: returns the standby/rest angle.
- `get_current_position()`: returns the last known position.
- `connect(servo, direction)`: links a second servo so both move together.
- `start(kit)`: prepares the servo with the hardware kit.
- `sleep()`: moves the servo to the rest position.
- `move_to_angle(position)`: sends a target angle to the servo, clamped to the calibrated min/max limits.
- `move_to_calibration_angle(position)`: moves the servo while searching for new calibration bounds, bypassing the configured min/max limits and clamping only to the servo's physical actuation range.
- `set_calibration(min_val, max_val, rest_position)`: updates the servo's calibrated limits and rest position at runtime (used both at construction time and when applying new calibration values).
- `to_calibration_dict()`: returns the current calibration as a plain `{"min", "max", "rest"}` dict, used to build `Project.get_servo_summary()` and to persist calibration files (see [calibration.md](calibration.md)).

## Helper

- `initialize_servos(kit, servos_data)`: initializes every servo in a list with the given ServoKit.

## Example

```python
from common.servo import AniServo, initialize_servos
from adafruit_servokit import ServoKit

servo = AniServo("head", 1, "MG90S", 10, 180, 90)
kit = ServoKit(channels=16)
servo.start(kit)
servo.move_to_angle(120)
```

## Notes

Calibrated limits are not fixed at construction time: `Project.calibrate_save()` calls `set_calibration()` again with new values discovered during a calibration session, and those values are what get persisted via [`common/calibration.py`](calibration.md).
