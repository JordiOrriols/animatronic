import types
import sys

import pytest

from common.xbox_input import XboxInputReader


class FakeJoystick:
    def __init__(self, axis_values):
        self._axis_values = axis_values

    def init(self):
        return None

    def get_name(self):
        return "Fake Xbox Controller"

    def get_axis(self, index):
        return self._axis_values.get(index, 0.0)

    def quit(self):
        return None


@pytest.fixture
def fake_pygame(monkeypatch):
    fake_module = types.ModuleType("pygame")
    fake_module.error = Exception

    joystick_module = types.SimpleNamespace()
    state = {"count": 1, "joystick": None}

    def joystick_init():
        return None

    def get_count():
        return state["count"]

    def joystick_factory(index):
        joystick = FakeJoystick({0: 0.02, 1: -0.5, 2: 0.0, 3: 0.0, 4: -1.0, 5: 1.0})
        state["joystick"] = joystick
        return joystick

    def joystick_quit():
        return None

    joystick_module.init = joystick_init
    joystick_module.get_count = get_count
    joystick_module.Joystick = joystick_factory
    joystick_module.quit = joystick_quit

    fake_module.init = lambda: None
    fake_module.joystick = joystick_module
    fake_module.event = types.SimpleNamespace(pump=lambda: None)

    monkeypatch.setitem(sys.modules, "pygame", fake_module)
    return state


def test_reader_connects_when_controller_present(fake_pygame):
    reader = XboxInputReader()
    assert reader.connect() is True
    assert reader.is_connected() is True


def test_reader_connect_fails_when_no_controller(fake_pygame):
    fake_pygame["count"] = 0
    reader = XboxInputReader()
    assert reader.connect() is False


def test_reader_applies_deadzone_and_normalizes_triggers(fake_pygame):
    reader = XboxInputReader(deadzone=0.08)
    reader.connect()

    axes = reader.poll_axes()

    assert axes["left_stick_x"] == 0.0  # 0.02 is inside the deadzone
    assert axes["left_stick_y"] == -0.5
    assert axes["left_trigger"] == 0.0  # raw -1.0 -> released
    assert axes["right_trigger"] == 1.0  # raw 1.0 -> fully pressed


def test_reader_is_connected_false_after_disconnect(fake_pygame):
    reader = XboxInputReader()
    reader.connect()
    fake_pygame["count"] = 0
    assert reader.is_connected() is False
