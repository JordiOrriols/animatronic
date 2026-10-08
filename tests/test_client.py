import asyncio
import threading

import pytest

import client as client_app
import common.project as project_module
from common.project import Project
from common.websocket import WebSocketClient


class FakeProject:
    def __init__(self):
        self.calls = []

    def load_animation(self, name):
        self.calls.append(("load", name))

    def play(self):
        self.calls.append(("play",))

    def auto_start(self):
        self.calls.append(("auto-start",))

    def auto_stop(self):
        self.calls.append(("auto-stop",))

    def calibrate_move(self, servo_pin, position):
        self.calls.append(("calibrate-move", servo_pin, position))

    def calibrate_save(self, servo_pin, neutral, min_val, max_val):
        self.calls.append(("calibrate-save", servo_pin, neutral, min_val, max_val))

    def calibrate_commit(self):
        self.calls.append(("calibrate-commit",))

    def evaluate(self):
        self.calls.append(("evaluate",))

    def standby(self):
        self.calls.append(("standby",))

    def xbox_start(self):
        self.calls.append(("xbox-start",))

    def xbox_update(self, raw_axes):
        self.calls.append(("xbox-update", raw_axes))

    def xbox_stop(self):
        self.calls.append(("xbox-stop",))


class FakeClient:
    def __init__(self):
        self.sent = []

    def connect(self):
        return None

    def send(self, action, *data):
        self.sent.append((action, data))

    def ready(self, handler):
        return None


def test_client_handler_routes_messages(monkeypatch):
    fake_client = FakeClient()
    fake_project = FakeProject()

    monkeypatch.setattr(client_app.RUNTIME, "client", fake_client)
    monkeypatch.setattr(client_app.RUNTIME, "project", fake_project)
    monkeypatch.setattr(client_app.subprocess, "run", lambda *args, **kwargs: None)

    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["play"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["auto-start"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["auto-stop"]})
    client_app.handler(
        {"action": client_app.WEBSOCKET_MESSAGES["calibrate-move"], "data": [{"servo_pin": 1, "position": 2}]}
    )
    client_app.handler(
        {
            "action": client_app.WEBSOCKET_MESSAGES["calibrate-save"],
            "data": [{"servo_pin": 1, "neutral": 90, "min": 20, "max": 150}],
        }
    )
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["calibrate-commit"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["evaluate"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["standby"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["xbox-start"]})
    client_app.handler(
        {
            "action": client_app.WEBSOCKET_MESSAGES["xbox-position"],
            "data": [{"left_stick_x": 0.5}],
        }
    )
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["xbox-stop"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["reboot"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["exit"]})

    assert fake_project.calls[0] == ("play",)
    assert fake_project.calls[1] == ("auto-start",)
    assert fake_project.calls[2] == ("auto-stop",)
    assert fake_project.calls[3] == ("calibrate-move", 1, 2)
    assert fake_project.calls[4] == ("calibrate-save", 1, 90, 20, 150)
    assert fake_project.calls[5] == ("calibrate-commit",)
    assert fake_project.calls[6] == ("evaluate",)
    assert fake_project.calls[7] == ("standby",)
    assert fake_project.calls[8] == ("xbox-start",)
    assert fake_project.calls[9] == ("xbox-update", {"left_stick_x": 0.5})
    assert fake_project.calls[10] == ("xbox-stop",)


def test_main_sends_capabilities_servos_and_version(monkeypatch):
    fake_client = FakeClient()
    fake_project = FakeProject()
    fake_project.get_capabilities = lambda: {"animation": True}
    fake_project.get_servo_summary = lambda: [{"name": "head"}]

    sent = {}

    async def fake_ready(handler, handshake=None):
        sent["handshake"] = handshake

    fake_client.ready = fake_ready

    monkeypatch.setattr(client_app.RUNTIME, "client", fake_client)
    monkeypatch.setattr(client_app.RUNTIME, "project", fake_project)
    monkeypatch.setattr(client_app, "get_version", lambda: "9.9.9")

    client_app.main()

    assert sent["handshake"] == {
        "capabilities": {"animation": True},
        "servos": [{"name": "head"}],
        "version": "9.9.9",
    }


def test_websocket_receives_auto_stop_while_movements_are_running(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    project = Project(init_servos=False)
    updated = threading.Event()
    movements = []

    class Controller:
        def __init__(self, servo, config):
            self.servo = servo

        def update(self):
            movements.append(self.servo.get_name())
            updated.set()

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    fake_client = FakeClient()
    monkeypatch.setattr(client_app.RUNTIME, "client", fake_client)
    monkeypatch.setattr(client_app.RUNTIME, "project", project)
    actions = iter(["auto-start", "auto-stop", "exit"])

    class Connection:
        def recv(self):
            action = next(actions)
            if action == "auto-stop":
                assert updated.wait(1), "Auto worker never started"
            return '{"action": "' + client_app.WEBSOCKET_MESSAGES[action] + '"}'

        def send(self, message):
            return None

        def close(self):
            return None

    websocket = WebSocketClient()
    websocket._WebSocketClient__websocket = Connection()
    watchdog = threading.Timer(1, project.auto_stop)
    watchdog.start()
    try:
        def handle(message):
            if message["action"] != client_app.WEBSOCKET_MESSAGES["exit"]:
                client_app.handler(message)
        asyncio.run(websocket.ready(handle))
        assert watchdog.is_alive(), "Auto start blocked receipt of the stop command"
        assert movements
        assert fake_client.sent == [(client_app.WEBSOCKET_MESSAGES["finished"], ())]
        count_after_stop = len(movements)
        threading.Event().wait(0.05)
        assert len(movements) == count_after_stop
    finally:
        watchdog.cancel()
        watchdog.join()
        project.auto_stop()


def test_main_stops_auto_on_connection_failure(monkeypatch):
    fake_client = FakeClient()
    fake_project = FakeProject()
    fake_project.get_capabilities = lambda: {}
    fake_project.get_servo_summary = lambda: []

    async def disconnected(handler, handshake=None):
        raise ConnectionError("Disconnected")

    fake_client.ready = disconnected
    monkeypatch.setattr(client_app.RUNTIME, "client", fake_client)
    monkeypatch.setattr(client_app.RUNTIME, "project", fake_project)

    with pytest.raises(ConnectionError, match="Disconnected"):
        client_app.main()

    assert fake_project.calls == [("auto-stop",)]
