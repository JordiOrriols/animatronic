import asyncio
import json
import threading

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


def test_show_options_hides_gated_options_when_unsupported(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    seen_options = {}

    class RecordingMenu(FakeTerminalMenu):
        def __init__(self, options, title=None):
            super().__init__(options, title)
            seen_options["options"] = options

        def show(self):
            return 1  # "[s] Standby" - avoids invoking calibrate()'s blocking input()

    monkeypatch.setattr(server_app, "send_message", fake_send_message)
    monkeypatch.setattr(server_app, "TerminalMenu", RecordingMenu)

    capabilities = {"animation": False, "generative": False, "xbox": False}
    asyncio.run(server_app.show_options(FakeWebSocket(), capabilities))

    # Only the always-shown options should remain, in order, starting with Calibrate.
    assert seen_options["options"] == [
        "[c] Calibrate",
        "[s] Standby",
        "[r] Reboot",
        "[e] Exit",
    ]
    assert sent[0][0] == server_app.WEBSOCKET_MESSAGES["standby"]


def test_show_options_default_capabilities_show_full_menu(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    monkeypatch.setattr(server_app, "send_message", fake_send_message)
    monkeypatch.setattr(server_app, "playsound", lambda *args, **kwargs: None)
    monkeypatch.setattr(server_app, "TerminalMenu", FakeTerminalMenu)

    # No capabilities passed (older client) -> full menu, Play still first.
    asyncio.run(server_app.show_options(FakeWebSocket()))
    assert sent[0][0] == server_app.WEBSOCKET_MESSAGES["play"]


def test_handler_forwards_capabilities_from_ready_message(monkeypatch):
    received_capabilities = {}

    async def fake_show_options(websocket, capabilities=None):
        received_capabilities.update(capabilities or {})

    async def fake_send_message(websocket, action, *data):
        return None

    class FakeWebSocket:
        async def __aiter__(self):
            yield json.dumps(
                {
                    "action": "client-ready",
                    "data": [{"animation": False, "generative": True, "xbox": True}],
                }
            )

    monkeypatch.setattr(server_app, "show_options", fake_show_options)
    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    asyncio.run(server_app.handler(FakeWebSocket()))

    assert received_capabilities == {
        "animation": False,
        "generative": True,
        "xbox": True,
    }



class FakeXboxInputReader:
    def __init__(self, *args, **kwargs):
        self.connected = True
        self.poll_calls = 0

    def connect(self):
        return True

    def is_connected(self):
        return self.connected

    def poll_axes(self):
        self.poll_calls += 1
        return {"left_stick_x": 0.5}

    def disconnect(self):
        self.connected = False


def test_show_options_selects_xbox_controller(monkeypatch):
    called = {}

    async def fake_xbox_control(websocket):
        called["websocket"] = websocket

    class FakeXboxMenu(FakeTerminalMenu):
        def show(self):
            return 2

    monkeypatch.setattr(server_app, "TerminalMenu", FakeXboxMenu)
    monkeypatch.setattr(server_app, "xbox_control", fake_xbox_control)

    asyncio.run(server_app.show_options(FakeWebSocket()))
    assert called["websocket"] is not None


def test_xbox_stream_loop_sends_positions_until_stopped(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    reader = FakeXboxInputReader()
    stop_event = threading.Event()

    async def stopper():
        # Stop after a couple of iterations instead of relying on real input().
        while reader.poll_calls < 2:
            await asyncio.sleep(0)
        stop_event.set()

    async def run_loop():
        results = await asyncio.gather(
            server_app.xbox_stream_loop(FakeWebSocket(), reader, stop_event, 0),
            stopper(),
        )
        return results[0]

    disconnected = asyncio.run(run_loop())

    assert disconnected is False
    assert reader.poll_calls >= 2
    assert all(action == server_app.WEBSOCKET_MESSAGES["xbox-position"] for action, _ in sent)


def test_xbox_stream_loop_detects_disconnect(monkeypatch):
    async def fake_send_message(*args, **kwargs):
        return None

    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    reader = FakeXboxInputReader()
    reader.connected = False
    stop_event = threading.Event()

    disconnected = asyncio.run(
        server_app.xbox_stream_loop(FakeWebSocket(), reader, stop_event, 0)
    )

    assert disconnected is True
