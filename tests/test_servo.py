import pytest
from types import SimpleNamespace

import common.servo as servo_module
from common.servo import AniServo


class FakeServoHandle:
    def __init__(self):
        self._angle = 90
        self.history = []
        self.pulse_width_range = None
        self.actuation_range = None

    def set_pulse_width_range(self, minimum, maximum):
        self.pulse_width_range = (minimum, maximum)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, position):
        self._angle = position
        self.history.append(position)


@pytest.fixture(autouse=True)
def fast_movement_clock(monkeypatch):
    clock = [0.0]

    def advance(seconds):
        clock[0] += seconds

    monkeypatch.setattr(
        servo_module, "time", SimpleNamespace(monotonic=lambda: clock[0], sleep=advance)
    )
    return clock

class FakeServoKit:
    def __init__(self):
        self.servo = [FakeServoHandle() for _ in range(16)]


@pytest.mark.parametrize(
    ("position", "expected"),
    [(200, 180), (0, 10), (90, 90)],
)
def test_ani_servo_clamps_positions(position, expected):
    servo = AniServo("head", 1, "MG90S", 10, 200, 90)
    kit = FakeServoKit()
    servo.start(kit)
    servo.move_to_angle(position)
    assert kit.servo[1].angle == expected


def test_ani_servo_connects_and_sleeps():
    servo = AniServo("head", 1, "MG90S", 10, 200, 90)
    partner = AniServo("partner", 2, "MG90S", 10, 200, 90)
    servo.connect(partner, "inverted")

    kit = FakeServoKit()
    servo.start(kit)
    servo.move_to_angle(60)

    assert kit.servo[1].angle == 60
    assert kit.servo[2].angle == 120

    servo.sleep()
    assert kit.servo[1].angle == 90


def test_move_to_calibration_angle_bypasses_configured_limits():
    servo = AniServo("head", 1, "MG90S", 50, 120, 90)
    kit = FakeServoKit()
    servo.start(kit)

    servo.move_to_calibration_angle(10)
    assert kit.servo[1].angle == 10

    servo.move_to_calibration_angle(-20)
    assert kit.servo[1].angle == 0

    servo.move_to_calibration_angle(999)
    assert kit.servo[1].angle == 180


def test_set_calibration_updates_limits_and_rest():
    servo = AniServo("head", 1, "MG90S", 10, 200, 90)
    kit = FakeServoKit()
    servo.start(kit)

    servo.set_calibration(30, 150, 60)

    assert servo.get_physical_limit_min() == 30
    assert servo.get_physical_limit_max() == 150
    assert servo.get_rest_position() == 60

    servo.move_to_angle(0)
    assert kit.servo[1].angle == 30


def test_to_calibration_dict_reflects_current_state():
    servo = AniServo("head", 1, "MG90S", 10, 200, 90)
    assert servo.to_calibration_dict() == {"min": 10, "max": 180, "rest": 90}

    servo.set_calibration(20, 150, 60)
    assert servo.to_calibration_dict() == {"min": 20, "max": 150, "rest": 60}


def test_sleep_eases_from_current_angle_for_default_duration(fast_movement_clock):
    servo = AniServo("head", 1, "MG90S", 10, 180, 90)
    kit = FakeServoKit()
    servo.start(kit)
    servo.move_to_angle(30)
    kit.servo[1].history.clear()
    began = fast_movement_clock[0]

    servo.sleep()

    positions = kit.servo[1].history
    assert positions[0] == 30
    assert positions[-1] == 90
    assert len(positions) > 50
    assert fast_movement_clock[0] - began == pytest.approx(1.0)
    assert positions[1] - positions[0] < positions[len(positions) // 2] - positions[len(positions) // 2 - 1]


def test_sleep_from_calibration_angle_does_not_jump_to_new_limits():
    servo = AniServo("head", 1, "MG90S", 50, 120, 90)
    kit = FakeServoKit()
    servo.start(kit)
    servo.move_to_calibration_angle(20)
    kit.servo[1].history.clear()
    servo.sleep()

    history = kit.servo[1].history
    assert history[0] == 20
    assert history[-1] == 90
    assert history[2] < 50  # No jump to the calibrated minimum.


def test_unknown_current_angle_logs_unknown_startup(capsys):
    servo = AniServo("head", 1, "MG90S", 10, 180, 90)
    kit = FakeServoKit()
    kit.servo[1]._angle = None
    servo.start(kit)
    assert kit.servo[1].angle == 90
    assert "cannot ease the initial movement command" in capsys.readouterr().out


def test_eased_move_updates_linked_servos_and_clamps_target():
    servo = AniServo("head", 1, "MG90S", 10, 170, 90)
    partner = AniServo("partner", 2, "MG90S", 10, 170, 90)
    servo.connect(partner, "inverted")
    kit = FakeServoKit()
    servo.start(kit)
    servo.move_to_angle_eased(200, duration_ms=200)
    assert kit.servo[1].angle == 170
    assert kit.servo[2].angle == 10
    assert len(kit.servo[1].history) > 5


def test_project_returns_to_neutral_without_creating_position_files(tmp_path, monkeypatch):
    import common.project as project_module

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    servo = AniServo("wings", 2, "MG90S", 10, 180, 90)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", [servo])
    kit = FakeServoKit()
    monkeypatch.setattr(project_module, "ServoKit", lambda channels: kit)

    project = project_module.Project()
    project.get_servos_data()[0].move_to_angle(45)

    assert kit.servo[2].angle == 45
    project.standby()
    assert kit.servo[2].angle == 90
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("duration", [0, 200, 1500])
def test_eased_move_duration_is_independent_of_distance(duration, fast_movement_clock):
    servo = AniServo("head", 1, "MG90S", 10, 170, 90)
    kit = FakeServoKit()
    servo.start(kit)
    began = fast_movement_clock[0]
    servo.move_to_angle_eased(150, duration_ms=duration, ease_in=0.3, ease_out=0.4)
    assert kit.servo[1].angle == 150
    assert fast_movement_clock[0] - began == pytest.approx(duration / 1000, abs=0.02)


@pytest.mark.parametrize("kwargs", [
    {"duration_ms": -1}, {"duration_ms": float("nan")}, {"duration_ms": True},
    {"ease_in": -0.1}, {"ease_out": 1.1}, {"ease_in": float("inf")},
])
def test_eased_move_rejects_invalid_parameters_before_moving(kwargs):
    servo = AniServo("head", 1, "MG90S", 10, 170, 90)
    kit = FakeServoKit()
    servo.start(kit)
    kit.servo[1].history.clear()
    with pytest.raises(ValueError):
        servo.move_to_angle_eased(150, **kwargs)
    assert kit.servo[1].history == []


def test_shared_easing_matches_existing_generative_formula():
    progress = 0.4
    expected = 1 - (1 - progress ** 1.6) ** 1.6
    assert AniServo.apply_easing(progress) == pytest.approx(expected)
    assert AniServo.apply_easing(0) == 0
    assert AniServo.apply_easing(1) == 1
    assert AniServo.apply_easing(progress, 0, 0) == progress
