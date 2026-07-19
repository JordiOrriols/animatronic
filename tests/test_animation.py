import pytest

from common.animation import Animation


@pytest.mark.parametrize(
    ("data", "expected_frames"),
    [
        ({"fps": 2, "frames": 3, "positions": {"head": [0, 10, 20]}}, 3),
        ({"fps": 4, "frames": 4, "positions": {"head": [5, 15, 25, 35]}}, 4),
    ],
)
def test_animation_initializes_from_data(monkeypatch, data, expected_frames):
    animation = Animation(data)
    assert animation.get_positions() == data["positions"]
    assert animation.in_progress() is False

    times = iter([100.0, 100.0, 100.5, 100.5, 101.0, 101.0])
    monkeypatch.setattr("common.animation.time.time", lambda: next(times))

    animation.start()
    animation.refresh()
    assert animation.in_progress() is True

    class FakeServo:
        def get_name(self):
            return "head"

    position = animation.get_current_position(FakeServo())
    assert isinstance(position, (int, float))
    assert position >= 0

    animation.end()
    assert animation.in_progress() is False
