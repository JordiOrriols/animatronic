import asyncio
import copy
import sys
import threading
import types

import pytest

from common.config import WEBSOCKET_MESSAGES
from common.sequence import ServoSequence
from common.servo import AniServo
from common.sequence_config import build_timeline, validate_sequence
from common.sequence_audio import SequenceAudio
from projects.seagull.config import generative_sequences


def test_sequence_return_annotation_supports_python_before_310():
    from typing import Optional

    assert ServoSequence.update.__annotations__["return"] == Optional[str]


@pytest.fixture(name="config")
def sequence_config():
    result = copy.deepcopy(generative_sequences["mine"])
    result["timing"] = {
        "intro_pause_ms": 2000, "beat_interval_ms": 500,
        "min_repeated_beats": 3, "max_repeated_beats": 6, "final_pause_ms": 500,
    }
    result["servos"] = {
        "head-pitch": {
            "mode": "hold", "position_1": {"reference": "max", "fraction": 1.0},
            "position_2": {"reference": "neutral", "fraction": 0.0}, "transition_ms": 600,
        },
        "beak": {
            "mode": "pulse", "position_1": {"reference": "neutral", "fraction": 0.0},
            "position_2": {"reference": "max", "fraction": 0.8},
            "transition_ms": 600, "out_ms": 100, "back_ms": 200,
        },
    }
    result["audio"]["files"] = [
        {"path": "sound/seagull/a.mp3", "animation_offset_ms": 100},
        {"path": "sound/seagull/b.mp3", "animation_offset_ms": -80},
    ]
    return result


class Servo(AniServo):
    def __init__(self, name, current=90):
        super().__init__(name, 0, "MG90S", 20, 160, 90)
        self.name = name
        self.current = current
        self.history = []

    def get_name(self):
        return self.name

    def get_rest_position(self):
        return 90

    def get_physical_limit_min(self):
        return 20

    def get_physical_limit_max(self):
        return 160

    def get_current_position(self):
        return self.current

    def move_to_angle(self, angle):
        self.current = angle
        self.history.append(angle)


def test_random_timeline_count_spacing_offsets_and_intro_pause(config, monkeypatch):
    monkeypatch.setattr("common.sequence_config.random.randint", lambda a, b: 4)
    choices = iter(config["audio"]["files"] * 3)
    monkeypatch.setattr("common.sequence_config.random.choice", lambda files: next(choices))
    timeline = build_timeline(config, {"sound/seagull/a.mp3": 200, "sound/seagull/b.mp3": 250})
    beats = timeline["beats"]
    assert len(beats) == 6
    assert [beat["movement_ms"] - beat["audio_ms"] for beat in beats] == [100, -80] * 3
    assert min(beat["movement_ms"] for beat in beats) >= 0
    assert beats[1]["audio_ms"] - (beats[0]["movement_ms"] + 300) >= 2000
    assert [b["audio_ms"] - a["audio_ms"] for a, b in zip(beats[1:], beats[2:])] == [500] * 4
    assert timeline["end_ms"] >= beats[-1]["movement_ms"] + 300


def test_beat_intervals_are_random_within_configured_range(config):
    config["timing"] = {"intro_pause_ms": 100, "min_beat_interval_ms": 350,
                        "max_beat_interval_ms": 800, "min_repeated_beats": 6,
                        "max_repeated_beats": 6, "final_pause_ms": 500}
    config["audio"]["files"] = [{"path": "sound/seagull/a.mp3", "animation_offset_ms": 0}]
    gaps = set()
    for _ in range(20):
        beats = build_timeline(config, {"sound/seagull/a.mp3": 900})["beats"]
        rhythm = [b["audio_ms"] - a["audio_ms"] for a, b in zip(beats[1:-1], beats[2:-1])]
        assert len(rhythm) == 5
        assert all(350 <= gap <= 800 for gap in rhythm)
        gaps.update(round(gap) for gap in rhythm)
    assert len(gaps) > 1


def test_beat_interval_range_is_validated(config):
    config["timing"].pop("beat_interval_ms")
    config["timing"].update(min_beat_interval_ms=800, max_beat_interval_ms=350)
    with pytest.raises(ValueError, match="exceeds"):
        validate_sequence(config)
    config["timing"].update(max_beat_interval_ms=900, beat_interval_ms=500)
    with pytest.raises(ValueError, match="not both"):
        validate_sequence(config)
    config["timing"].pop("beat_interval_ms")
    config["timing"]["min_beat_interval_ms"] = 250
    with pytest.raises(ValueError, match="overlap"):
        validate_sequence(config)


