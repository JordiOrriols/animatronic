import io
import os
import sys
import types

import pytest

# Provide a lightweight ServoKit stub before importing the project modules.
fake_servokit = types.ModuleType("adafruit_servokit")


class FakeServoKit:
    def __init__(self, channels=16):
        self.channels = channels


fake_servokit.ServoKit = FakeServoKit
sys.modules.setdefault("adafruit_servokit", fake_servokit)
sys.modules.setdefault("board", types.ModuleType("board"))

import common.generative as generative_module
import common.project as project_module
from common.project import Project


class MockServo:
    def __init__(self, name="servo", rest=90, current=90, min_limit=20, max_limit=160, pin=0):
        self._name = name
        self._rest = rest
        self._current = current
        self._min_limit = min_limit
        self._max_limit = max_limit
        self._pin = pin
        self.history = []

    def get_name(self):
        return self._name

    def get_pin(self):
        return self._pin

    def get_current_position(self):
        return self._current

    def get_physical_limit_min(self):
        return self._min_limit

    def get_physical_limit_max(self):
        return self._max_limit

    def get_rest_position(self):
        return self._rest

    def move_to_angle(self, angle):
        self._current = angle
        self.history.append(angle)

    def sleep(self):
        self._current = self._rest


def test_generative_movement_moves_and_returns_to_rest(monkeypatch):
    servo = MockServo(current=90)
    config = {
        "min_duration_ms": 100,
        "max_duration_ms": 200,
        "min_wait_ms": 100,
        "max_wait_ms": 200,
        "min_angle": 40,
        "max_angle": 140,
        "random_factor": 1.0,
        "ease_in": 0.2,
        "ease_out": 0.2,
        "return_to_rest": True,
        "rest_hold_ms": 50,
    }

    times = iter([0.0, 0.2, 0.3, 0.4])
    monkeypatch.setattr(generative_module.time, "time", lambda: next(times))
    monkeypatch.setattr(generative_module.random, "uniform", lambda a, b: 0.1)
    monkeypatch.setattr(generative_module.random, "randint", lambda a, b: a)

    controller = generative_module.GenerativeMovement(servo, config)

    controller.update()  # start waiting -> moving at t=0.2
    controller.update()  # move to target -> return to rest at t=0.3
    controller.update()  # finish return to rest at t=0.4

    assert 40 in servo.history
    assert servo.get_current_position() == 90


def test_generative_movement_uses_default_bounds_when_no_config(monkeypatch):
    servo = MockServo(current=90)
    monkeypatch.setattr(generative_module.time, "time", lambda: 0.0)
    monkeypatch.setattr(generative_module.random, "uniform", lambda a, b: 0.1)
    monkeypatch.setattr(generative_module.random, "randint", lambda a, b: 120)

    controller = generative_module.GenerativeMovement(servo)
    controller.update()

    assert servo.get_current_position() == 90


def test_project_auto_start_uses_generative_controllers(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)

    class FakeKit:
        def __init__(self, channels=16):
            self.channels = channels

    class FakeController:
        def __init__(self, servo, config=None):
            self.servo = servo
            self.config = config
            self.calls = 0

        def update(self):
            self.calls += 1

    monkeypatch.setattr(project_module, "ServoKit", FakeKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)
    monkeypatch.setattr(project_module, "GenerativeMovement", FakeController)

    def stop_after_first_sleep(*args, **kwargs):
        project._Project__automatic_mode = False

    monkeypatch.setattr(project_module.time, "sleep", stop_after_first_sleep)

    project = Project(init_servos=False)
    project.auto_start()

    assert len(project.get_servos_data()) > 0


def test_project_evaluate_play_calibrate_and_standby(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    class FakeAnimation:
        def __init__(self, data):
            self.data = data
            self._in_progress = True

        def start(self):
            self.started = True

        def in_progress(self):
            if self._in_progress:
                self._in_progress = False
                return True
            return False

        def refresh(self):
            return None

        def end(self):
            self.ended = True

        def get_positions(self):
            return {"servo-a": [0, 90]}

        def get_current_position(self, servo):
            return 90

    monkeypatch.setattr(project_module, "Animation", FakeAnimation)

    project = Project(init_servos=False)
    project._Project__animation_data = {"dummy": True}
    project._Project__servos_data = [
        MockServo(name="servo-a", current=90, min_limit=0, max_limit=180)
    ]

    project.evaluate()
    project.play()
    project.calibrate(0, 120)
    project.standby()
    project.auto_stop()

    assert project._Project__automatic_mode is False


def test_project_validation_failure_and_load_animation(monkeypatch, tmp_path):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    project = Project(init_servos=False)
    project._Project__servos_data = None
    assert project._Project__validate_servos_data() is False

    project._Project__servos_data = [MockServo(name="servo-a", current=90, min_limit=0, max_limit=180)]
    project._Project__animation_data = {"dummy": True}

    def fake_open(path, encoding=None):
        return io.StringIO('{"loaded": true}')

    monkeypatch.setattr("builtins.open", fake_open)
    project.load_animation("dummy")

    assert project._Project__animation_data == {"loaded": True}


def test_project_handles_missing_config(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "missing-project")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    with pytest.raises(KeyError):
        Project(init_servos=False)
