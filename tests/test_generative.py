import io
import os
import sys
import threading
import types
import copy
import time

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
import projects.seagull.config as seagull_config
from common.project import Project
from common.config import WEBSOCKET_MESSAGES
from common.sequence_config import build_timeline
from projects.seagull.config import generative_sequences


@pytest.fixture(autouse=True)
def isolate_optional_sequences(monkeypatch):
    """Ordinary movement tests opt into sequences only when testing them."""
    monkeypatch.setattr(seagull_config, "generative_sequences", {})


def test_seagull_reports_enabled_mine_sequence(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    monkeypatch.setattr(seagull_config, "generative_sequences", generative_sequences)
    project = Project(init_servos=False)
    settings = project.get_sequence_settings()
    assert "mine" in settings
    # Check invariants rather than exact tuning values, so config tweaks don't break tests.
    timing = settings["mine"]["timing"]
    assert 0 < timing["min_beat_interval_ms"] <= timing["max_beat_interval_ms"]
    assert 1 <= timing["min_repeated_beats"] <= timing["max_repeated_beats"]
    servos = settings["mine"]["servos"]
    assert set(servos) <= {"head-pitch", "beak", "wings"}
    assert all(servo["mode"] == "pulse" for servo in servos.values())
    assert all(servo["out_ms"] + servo["back_ms"] <= timing["min_beat_interval_ms"]
               for servo in servos.values())
    assert 0 < settings["mine"]["min_wait_ms"] <= settings["mine"]["max_wait_ms"]
    assert all(os.path.isfile(clip["path"]) for clip in settings["mine"]["audio"]["files"])


@pytest.mark.parametrize("cancel", [False, True])
def test_auto_sequence_pauses_all_controllers_then_resumes_or_cancels(monkeypatch, cancel):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    pitch = MockServo(name="head-pitch")
    beak = MockServo(name="beak")
    yaw = MockServo(name="head-yaw", current=65)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [pitch, beak, yaw])
    config = copy.deepcopy(generative_sequences["mine"])
    config["enabled"] = True
    config["servos"].pop("wings")
    config["restore_ms"] = 10
    config["timing"].update(intro_pause_ms=20, min_beat_interval_ms=50,
                            max_beat_interval_ms=50, final_pause_ms=50,
                            min_repeated_beats=3, max_repeated_beats=3)
    config["servos"]["head-pitch"].update(
        mode="hold", position_2={"reference": "neutral", "fraction": 0.0}
    )
    for settings in config["servos"].values():
        settings.update(transition_ms=0, out_ms=10, back_ms=10)
    controllers = []
    resumed = threading.Event()
    prepared = threading.Event()
    pause_count = []
    sent = []

    class Controller:
        def __init__(self, servo, settings):
            self.servo = servo
            self.calls = 0
            self.start_position = servo.get_current_position()
            controllers.append(self)

        def update(self):
            self.calls += 1
            self.servo.move_to_angle(100)
            if len(controllers) > 2:
                resumed.set()

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    deadlines = iter([time.monotonic() + 0.03, time.monotonic() + 1000])
    monkeypatch.setattr(Project, "_Project__next_sequence_due", staticmethod(
        lambda cfg: next(deadlines)
    ))
    project = Project(init_servos=False)
    project._generative_settings = {"head-yaw": {}, "head-pitch": {}}
    project._sequence_settings = {"mine": config}

    def send(action, data):
        sent.append((action, data))
        if action == WEBSOCKET_MESSAGES["sequence-ready"]:
            pause_count[:] = [controller.calls for controller in controllers]
            prepared.set()
            if not cancel:
                timeline = build_timeline(
                    config, {clip["path"]: 10 for clip in config["audio"]["files"]}
                )
                project.sequence_command(WEBSOCKET_MESSAGES["sequence-arm"],
                                         {"id": data["id"], "timeline": timeline,
                                          "lead_ms": 100})
        elif action == WEBSOCKET_MESSAGES["sequence-complete"]:
            assert [controller.calls for controller in controllers] == pause_count
            assert pitch.get_current_position() == 90
            assert beak.get_current_position() == 90

    project.sequence_sender = send
    try:
        project.auto_start()
        assert prepared.wait(1)
        if cancel:
            threading.Event().wait(0.05)
            assert [controller.calls for controller in controllers] == pause_count
        else:
            assert resumed.wait(2)
            assert controllers[2].start_position == 90
            assert any(action == WEBSOCKET_MESSAGES["sequence-complete"] for action, _ in sent)
    finally:
        project.auto_stop()
    assert all(servo.get_current_position() == 90 for servo in [pitch, beak, yaw])
    if cancel:
        ready_id = next(data["id"] for action, data in sent
                        if action == WEBSOCKET_MESSAGES["sequence-ready"])
        assert sent[-1] == (WEBSOCKET_MESSAGES["sequence-cancel"],
                            {"id": ready_id, "reason": "Auto stopped"})


