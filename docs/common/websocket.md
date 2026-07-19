# WebSocketClient

`WebSocketClient` connects the client to the server over a WebSocket and exchanges action messages.

## Main methods

- `__init__()`: creates the client and its auto-discovery helper.
- `connect()`: discovers the server, opens the socket, and sends the initial connection message.
- `ready(handler)`: waits for incoming messages and dispatches them to a handler.
- `send(action, *data)`: sends a JSON message to the server.

## Example

```python
import asyncio
from common.websocket import WebSocketClient

client = WebSocketClient()
client.connect()

async def handle(message):
    print(message)

asyncio.run(client.ready(handle))
```

## Notes

The client uses the auto-discovery layer first, so the server must be reachable on the local network.
