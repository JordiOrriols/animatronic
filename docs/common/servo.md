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
- `sleep()`: returns to rest using `move_to_angle_eased()` with its defaults.
- `move_to_angle_eased(position, duration_ms=1000, ease_in=0.2, ease_out=0.2)`: blocking movement from the current commanded angle to a calibrated target with approximately 20 ms updates. Duration is independent of distance; zero duration moves directly. Linked servos follow the interpolated movement. If the current angle is unknown, a warning is logged and the target is commanded directly.
- `apply_easing(progress, ease_in=0.2, ease_out=0.2)`: shared static easing formula used by both eased servo movements and non-blocking generative updates. Easing factors must be finite numbers from 0 to 1; zero factors produce linear interpolation.
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
servo.move_to_angle_eased(90, duration_ms=800, ease_in=0.3, ease_out=0.3)
```

## Notes

Calibrated limits are not fixed at construction time: `Project.calibrate_save()` calls `set_calibration()` again with new values discovered during a calibration session, and those values are what get persisted via [`common/calibration.py`](calibration.md).

## Startup and shutdown

Servo positions are not saved to disk or restored after restart. Current angles are commanded positions, not measured feedback. If there is no current hardware command, startup logs a warning and sends calibrated neutral directly because there is no known starting angle to interpolate from. Make a new or uncertain mechanism safe before powering its servos.

Normal exit, Ctrl+C, SIGTERM, disconnects, completed playback, Auto stop, and Xbox stop attempt eased returns to neutral. Abrupt power loss or SIGKILL cannot execute shutdown movement. Neutral returns are not a hardware emergency stop or a physical-speed guarantee.
