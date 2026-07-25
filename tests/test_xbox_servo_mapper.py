from common.xbox_servo_mapper import XboxServoMapper


class MockServo:
    def __init__(self, name="servo", rest=90, current=90, min_limit=20, max_limit=160):
        self._name = name
        self._rest = rest
        self._current = current
        self._min_limit = min_limit
        self._max_limit = max_limit
        self.history = []

    def get_name(self):
        return self._name

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


def test_mapper_maps_centered_stick_to_midpoint():
    servo = MockServo(current=20, min_limit=20, max_limit=160)
    mapper = XboxServoMapper([servo], {"servo": {"input": "left_stick_x", "smoothing": 1.0}})

    mapper.update({"left_stick_x": 0.0})

    assert servo.get_current_position() == 90


def test_mapper_maps_full_deflection_to_bounds():
    servo = MockServo(current=90, min_limit=20, max_limit=160)
    mapper = XboxServoMapper([servo], {"servo": {"input": "left_stick_x", "smoothing": 1.0}})

    mapper.update({"left_stick_x": 1.0})
    assert servo.get_current_position() == 160

    mapper.update({"left_stick_x": -1.0})
    assert servo.get_current_position() == 20


def test_mapper_respects_invert_and_custom_bounds():
    servo = MockServo(current=90, min_limit=0, max_limit=180)
    mapper = XboxServoMapper(
        [servo],
        {"servo": {"input": "left_stick_y", "invert": True, "min_angle": 40, "max_angle": 70, "smoothing": 1.0}},
    )

    mapper.update({"left_stick_y": 1.0})
    assert servo.get_current_position() == 40

    mapper.update({"left_stick_y": -1.0})
    assert servo.get_current_position() == 70


def test_mapper_trigger_input_uses_0_to_1_range():
    servo = MockServo(current=45, min_limit=40, max_limit=70)
    mapper = XboxServoMapper([servo], {"servo": {"input": "right_trigger", "smoothing": 1.0}})

    mapper.update({"right_trigger": 0.0})
    assert servo.get_current_position() == 40

    mapper.update({"right_trigger": 1.0})
    assert servo.get_current_position() == 70


def test_mapper_smoothing_eases_towards_target_gradually():
    servo = MockServo(current=0, min_limit=0, max_limit=100)
    mapper = XboxServoMapper([servo], {"servo": {"input": "left_stick_x", "smoothing": 0.5}})

    # Target for stick=1.0 is 100 (full deflection maps to max_limit).
    mapper.update({"left_stick_x": 1.0})
    first = servo.get_current_position()
    mapper.update({"left_stick_x": 1.0})
    second = servo.get_current_position()

    assert 0 < first < second <= 100


def test_mapper_ignores_unmapped_servos_and_missing_axes():
    servo = MockServo(name="unmapped", current=90)
    mapper = XboxServoMapper([servo], {})
    mapper.update({"left_stick_x": 1.0})
    assert servo.get_current_position() == 90

    servo2 = MockServo(name="mapped", current=90)
    mapper2 = XboxServoMapper([servo2], {"mapped": {"input": "left_stick_x"}})
    mapper2.update({"right_stick_y": 1.0})  # different axis, no update expected
    assert servo2.get_current_position() == 90


def test_mapper_reset_reseeds_current_position():
    servo = MockServo(current=30, min_limit=0, max_limit=180)
    mapper = XboxServoMapper([servo], {"servo": {"input": "left_stick_x", "smoothing": 0.1}})

    servo.move_to_angle(150)  # simulate external movement
    mapper.reset()
    mapper.update({"left_stick_x": -1.0})  # target = 0

    # With a small smoothing factor starting from the reset value (150), the first
    # update should move only slightly away from 150, not from the stale seed (30).
    assert servo.get_current_position() < 150
    assert servo.get_current_position() > 100
