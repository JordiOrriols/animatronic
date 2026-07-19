# Common module reference

This folder documents the shared modules under the `common` package. They cover animation playback, servo control, project setup, auto-discovery, generative motion, and websocket communication.

## Module index

- [Animation](animation.md)
- [AutoDiscovery](autodiscovery.md)
- [GenerativeMovement](generative.md)
- [Project](project.md)
- [AniServo](servo.md)
- [WebSocketClient](websocket.md)

## Quick start

Most modules are imported directly from the repository root:

```python
from common.animation import Animation
from common.project import Project
from common.servo import AniServo
from common.websocket import WebSocketClient
```

When running locally, make sure the repository root is on `PYTHONPATH` or start the script from the project root.