@pytest.mark.parametrize("failure", ["server-cancel", "bad-schedule"])
def test_failed_sequence_restores_and_auto_keeps_running(monkeypatch, failure):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    pitch = MockServo(name="head-pitch")
    beak = MockServo(name="beak")
    yaw = MockServo(name="head-yaw", current=65)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [pitch, beak, yaw])
    config = copy.deepcopy(generative_sequences["mine"])
    config["servos"].pop("wings")
    config["restore_ms"] = 10
    for settings in config["servos"].values():
        settings.update(transition_ms=0)
    controllers = []
    resumed = threading.Event()
    sent = []

    class Controller:
        def __init__(self, servo, settings):
            controllers.append(self)

        def update(self):
            if len(controllers) > 1:
                resumed.set()

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    deadlines = iter([time.monotonic() + 0.03, time.monotonic() + 1000])
    monkeypatch.setattr(Project, "_Project__next_sequence_due", staticmethod(
        lambda cfg: next(deadlines)
    ))
    project = Project(init_servos=False)
    project._generative_settings = {"head-yaw": {}}
    project._sequence_settings = {"mine": config}

    def send(action, data):
        sent.append((action, data))
        if action != WEBSOCKET_MESSAGES["sequence-ready"]:
            return
        if failure == "server-cancel":
            project.sequence_command(WEBSOCKET_MESSAGES["sequence-cancel"],
                                     {"id": data["id"], "reason": "TimeoutError"})
        else:
            project.sequence_command(WEBSOCKET_MESSAGES["sequence-arm"],
                                     {"id": data["id"], "timeline": {}, "lead_ms": 100})

    project.sequence_sender = send
    try:
        project.auto_start()
        assert resumed.wait(2)
        assert project._Project__auto_thread.is_alive()
        assert pitch.get_current_position() == 90
        assert beak.get_current_position() == 90
    finally:
        project.auto_stop()
    actions = [action for action, _ in sent]
    assert WEBSOCKET_MESSAGES["sequence-complete"] not in actions
    if failure == "bad-schedule":
        assert actions[-1] == WEBSOCKET_MESSAGES["sequence-cancel"]
    else:
        assert WEBSOCKET_MESSAGES["sequence-cancel"] not in actions


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

    def move_to_calibration_angle(self, angle):
        self._current = angle
        self.history.append(("calibration", angle))

    def set_calibration(self, min_val, max_val, rest_position):
        self._min_limit = min_val
        self._max_limit = max_val
        self._rest = rest_position

    def to_calibration_dict(self):
        return {"min": self._min_limit, "max": self._max_limit, "rest": self._rest}

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

    clock = [0.0]
    monkeypatch.setattr(generative_module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(generative_module.random, "uniform", lambda a, b: 0.1)
    monkeypatch.setattr(generative_module.random, "randint", lambda a, b: a)

    controller = generative_module.GenerativeMovement(servo, config)

    clock[0] = 0.2
    controller.update()
    clock[0] = 0.4
    controller.update()
    assert servo.get_current_position() == 40
    assert controller._state == "moving_rest"
    clock[0] = 0.45
    controller.update()
    assert servo.get_current_position() == pytest.approx(
        40 + 50 * generative_module.AniServo.apply_easing(0.5)
    )
    clock[0] = 0.6
    controller.update()

    assert 40 in servo.history
    assert servo.get_current_position() == 90


def test_generative_movement_uses_default_bounds_when_no_config(monkeypatch):
    servo = MockServo(current=90)
    monkeypatch.setattr(generative_module.time, "monotonic", lambda: 0.0)
    monkeypatch.setattr(generative_module.random, "uniform", lambda a, b: 0.1)
    monkeypatch.setattr(generative_module.random, "randint", lambda a, b: 120)

    controller = generative_module.GenerativeMovement(servo)
    controller.update()

    assert servo.get_current_position() == 90


@pytest.mark.parametrize(
    ("minimum_fraction", "maximum_fraction", "expected"),
    [(1, 1, (20, 160)), (0, 0, (80, 80)), (0.5, 0.25, (50, 100)),
     (0, 1, (80, 160)), (1, 0, (20, 80))],
)
def test_generative_limits_are_relative_to_neutral(minimum_fraction, maximum_fraction, expected):
    controller = generative_module.GenerativeMovement(
        MockServo(rest=80),
        {"min_range_fraction": minimum_fraction, "max_range_fraction": maximum_fraction},
    )
    assert controller._get_angle_bounds() == expected


@pytest.mark.parametrize("key", ["min_range_fraction", "max_range_fraction"])
@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf"), None, True, "0.5"])
def test_generative_rejects_invalid_range_fractions(key, value):
    with pytest.raises(ValueError, match=key):
        generative_module.GenerativeMovement(MockServo(), {key: value})


def test_zero_range_targets_neutral_not_current_position():
    controller = generative_module.GenerativeMovement(
        MockServo(rest=80, current=120),
        {"min_range_fraction": 0, "max_range_fraction": 0},
    )
    assert controller._choose_target() == 80


def test_fraction_limits_intersect_angle_overrides():
    controller = generative_module.GenerativeMovement(
        MockServo(rest=80),
        {"min_range_fraction": 0.5, "max_range_fraction": 0.25,
         "min_angle": 60, "max_angle": 150},
    )
    assert controller._get_angle_bounds() == (60, 100)


def test_invalid_neutral_and_nonintersecting_overrides_are_rejected():
    with pytest.raises(ValueError, match="neutral position"):
        generative_module.GenerativeMovement(MockServo(rest=10))
    with pytest.raises(ValueError, match="do not intersect"):
        generative_module.GenerativeMovement(MockServo(), {"min_angle": 170})


def test_auto_failure_returns_to_neutral_and_is_not_acknowledged_as_success(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    servo = MockServo(name="wings", rest=80, current=120)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [servo])
    updated = threading.Event()

    class Controller:
        def __init__(self, controlled_servo, config):
            return None

        def update(self):
            updated.set()
            raise OSError("hardware unavailable")

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    project = Project(init_servos=False)
    project._generative_settings = {"wings": {}}
    project.auto_start()
    assert updated.wait(1)
    with pytest.raises(OSError, match="hardware unavailable"):
        project.auto_stop()
    assert servo.get_current_position() == 80


def test_standby_attempts_all_servos_even_if_one_fails(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    bad = MockServo(name="bad")
    good = MockServo(name="good", rest=80, current=120)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [bad, good])

    def fail_sleep():
        raise OSError("servo disconnected")

    monkeypatch.setattr(bad, "sleep", fail_sleep)
    project = Project(init_servos=False)
    with pytest.raises(OSError, match="servo disconnected"):
        project.standby()
    assert good.get_current_position() == 80


@pytest.mark.parametrize("fails", [False, True])
def test_animation_returns_to_neutral_on_completion_and_failure(monkeypatch, fails):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    servo = MockServo(name="wings", rest=80, current=120)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [servo])

    class Animation:
        def __init__(self, data):
            return None

        def start(self):
            if fails:
                raise RuntimeError("animation failed")

        def in_progress(self):
            return False

        def end(self):
            return None

    monkeypatch.setattr(project_module, "Animation", Animation)
    project = Project(init_servos=False)
    project._Project__animation_data = {"dummy": True}
    if fails:
        with pytest.raises(RuntimeError, match="animation failed"):
            project.play()
    else:
        project.play()
    assert servo.get_current_position() == 80