def test_sequence_holds_head_pulses_beak_preserves_yaw_and_restores(config):
    pitch, beak, yaw = Servo("head-pitch", 100), Servo("beak", 110), Servo("head-yaw", 65)
    sequence = ServoSequence(config, [pitch, beak, yaw], 0)
    assert sequence.update(0.6) == "ready"
    assert pitch.current == 160
    assert beak.current == 90
    sequence.arm({"beats": [{"movement_ms": 0}], "end_ms": 500}, 1, 500)
    sequence.update(1.55)
    assert 90 < beak.current < 146
    assert pitch.current == 160
    sequence.update(1.8)
    assert beak.current == pytest.approx(90)
    sequence.update(2)
    assert sequence.phase == "restoring"
    assert sequence.update(2.7) == "complete"
    assert pitch.current == 90
    assert beak.current == 110
    assert yaw.current == 65
    assert yaw.history == []


@pytest.mark.parametrize("field,value", [
    ("beat_interval_ms", 0), ("min_repeated_beats", 2.5),
    ("max_repeated_beats", 1), ("intro_pause_ms", float("nan")),
])
def test_invalid_timing_is_rejected(config, field, value):
    config["timing"][field] = value
    with pytest.raises(ValueError):
        validate_sequence(config)


def test_overlapping_offsets_unknown_servos_and_invalid_fraction_fail(config):
    config["audio"]["files"][0]["animation_offset_ms"] = 300
    with pytest.raises(ValueError, match="overlap"):
        validate_sequence(config)
    config["audio"]["files"][0]["animation_offset_ms"] = 100
    with pytest.raises(ValueError, match="Unknown"):
        ServoSequence(config, [Servo("beak")], 0)
    config["servos"]["beak"]["position_2"]["fraction"] = 1.2
    with pytest.raises(ValueError, match="fraction"):
        validate_sequence(config)


def test_schedule_timeout_and_overlap_are_explicit(config):
    sequence = ServoSequence(config, [Servo("head-pitch"), Servo("beak")], 0)
    sequence.update(1)
    with pytest.raises(TimeoutError):
        sequence.update(12)
    with pytest.raises(ValueError, match="overlap"):
        sequence.arm({"beats": [{"movement_ms": 0}, {"movement_ms": 200}],
                      "end_ms": 1000}, 1, 500)


async def wait_until(condition, timeout=5.0):
    """Poll instead of sleeping a fixed time so slow CI runners do not flake."""
    deadline = asyncio.get_running_loop().time() + timeout
    while not condition():
        assert asyncio.get_running_loop().time() < deadline, "condition not met in time"
        await asyncio.sleep(0.01)


def test_audio_waits_for_ack_plays_on_server_and_cancels(config, monkeypatch):
    played = []

    class Channel:
        def get_busy(self):
            return False

        def play(self, sound):
            played.append(sound)

        def stop(self):
            played.append("stop")

    async def exercise():
        sent = []
        async def send(action, data):
            sent.append((action, data))
        audio = SequenceAudio(send)
        audio.configure({"mine": config})
        audio.channel = Channel()
        monkeypatch.setitem(sys.modules, "pygame", types.SimpleNamespace(error=RuntimeError))
        audio.sounds = {"sound/seagull/a.mp3": "a", "sound/seagull/b.mp3": "b"}

        def slow_load(cfg):
            # Simulate a slow CI worker thread; the test must not rely on fixed sleeps.
            threading.Event().wait(0.1)
            return {key: 100 for key in audio.sounds}
        monkeypatch.setattr(audio, "_load", slow_load)
        monkeypatch.setattr("common.sequence_audio.build_timeline", lambda *args: {
            "beats": [{"path": "sound/seagull/a.mp3", "audio_ms": 0, "movement_ms": 0}],
            "end_ms": 1000,
        })
        await audio.ready({"id": "one", "name": "mine"})
        await wait_until(lambda: sent)
        assert sent[0][0] == WEBSOCKET_MESSAGES["sequence-arm"]
        assert "a" not in played
        audio.acknowledge({"id": "stale"})
        assert not audio.armed.is_set()
        audio.acknowledge({"id": "one"})
        await wait_until(lambda: "a" in played)
        await audio.stop({"id": "stale"})
        assert audio.active_id == "one"
        await audio.stop()
        assert played[-1] == "stop"
        assert audio.task is None
    asyncio.run(exercise())


