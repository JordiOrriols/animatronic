import pytest

from common.autodiscovery import AutoDiscoveryClient, AutoDiscoveryServer


class FakeSocket:
    def __init__(self, packet=None):
        self.packet = packet
        self.sent = []
        self.closed = False
        self.bound = None
        self.options = []
        self.connected = None

    def bind(self, address):
        self.bound = address

    def setsockopt(self, level, optname, value):
        self.options.append((level, optname, value))

    def recvfrom(self, size):
        if self.packet is not None:
            packet = self.packet
            self.packet = None
            return packet, ("127.0.0.1", 1234)
        raise RuntimeError("no packet")

    def sendto(self, data, address):
        self.sent.append((data, address))

    def close(self):
        self.closed = True

    def connect(self, address):
        self.connected = address

    def getsockname(self):
        return ("192.168.0.10", 4321)


@pytest.mark.parametrize("packet, expected", [(b"jordiorriols-animatronic@127.0.0.1", "127.0.0.1")])
def test_autodiscovery_client_listens_for_broadcast(monkeypatch, packet, expected):
    monkeypatch.setattr("common.autodiscovery.socket", lambda *args: FakeSocket(packet))

    client = AutoDiscoveryClient()
    assert client.listen() == expected


def test_autodiscovery_server_can_be_enabled_and_disabled(monkeypatch):
    monkeypatch.setattr("common.autodiscovery.socket", lambda *args: FakeSocket())

    class FakeThread:
        def __init__(self, target=None):
            self.target = target

        def start(self):
            self.started = True

    monkeypatch.setattr("common.autodiscovery.threading.Thread", FakeThread)
    monkeypatch.setattr("common.autodiscovery.gethostbyname", lambda name: "10.0.0.1")
    monkeypatch.setattr("common.autodiscovery.gethostname", lambda: "host")

    server = AutoDiscoveryServer()
    server.start()
    server.disable()
    server.enable()
    assert server.get_current_ip() is None
