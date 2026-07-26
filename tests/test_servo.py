import pytest

from common.servo import AniServo


class FakeServoHandle:
    def __init__(self):
        self.angle = 90
        self.pulse_width_range = None
        self.actuation_range = None

    def set_pulse_width_range(self, minimum, maximum):
        self.pulse_width_range = (minimum, maximum)


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
