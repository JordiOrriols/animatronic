# AutoDiscovery

The auto-discovery modules let a client find a server on the local network and let a server announce its IP address.

The server pauses announcements when a client reports `client-connected` and resumes them when that client's websocket session ends, including normal disconnects and connection errors. It keeps the existing discovery thread and websocket listener running, so another client can discover and connect without restarting the server. Announcements resume on the broadcast loop's next iteration (up to 10 seconds when previously paused).

## Classes

### `AutoDiscoveryClient`

Used by the client side.

#### Methods

- `__init__()`: creates the UDP socket and binds it.
- `listen()`: waits for a broadcast packet from the server and returns the discovered IP address.

#### Example

```python
from common.autodiscovery import AutoDiscoveryClient

client = AutoDiscoveryClient()
server_ip = client.listen()
print(server_ip)
```

### `AutoDiscoveryServer`

Used by the server side.

#### Methods

- `__init__()`: prepares the broadcast socket.
- `start()`: starts broadcasting the server IP address.
- `disable()`: stops broadcasting temporarily.
- `enable()`: resumes broadcasting.
- `get_current_ip()`: returns the current detected local IP.

#### Example

```python
from common.autodiscovery import AutoDiscoveryServer

server = AutoDiscoveryServer()
server.start()
```