def test_xbox_stop_returns_to_neutral_and_calibration_only_moves_selected_servo(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    monkeypatch.setattr(project_module, "save_calibration", lambda *args: None)
    wings = MockServo(name="wings", pin=2, rest=80, current=120)
    beak = MockServo(name="beak", pin=3, rest=75, current=100)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [wings, beak])
    project = Project(init_servos=False)
    project.calibrate_neutral(2)
    assert wings.get_current_position() == 80
    assert beak.get_current_position() == 100
    project.calibrate_move(2, 30)
    project.calibrate_save(2, 80, 30, 150)
    project.calibrate_commit()
    assert wings.get_current_position() == 30
    project.xbox_stop()
    assert wings.get_current_position() == 80
    assert beak.get_current_position() == 75


@pytest.mark.parametrize("wings_config", [{}, {"min_wait_ms": 400}])
def test_project_auto_start_only_moves_configured_servos(monkeypatch, wings_config):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    wings = MockServo(name="wings")
    beak = MockServo(name="beak", rest=75, current=120)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [wings, beak])
    controllers = []
    updated = threading.Event()

    class FakeKit:
        def __init__(self, channels=16):
            self.channels = channels

    class FakeController:
        def __init__(self, servo, config=None):
            self.servo = servo
            self.config = config
            self.calls = 0
            controllers.append(self)

        def update(self):
            self.calls += 1
            self.servo.move_to_angle(100)
            if self.calls == 3:
                updated.set()

    monkeypatch.setattr(project_module, "ServoKit", FakeKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)
    monkeypatch.setattr(project_module, "GenerativeMovement", FakeController)

    project = Project(init_servos=False)
    project._generative_settings = {"wings": wings_config}
    try:
        project.auto_start()
        assert updated.wait(1)
    finally:
        project.auto_stop()

    assert len(controllers) == 1
    assert controllers[0].servo is wings
    assert controllers[0].config == wings_config
    assert controllers[0].calls >= 3
    assert wings.history == [100] * controllers[0].calls
    assert beak.get_current_position() == 75


