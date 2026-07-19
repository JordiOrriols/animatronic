# AutoDiscovery

The auto-discovery modules let a client find a server on the local network and let a server announce its IP address.

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
