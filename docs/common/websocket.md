# WebSocketClient

`WebSocketClient` connects the client to the server over a WebSocket and exchanges action messages.

## Main methods

- `__init__()`: creates the client and its auto-discovery helper.
- `connect()`: discovers the server, opens the socket, and sends the initial connection message.
- `ready(handler, handshake=None)`: sends `handshake` (typically `{"capabilities", "servos", "version"}`, see [project.md](project.md) and [version.md](version.md)) as the client-ready message, then waits for incoming messages and dispatches each to `handler`.
- `send(action, *data)`: sends a JSON message to the server.

## Example

```python
import asyncio
from common.project import Project
from common.version import get_version
from common.websocket import WebSocketClient

client = WebSocketClient()
client.connect()
project = Project()

async def handle(message):
    print(message)

handshake = {
    "capabilities": project.get_capabilities(),
    "servos": project.get_servo_summary(),
    "version": get_version(),
}
asyncio.run(client.ready(handle, handshake))
```

## Notes

The client uses the auto-discovery layer first, so the server must be reachable on the local network. The `handshake` payload lets the server build its menu (hiding options the project doesn't support or that require calibration) and log which client version connected, without importing any project-specific code.
