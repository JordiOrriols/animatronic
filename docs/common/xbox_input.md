# XboxInputReader

`XboxInputReader` runs on the **server** (which has the physical Xbox controller attached) and wraps `pygame.joystick` to poll raw stick/trigger values.

## What it does

It produces a small flat dict of named, normalized values (deadzone applied to sticks, triggers normalized to `0.0..1.0`) that gets sent as-is over the websocket to the client. The client then maps them to servo angles via [`XboxServoMapper`](xbox_servo_mapper.md).

`pygame` is imported lazily inside each method, so this module (and anything that imports it, like `server.py`) can be imported without `pygame` installed when no physical Xbox controller is being used.

## Main methods

- `__init__(deadzone=0.08)`: creates the reader with a stick deadzone.
- `connect() -> bool`: initializes pygame and grabs the first connected controller. Returns `False` (and logs an error) if none is found.
- `is_connected() -> bool`: checks whether a controller is still connected.
- `disconnect()`: releases the controller and shuts down the joystick subsystem.
- `poll_axes() -> dict`: reads the current state of all mapped axes/triggers, e.g. `{"left_stick_x": 0.0, ..., "right_trigger": 0.0}`, with stick values in `-1.0..1.0` (deadzone applied) and trigger values in `0.0..1.0`.

## Example

```python
from common.xbox_input import XboxInputReader

reader = XboxInputReader()
if reader.connect():
    axes = reader.poll_axes()
    print(axes)
    reader.disconnect()
```

## Notes

- `AXIS_INDEX` maps named axes (`left_stick_x`, `left_stick_y`, `right_stick_x`, `right_stick_y`, `left_trigger`, `right_trigger`) to pygame/SDL2 axis indices for a standard Xbox controller on macOS; exact indices can vary slightly between controller models and pygame/SDL versions. If mappings look wrong for your hardware, enable debug logging (`reader.debug()`) to print raw axis values and adjust the table.
- `server.py`'s `xbox_control()`/`xbox_stream_loop()` drive this class, streaming `poll_axes()` results to the client at a fixed interval until the user stops it or the controller disconnects.
