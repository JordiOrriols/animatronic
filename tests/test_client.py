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

    def calibrate(self, servo_pin, position):
        self.calls.append(("calibrate", servo_pin, position))

    def evaluate(self):
        self.calls.append(("evaluate",))

    def standby(self):
        self.calls.append(("standby",))


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

    monkeypatch.setattr(client_app, "client", fake_client)
    monkeypatch.setattr(client_app, "project", fake_project)
    monkeypatch.setattr(client_app.subprocess, "run", lambda *args, **kwargs: None)

    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["play"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["auto-start"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["auto-stop"]})
    client_app.handler(
        {"action": client_app.WEBSOCKET_MESSAGES["calibrate"], "data": [{"servo_pin": 1, "position": 2}]}
    )
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["evaluate"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["standby"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["reboot"]})
    client_app.handler({"action": client_app.WEBSOCKET_MESSAGES["exit"]})

    assert fake_project.calls[0] == ("play",)
    assert fake_project.calls[1] == ("auto-start",)
    assert fake_project.calls[2] == ("auto-stop",)
    assert fake_project.calls[3] == ("calibrate", 1, 2)
    assert fake_project.calls[4] == ("evaluate",)
    assert fake_project.calls[5] == ("standby",)
