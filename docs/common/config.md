# Config

`config` centralizes constants shared across the codebase: servo hardware profiles, and network/websocket settings.

## Servo hardware profiles

`fabric_servo_data` maps a servo type constant to its hardware characteristics (`pulse_width` min/max in microseconds, and `actuation_range` in degrees), used by `AniServo.start()` to configure the physical servo correctly:

- `MG996R_TYPE` ("MG996R") - Standard servo.
- `MG92B_TYPE` ("MG92B") - Blue metal micro servo.
- `MG90S_TYPE` ("MG90S") - Purple metal micro servo, 180 degree version.
- `MG90S_90_TYPE` ("MG90S-90") - Purple metal micro servo, 90 degree version.
- `TS90MD_TYPE` ("TS90MD") - Purple metal micro servo, 180 degree version.
- `GHS37A_TYPE` ("GHS37A") - Nano servo.

Use these constants as the `servo_type` argument when constructing an `AniServo` (see [servo.md](servo.md)) or defining a project's servo list (e.g. `projects/skeleton/config.py`).

## Auto-discovery settings

- `DISCOVERY_PORT` (`50000`): UDP port used to broadcast/listen for the server's IP address (see [autodiscovery.md](autodiscovery.md)).
- `DISCOVERY_MAGIC`: a magic string prefix used to identify genuine broadcast packets from this project.

## Websocket settings

- `WEBSOCKET_PORT` (`8765`): TCP port the server listens on and the client connects to.
- `WEBSOCKET_MESSAGES`: the dictionary of action names used as the `"action"` field of every websocket message exchanged between `server.py` and `client.py` (e.g. `"ready"`, `"play"`, `"calibrate-move"`, `"xbox-start"`, `"exit"`). Both sides import from this single dict so action names never drift out of sync.

## Example

```python
from common.config import MG90S_TYPE, WEBSOCKET_PORT, WEBSOCKET_MESSAGES

print(WEBSOCKET_PORT)
print(WEBSOCKET_MESSAGES["ready"])
```
