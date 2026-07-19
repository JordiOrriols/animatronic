import asyncio

import server as server_app


class FakeWebSocket:
    async def send(self, message):
        return None


class FakeTerminalMenu:
    def __init__(self, options, title=None):
        self.options = options
        self.title = title

    def show(self):
        return 0


def test_show_options_sends_play_action(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    monkeypatch.setattr(server_app, "send_message", fake_send_message)
    monkeypatch.setattr(server_app, "playsound", lambda *args, **kwargs: None)
    monkeypatch.setattr(server_app, "TerminalMenu", FakeTerminalMenu)

    asyncio.run(server_app.show_options(FakeWebSocket()))
    assert sent[0][0] == server_app.WEBSOCKET_MESSAGES["play"]


def test_handler_disables_auto_discovery_on_connect(monkeypatch):
    class FakeDiscovery:
        def disable(self):
            self.disabled = True

    class FakeWebSocket:
        async def __aiter__(self):
            yield '{"action": "client-connected"}'

    discovery = FakeDiscovery()
    monkeypatch.setattr(server_app, "get_auto_discovery", lambda: discovery)

    async def run_handler():
        await server_app.handler(FakeWebSocket())

    asyncio.run(run_handler())
    assert discovery.disabled is True
