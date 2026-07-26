# Common module reference

This folder documents the shared modules under the `common` package. They cover animation playback, servo control and calibration, project setup, auto-discovery, generative motion, Xbox controller support, websocket communication, versioning, and logging.

## Module index

- [Animation](animation.md)
- [AutoDiscovery](autodiscovery.md)
- [Calibration](calibration.md)
- [Config](config.md)
- [GenerativeMovement](generative.md)
- [Logger](logger.md)
- [Project](project.md)
- [AniServo](servo.md)
- [Version](version.md)
- [WebSocketClient](websocket.md)
- [XboxInputReader](xbox_input.md)
- [XboxServoMapper](xbox_servo_mapper.md)

## Quick start

Most modules are imported directly from the repository root:

```python
from common.animation import Animation
from common.calibration import has_calibration, load_calibration
from common.project import Project
from common.servo import AniServo
from common.version import get_version
from common.websocket import WebSocketClient
```

When running locally, make sure the repository root is on `PYTHONPATH` or start the script from the project root - several modules (`common/calibration.py`, `common/project.py`, `common/version.py`) resolve project-relative paths (`.version`, `.env`, `projects/<id>/...`) against the current working directory.
