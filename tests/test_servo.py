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
    [(200, 180), (0, 0), (90, 90)],
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