def test_audio_failure_sends_cancel_not_success(config, monkeypatch):
    async def exercise():
        sent = []
        async def send(action, data):
            sent.append((action, data))
        audio = SequenceAudio(send)
        audio.configure({"mine": config})
        def missing(cfg):
            raise ValueError("Missing audio file")
        monkeypatch.setattr(audio, "_load", missing)
        await audio.ready({"id": "one", "name": "mine"})
        assert audio.task is not None
        await audio.task
        assert sent == [(WEBSOCKET_MESSAGES["sequence-cancel"],
                         {"id": "one", "reason": "ValueError: Missing audio file"})]
        await audio.stop()
    asyncio.run(exercise())


@pytest.mark.parametrize("error", [AttributeError("mixer"), "hang"])
def test_unexpected_or_hung_audio_load_still_cancels(config, monkeypatch, error):
    monkeypatch.setattr("common.sequence_audio.LOAD_TIMEOUT_S", 0.1)

    async def exercise():
        sent = []
        async def send(action, data):
            sent.append((action, data))
        audio = SequenceAudio(send)
        audio.configure({"mine": config})
        def load(cfg):
            if error == "hang":
                threading.Event().wait(0.5)
            else:
                raise error
        monkeypatch.setattr(audio, "_load", load)
        await audio.ready({"id": "one", "name": "mine"})
        await audio.task
        assert sent[0][0] == WEBSOCKET_MESSAGES["sequence-cancel"]
        assert sent[0][1]["reason"].startswith(
            "TimeoutError" if error == "hang" else "AttributeError"
        )
        assert audio.active_id is None
        await audio.stop()
    asyncio.run(exercise())


def test_long_audio_clips_overlap_without_changing_beat_spacing(config):
    timeline = build_timeline(config, {clip["path"]: 984 for clip in config["audio"]["files"]})
    beats = timeline["beats"]
    assert all(b["audio_ms"] - a["audio_ms"] == 500
               for a, b in zip(beats[1:], beats[2:]))
    assert timeline["end_ms"] >= beats[-1]["audio_ms"] + 984


def test_server_audio_loads_clips_and_allocates_isolated_channels(config, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    directory = tmp_path / "sound" / "seagull"
    directory.mkdir(parents=True)
    for clip in config["audio"]["files"]:
        (tmp_path / clip["path"]).write_bytes(b"test audio placeholder")
    channels = {}
    count = [1]

    class Channel:
        def __init__(self):
            self.busy = False
            self.played = []
            self.stops = 0

        def get_busy(self):
            return self.busy

        def play(self, sound):
            self.busy = True
            self.played.append(sound)

        def stop(self):
            self.busy = False
            self.stops += 1

    class Sound:
        def __init__(self, path):
            self.path = path

        def get_length(self):
            return 0.25

    class DecodeError(Exception):
        pass

    def channel(index):
        if index not in channels:
            channels[index] = Channel()
        return channels[index]

    pygame = types.SimpleNamespace(
        error=DecodeError,
        mixer=types.SimpleNamespace(
            get_init=lambda: True, get_num_channels=lambda: count[0],
            set_num_channels=lambda value: count.__setitem__(0, value),
            Channel=channel, Sound=Sound,
        ),
    )
    monkeypatch.setitem(sys.modules, "pygame", pygame)

    async def send(*args):
        return None

    first, second = SequenceAudio(send), SequenceAudio(send)
    try:
        lengths = first._load(config)
        second._load(config)
        assert set(lengths.values()) == {250}
        assert first.channel is not second.channel
        assert first.channel_index != second.channel_index
        sound = first.sounds[config["audio"]["files"][0]["path"]]
        first._play(sound)
        first._play(sound)
        assert first.channel.stops == 0
        assert len(first.extra_channels) == 1
        overlapping = next(iter(first.extra_channels.values()))
        assert overlapping.get_busy()
        assert second.channel.played == []
        first.channel.busy = False
        first._play(sound)
        assert len(first.extra_channels) == 1
        assert len(first.channel.played) == 2
        asyncio.run(first.stop())
        assert not overlapping.get_busy()
        assert not first.channel.get_busy()
        missing = copy.deepcopy(config)
        missing["audio"]["files"][0]["path"] = "sound/seagull/missing.mp3"
        with pytest.raises(ValueError, match="missing"):
            first._load(missing)
    finally:
        asyncio.run(first.close())
        asyncio.run(second.close())
    assert SequenceAudio._channel_indices == set()