def test_project_auto_start_without_settings_keeps_all_servos_at_rest(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    servo = MockServo(rest=80, current=120)
    monkeypatch.setitem(project_module.servos_data_object, "skeleton", [servo])

    def fail_controller(*args, **kwargs):
        pytest.fail("Unconfigured servos must not receive generative controllers")

    monkeypatch.setattr(project_module, "GenerativeMovement", fail_controller)
    project = Project(init_servos=False)
    project._generative_settings = {}
    try:
        project.auto_start()
    finally:
        project.auto_stop()

    assert servo.get_current_position() == 80


def test_auto_worker_duplicate_start_restart_and_standby(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    servo = MockServo(name="wings", rest=80)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [servo])
    controllers = []
    updated = threading.Event()

    class Controller:
        def __init__(self, controlled_servo, config):
            controllers.append(self)
            self.servo = controlled_servo

        def update(self):
            self.servo.move_to_angle(100)
            updated.set()

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    project = Project(init_servos=False)
    project._generative_settings = {"wings": {}}
    try:
        project.auto_stop()  # Safe even before starting.
        project.auto_start()
        assert updated.wait(1)
        first_worker = project._Project__auto_thread
        project.auto_start()
        assert project._Project__auto_thread is first_worker
        assert len(controllers) == 1
        project.auto_stop()
        assert not first_worker.is_alive()
        assert servo.get_current_position() == 80
        project.auto_stop()  # Repeated stop is also safe.

        updated.clear()
        project.auto_start()
        assert updated.wait(1)
        assert len(controllers) == 2
        second_worker = project._Project__auto_thread
        project.standby()
        assert not second_worker.is_alive()
        assert servo.get_current_position() == 80
        count_after_standby = len(servo.history)
        threading.Event().wait(0.05)
        assert len(servo.history) == count_after_standby
    finally:
        project.auto_stop()


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
    project.calibrate_move(0, 120)
    project.standby()
    project.auto_stop()

    assert project._Project__auto_stop_event.is_set()


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


def test_load_animation_missing_file_disables_animation_capability(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    def fake_open(path, encoding=None):
        raise FileNotFoundError(path)

    monkeypatch.setattr("builtins.open", fake_open)

    project = Project(init_servos=False)
    project.load_animation("animation")  # should not raise

    assert project._Project__animation_data is None
    assert project.get_capabilities()["animation"] is False


def test_get_capabilities_reflects_project_config(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    project = Project(init_servos=False)
    project._Project__animation_data = {"dummy": True}

    # skeleton's config.py defines xbox_settings but no generative_settings.
    capabilities = project.get_capabilities()
    assert capabilities["animation"] is True
    assert capabilities["generative"] is False
    assert capabilities["xbox"] is True


def test_get_capabilities_calibrated_false_without_saved_calibration(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)
    monkeypatch.setattr(project_module, "has_calibration", lambda project_id: False)

    project = Project(init_servos=False)

    assert project.get_capabilities()["calibrated"] is False


def test_play_and_evaluate_are_no_ops_without_animation(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    project = Project(init_servos=False)
    project._Project__animation_data = None

    # Should not raise even though there's no animation data to build an Animation from.
    project.play()
    project.evaluate()


def test_get_servo_summary_reports_name_pin_and_calibration(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    project = Project(init_servos=False)
    project._Project__servos_data = [
        MockServo(name="servo-a", pin=3, min_limit=10, max_limit=170, rest=90)
    ]

    summary = project.get_servo_summary()
    assert summary == [{"name": "servo-a", "pin": 3, "min": 10, "max": 170, "rest": 90}]


def test_calibrate_move_bypasses_configured_limits(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    project = Project(init_servos=False)
    servo = MockServo(name="servo-a", pin=3, current=90)
    project._Project__servos_data = [servo]

    project.calibrate_move(3, 5)
    assert servo.get_current_position() == 5
    assert ("calibration", 5) in servo.history


def test_calibrate_save_stages_pending_calibration(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    project = Project(init_servos=False)
    servo = MockServo(name="servo-a", pin=3)
    project._Project__servos_data = [servo]

    project.calibrate_save(3, neutral=95, min_val=20, max_val=150)

    assert servo.to_calibration_dict() == {"min": 20, "max": 150, "rest": 95}
    assert project._Project__pending_calibration == {
        "servo-a": {"min": 20, "max": 150, "rest": 95}
    }


def test_calibrate_commit_persists_and_clears_pending(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    saved = {}
    monkeypatch.setattr(
        project_module, "save_calibration", lambda project_id, data: saved.update({project_id: data})
    )

    project = Project(init_servos=False)
    project._Project__pending_calibration = {"servo-a": {"min": 20, "max": 150, "rest": 95}}

    project.calibrate_commit()

    assert saved == {"skeleton": {"servo-a": {"min": 20, "max": 150, "rest": 95}}}
    assert project._Project__pending_calibration == {}


def test_calibrate_commit_is_no_op_without_pending_changes(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "skeleton")
    monkeypatch.setattr(project_module, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_module, "ServoKit", FakeServoKit)
    monkeypatch.setattr(project_module, "initialize_servos", lambda kit, servos: None)

    calls = []
    monkeypatch.setattr(project_module, "save_calibration", lambda *args, **kwargs: calls.append("save"))

    project = Project(init_servos=False)
    project.calibrate_commit()

    assert calls == []
