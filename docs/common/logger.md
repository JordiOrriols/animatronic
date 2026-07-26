# Logger

`Logger` is a small mixin class providing colored, prefixed console logging. Most shared classes (`AniServo`, `Project`, `WebSocketClient`, `AutoDiscoveryClient`/`Server`, `GenerativeMovement`, `XboxInputReader`, `XboxServoMapper`) inherit from it.

## Main methods

- `__init__(log_name)`: stores the label prefixed to every message from this instance (e.g. `"AniServo head on pin #1"`).
- `debug()`: enables debug mode, so subsequent `log()` calls are actually printed.
- `log(*message)`: logs a message, but only when debug mode is enabled.
- `info(*message)`: logs an informational message (blue).
- `warning(*message)`: logs a warning message (orange).
- `error(*message)`: logs an error message (red).
- `success(*message)`: logs a success message (green).
- `input(*message)`: logs an input prompt (white) - used before interactive `input()` calls.

## Example

```python
from common.logger import Logger

class MyThing(Logger):
    def __init__(self):
        super().__init__("MyThing")

    def do_something(self):
        self.info("Doing something...")
        self.success("Done!")

MyThing().do_something()
```

## Notes

`server.py` and `client.py` also create module-level `Logger` instances directly (`logger = Logger("Main")`) for top-level log messages that aren't tied to a specific class instance.
