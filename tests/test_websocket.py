import asyncio

from common.websocket import WebSocketClient


class FakeWebSocketConnection:
    def __init__(self):
        self.sent = []
        self.closed = False
        self._messages = iter(
            [
                '{"action": "client-ready", "data": []}',
                '{"action": "exit", "data": []}',
            ]
        )

    def send(self, message):
        self.sent.append(message)

    def recv(self):
        return next(self._messages)

    def close(self):
        self.closed = True


class FakeAutoDiscoveryClient:
    def listen(self):
        return "127.0.0.1"


def test_websocket_client_connects_and_reads_messages(monkeypatch):
    monkeypatch.setattr("common.websocket.AutoDiscoveryClient", FakeAutoDiscoveryClient)
    monkeypatch.setattr("common.websocket.connect", lambda uri: FakeWebSocketConnection())

    client = WebSocketClient()
    client.connect()

    received = []

    def handler(message):
        received.append(message)

    asyncio.run(client.ready(handler))
    assert received == [
        {"action": "client-ready", "data": []},
        {"action": "exit", "data": []},
    ]

