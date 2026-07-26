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


def test_show_options_hides_movement_options_until_calibrated(monkeypatch):
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

    capabilities = {"calibrated": False}
    asyncio.run(server_app.show_options(FakeWebSocket(), capabilities))

    # Play/Auto/Xbox/Evaluate all require calibration; Calibrate/Standby/Reboot/Exit don't.
    assert seen_options["options"] == [
        "[c] Calibrate",
        "[s] Standby",
        "[r] Reboot",
        "[e] Exit",
    ]
    assert sent[0][0] == server_app.WEBSOCKET_MESSAGES["standby"]


def test_handler_forwards_capabilities_and_servos_from_ready_message(monkeypatch):
    received = {}

    async def fake_show_options(websocket, capabilities=None, servos=None):
        received["capabilities"] = capabilities
        received["servos"] = servos

    async def fake_send_message(websocket, action, *data):
        return None

    class FakeWebSocket:
        async def __aiter__(self):
            yield json.dumps(
                {
                    "action": "client-ready",
                    "data": [
                        {
                            "capabilities": {"animation": False, "generative": True, "xbox": True},
                            "servos": [{"name": "head", "pin": 1, "min": 10, "max": 170, "rest": 90}],
                        }
                    ],
                }
            )

    monkeypatch.setattr(server_app, "show_options", fake_show_options)
    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    asyncio.run(server_app.handler(FakeWebSocket()))

    assert received["capabilities"] == {
        "animation": False,
        "generative": True,
        "xbox": True,
    }
    assert received["servos"] == [{"name": "head", "pin": 1, "min": 10, "max": 170, "rest": 90}]



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


def test_calibrate_without_servos_logs_error_and_returns(monkeypatch):
    called = {"menu": False}

    class ShouldNotBeCalledMenu:
        def __init__(self, *args, **kwargs):
            called["menu"] = True

        def show(self):
            return 0

    monkeypatch.setattr(server_app, "TerminalMenu", ShouldNotBeCalledMenu)

    asyncio.run(server_app.calibrate(FakeWebSocket(), []))
    assert called["menu"] is False


def test_adjust_value_nudges_then_confirms(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    inputs = iter(["+", "-", "-", "done"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    result = asyncio.run(server_app._adjust_value(FakeWebSocket(), 1, "Min", 100))

    assert result == 95
    assert [action for action, _ in sent] == [server_app.WEBSOCKET_MESSAGES["calibrate-move"]] * 3


def test_calibrate_all_servos_runs_neutral_min_max_flow(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    class AllMenu(FakeTerminalMenu):
        def show(self):
            return 0  # "[all] Calibrate ALL servos"

    monkeypatch.setattr(server_app, "TerminalMenu", AllMenu)

    inputs = iter(["", "x", "x", "x"])  # blank neutral (defaults to 90), confirm x3
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    servos = [{"name": "head", "pin": 1, "min": 10, "max": 170, "rest": 90}]
    asyncio.run(server_app.calibrate(FakeWebSocket(), servos))

    actions = [action for action, _ in sent]
    assert actions == [
        server_app.WEBSOCKET_MESSAGES["calibrate-move"],
        server_app.WEBSOCKET_MESSAGES["calibrate-save"],
        server_app.WEBSOCKET_MESSAGES["calibrate-commit"],
        server_app.WEBSOCKET_MESSAGES["standby"],
    ]
    save_payload = sent[1][1][0]
    assert save_payload == {"servo_pin": 1, "neutral": 90, "min": 10, "max": 170}


def test_calibrate_selects_single_servo_not_all(monkeypatch):
    sent = []

    async def fake_send_message(websocket, action, *data):
        sent.append((action, data))

    monkeypatch.setattr(server_app, "send_message", fake_send_message)

    class SingleMenu(FakeTerminalMenu):
        def show(self):
            return 2  # "[all]" is 0, servos[0] is 1, servos[1] is 2

    monkeypatch.setattr(server_app, "TerminalMenu", SingleMenu)

    inputs = iter(["", "x", "x", "x"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    servos = [
        {"name": "a", "pin": 1, "min": 0, "max": 180, "rest": 90},
        {"name": "b", "pin": 2, "min": 20, "max": 150, "rest": 80},
    ]
    asyncio.run(server_app.calibrate(FakeWebSocket(), servos))

    save_payload = [data[0] for action, data in sent if action == server_app.WEBSOCKET_MESSAGES["calibrate-save"]]
    assert save_payload == [{"servo_pin": 2, "neutral": 90, "min": 20, "max": 150}]
