import client as client_app


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
