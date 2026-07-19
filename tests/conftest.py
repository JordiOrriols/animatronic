import sys
import types

# Stub hardware/runtime dependencies for import-safe tests.
fake_servokit = types.ModuleType("adafruit_servokit")


class FakeServoKit:
    def __init__(self, channels=16):
        self.channels = channels


fake_servokit.ServoKit = FakeServoKit
sys.modules.setdefault("adafruit_servokit", fake_servokit)
sys.modules.setdefault("board", types.ModuleType("board"))

websockets_module = types.ModuleType("websockets")
sync_module = types.ModuleType("websockets.sync")
client_module = types.ModuleType("websockets.sync.client")


class FakeWebSocketConnection:
    def __init__(self, uri):
        self.uri = uri
        self.sent = []
        self.closed = False

    def send(self, message):
        self.sent.append(message)

    def recv(self):
        return '{"action": "client-ready", "data": []}'

    def close(self):
        self.closed = True


client_module.connect = lambda uri: FakeWebSocketConnection(uri)
sys.modules.setdefault("websockets", websockets_module)
sys.modules.setdefault("websockets.sync", sync_module)
sys.modules.setdefault("websockets.sync.client", client_module)

playsound_module = types.ModuleType("playsound")
playsound_module.playsound = lambda *args, **kwargs: None
sys.modules.setdefault("playsound", playsound_module)

simple_term_menu_module = types.ModuleType("simple_term_menu")


class FakeTerminalMenu:
    def __init__(self, options, title=None):
        self.options = options
        self.title = title

    def show(self):
        return 0


simple_term_menu_module.TerminalMenu = FakeTerminalMenu
sys.modules.setdefault("simple_term_menu", simple_term_menu_module)

server_module = types.ModuleType("websockets.server")
server_module.serve = lambda handler, host, port: None
sys.modules.setdefault("websockets.server", server_module)
