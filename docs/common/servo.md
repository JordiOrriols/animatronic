# AniServo

`AniServo` represents a single servo and handles its physical limits, rest position, and movement commands.

## Main methods

- `__init__(name, pin, servo_type, min_val, max_val, rest_position)`: creates the servo object with hardware metadata.
- `get_name()`, `get_pin()`: return the servo identity.
- `get_physical_limit_min()`, `get_physical_limit_max()`: return the allowed angle limits.
- `get_rest_position()`: returns the standby/rest angle.
- `get_current_position()`: returns the last known position.
- `connect(servo, direction)`: links a second servo so both move together.
- `start(kit)`: prepares the servo with the hardware kit.
- `sleep()`: moves the servo to the rest position.
- `move_to_angle(position)`: sends a clamped target angle to the servo.

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
