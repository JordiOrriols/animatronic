import asyncio
import json
import random
import runpy
import sys
import threading
import time
import types

import pytest

import common.project as project_module
import projects.seagull.config as seagull_config
from common.calibration import has_calibration, load_calibration, save_calibration
from common.config import WEBSOCKET_MESSAGES
from common.flock import FlockSequence
from common.project import Project
from common.sequence_audio import SequenceAudio
from common.sequence_config import build_timeline, member_config, validate_sequence
from common.servo import AniServo


class Servo(AniServo):
    def __init__(self, name, pin):
        super().__init__(name, pin, "MG90S", 20, 160, 90)
        self.current = 90
        self.history = []

    def get_current_position(self):
        return self.current

    def move_to_angle(self, position):
        self.current = position
        self.history.append(position)

    def sleep(self):
        self.move_to_angle(self.get_rest_position())


@pytest.fixture
def flock(monkeypatch):
    monkeypatch.setattr(seagull_config, "load_calibration", lambda project: {})
    monkeypatch.setattr(seagull_config, "seagull_voices", {})
    data, idle, sequences, xbox = seagull_config.build_seagull_configuration(3)
    servos = [Servo(servo.get_name(), servo.get_pin()) for servo in data]
    config = sequences["mine"]
    config.update(min_wait_ms=0, max_wait_ms=0, restore_ms=40)
    config["timing"].update(
        intro_pause_ms=20, min_beat_interval_ms=60, max_beat_interval_ms=100,
        min_repeated_beats=3, max_repeated_beats=6, final_pause_ms=60,
    )
    config["flock"].update(min_stagger_ms=10, max_stagger_ms=30)
    for settings in config["servos"].values():
        settings.update(transition_ms=20, out_ms=20, back_ms=20)
    lengths = {clip["path"]: 40 for clip in config["audio"]["files"]}
    return servos, idle, config, xbox, lengths


@pytest.fixture
def voiced_flock(flock):
    _, _, config, _, lengths = flock
    voices = {}
    for index, bird in enumerate(config["flock"]["members"], start=1):
        files = [
            {"path": f"sound/seagull/{bird}/mine-{variant}.mp3",
             "animation_offset_ms": offset}
            for variant, offset in [(1, -5), (2, 5)]
        ]
        voices[bird] = {"files": files}
        lengths.update({clip["path"]: 40 + index * 10 for clip in files})
    config["flock"]["audio_by_member"] = voices
    return flock


@pytest.mark.parametrize("leader", ["seagull-1", "seagull-2", "seagull-3"])
def test_each_bird_keeps_its_voice_as_leader_or_follower(voiced_flock, leader):
    servos, _, config, _, lengths = voiced_flock
    normalized = validate_sequence(config)
    assert validate_sequence(json.loads(json.dumps(normalized))) == normalized
    timeline = build_timeline(normalized, lengths, leader)
    sequence = FlockSequence(config, servos, 0)
    for bird, schedule in timeline["members"].items():
        voice = config["flock"]["audio_by_member"][bird]
        offsets = {clip["path"]: clip["animation_offset_ms"] for clip in voice["files"]}
        assert all(beat["path"] in offsets for beat in schedule["beats"])
        assert all(beat["movement_ms"] - beat["audio_ms"] == pytest.approx(
            offsets[beat["path"]]) for beat in schedule["beats"])
        assert member_config(sequence.config, bird)["audio"]["random_per_beat"] is True
        end = max(beat["audio_ms"] + lengths[beat["path"]] for beat in schedule["beats"])
        assert schedule["end_ms"] >= end


def test_voice_fallback_partial_overrides_and_single_clip_performance(voiced_flock):
    _, _, config, _, lengths = voiced_flock
    voices = config["flock"]["audio_by_member"]
    del voices["seagull-3"]
    voices["seagull-1"]["random_per_beat"] = False
    voices["seagull-2"] = {"random_per_beat": False}
    normalized = validate_sequence(config)
    assert member_config(normalized, "seagull-3")["audio"] == normalized["audio"]
    assert member_config(normalized, "seagull-2")["audio"]["files"] == normalized["audio"]["files"]
    timeline = build_timeline(normalized, lengths, "seagull-1")
    assert len({beat["path"] for beat in timeline["members"]["seagull-1"]["beats"]}) == 1
    assert len({beat["path"] for beat in timeline["members"]["seagull-2"]["beats"]}) == 1
    shared = {clip["path"] for clip in config["audio"]["files"]}
    assert all(beat["path"] in shared for bird in ("seagull-2", "seagull-3")
               for beat in timeline["members"][bird]["beats"])


def test_follower_cue_uses_leaders_voice_duration(voiced_flock, monkeypatch):
    _, _, config, _, lengths = voiced_flock
    monkeypatch.setattr("common.sequence_config.random.choice", lambda values: values[0])
    monkeypatch.setattr("common.sequence_config.random.uniform", lambda a, b: a)
    leader = "seagull-2"
    for clip in config["flock"]["audio_by_member"][leader]["files"]:
        lengths[clip["path"]] = 1000
    timeline = build_timeline(config, lengths, leader)
    first = timeline["members"][leader]["beats"][0]
    for bird in ("seagull-1", "seagull-3"):
        beat = timeline["members"][bird]["beats"][0]
        assert beat["audio_ms"] == pytest.approx(first["audio_ms"] + 1000 + 10 + 5)


@pytest.mark.parametrize("override", [
    None, [], {"unknown": {}}, {"seagull-1": None},
    {"seagull-1": {"files": []}},
    {"seagull-1": {"files": [{"path": "../voice.mp3"}]}},
    {"seagull-1": {"files": [{"path": "/tmp/voice.mp3"}]}},
    {"seagull-1": {"files": [{"path": "sound/voice.mp3", "animation_offset_ms": float("nan")}]}},
    {"seagull-1": {"random_per_beat": "yes"}},
])
def test_invalid_voice_overrides_fail_explicitly(flock, override):
    _, _, config, _, _ = flock
    config["flock"]["audio_by_member"] = override
    with pytest.raises(ValueError):
        validate_sequence(config)


def test_voice_offset_overlap_checked_per_bird_not_across_voices(voiced_flock):
    _, _, config, _, _ = voiced_flock
    voices = config["flock"]["audio_by_member"]
    for clip in voices["seagull-1"]["files"]:
        clip["animation_offset_ms"] = -100
    for clip in voices["seagull-2"]["files"]:
        clip["animation_offset_ms"] = 100
    validate_sequence(config)
    voices["seagull-1"]["files"][1]["animation_offset_ms"] = 100
    with pytest.raises(ValueError, match="overlap"):
        validate_sequence(config)


@pytest.mark.parametrize("count", [1, 3])
def test_seagull_voice_configuration_wires_into_sequences(flock, monkeypatch, count):
    _, _, config, _, _ = flock
    voice = {"files": [{"path": "sound/seagull/voice.mp3", "animation_offset_ms": 0}]}
    monkeypatch.setattr(seagull_config, "seagull_voices", {"seagull-1": voice})
    _, _, sequences, _ = seagull_config.build_seagull_configuration(count)
    if count == 1:
        assert sequences["mine"]["audio"]["files"] == voice["files"]
        assert "flock" not in sequences["mine"]
    else:
        assert sequences["mine"]["flock"]["audio_by_member"] == {"seagull-1": voice}
        assert sequences["mine"]["audio"]["files"] == config["audio"]["files"]
    voice["files"].clear()
    selected = (sequences["mine"]["audio"] if count == 1 else
                sequences["mine"]["flock"]["audio_by_member"]["seagull-1"])
    assert selected["files"]


def test_unknown_configured_voice_name_fails(monkeypatch):
    monkeypatch.setattr(seagull_config, "seagull_voices", {"seagul-1": {}})
    with pytest.raises(ValueError, match="seagull_voices keys"):
        seagull_config.build_seagull_configuration(3)


def test_three_birds_have_unique_channels_and_independent_settings(flock):
    servos, idle, config, xbox, _ = flock
    assert [servo.get_pin() for servo in servos] == list(range(12))
    assert len({servo.get_name() for servo in servos}) == 12
    assert len(idle) == 9
    assert len(xbox) == 12
    assert len(config["servos"]) == 9
    assert set(config["flock"]["members"]) == {"seagull-1", "seagull-2", "seagull-3"}
    idle["seagull-1-wings"]["min_wait_ms"] = 9999
    assert idle["seagull-2-wings"]["min_wait_ms"] != 9999
    config["servos"]["seagull-1-beak"]["out_ms"] = 9999
    assert config["servos"]["seagull-2-beak"]["out_ms"] == 20


@pytest.mark.parametrize("count", [0, 5, True, 1.5, "3"])
def test_invalid_bird_count_fails(count):
    with pytest.raises(ValueError, match="SEAGULL_COUNT"):
        seagull_config.build_seagull_configuration(count)


def test_one_bird_keeps_existing_names_and_sequence(monkeypatch):
    monkeypatch.setattr(seagull_config, "load_calibration", lambda project: {})
    servos, idle, sequences, xbox = seagull_config.build_seagull_configuration(1)
    assert [servo.get_name() for servo in servos] == ["head-yaw", "head-pitch", "wings", "beak"]
    assert [servo.get_pin() for servo in servos] == [0, 1, 2, 3]
    assert "flock" not in validate_sequence(sequences["mine"])
    assert set(idle) == {"head-yaw", "head-pitch", "wings"}
    assert set(xbox) == {servo.get_name() for servo in servos}


def test_environment_selects_three_birds_at_import(monkeypatch):
    monkeypatch.setenv("SEAGULL_COUNT", "3")
    namespace = runpy.run_path(seagull_config.__file__)
    assert len(namespace["seagull_servos_data"]) == 12
    assert "flock" in namespace["generative_sequences"]["mine"]
    config = validate_sequence(namespace["generative_sequences"]["mine"])
    for index in range(1, 4):
        audio = member_config(config, f"seagull-{index}")["audio"]
        assert audio["files"] == [
            {"path": f"sound/seagull/voice-{index}/mine-{clip}.mp3", "animation_offset_ms": 0}
            for clip in range(1, 4)
        ]


@pytest.mark.parametrize("value", ["many", "0", "5"])
def test_invalid_environment_count_fails_at_import(monkeypatch, value):
    monkeypatch.setenv("SEAGULL_COUNT", value)
    with pytest.raises(ValueError, match="SEAGULL_COUNT"):
        runpy.run_path(seagull_config.__file__)


@pytest.mark.parametrize("project_id", [None, "unknown"])
def test_invalid_project_configuration_fails_explicitly(monkeypatch, project_id):
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    if project_id is None:
        monkeypatch.delenv("PROJECT_ID", raising=False)
    else:
        monkeypatch.setenv("PROJECT_ID", project_id)
    with pytest.raises(KeyError, match="PROJECT_ID"):
        Project(init_servos=False)


def test_calibration_requires_all_twelve_names_and_loads_each_bird(flock, monkeypatch, tmp_path):
    servos, _, _, _, _ = flock
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_ID", "flock")
    names = [servo.get_name() for servo in servos]
    limits = {name: {"min": 20 + index, "max": 160, "rest": 90}
              for index, name in enumerate(names)}
    save_calibration("seagull", {names[0]: limits[names[0]]})
    assert not has_calibration("seagull", names)
    save_calibration("seagull", limits)
    assert has_calibration("seagull", names)
    monkeypatch.setattr(seagull_config, "load_calibration", load_calibration)
    loaded, _, _, _ = seagull_config.build_seagull_configuration(3)
    assert [servo.get_physical_limit_min() for servo in loaded] == list(range(20, 32))


@pytest.mark.parametrize("leader", ["seagull-1", "seagull-2", "seagull-3"])
def test_any_bird_can_lead(flock, monkeypatch, leader):
    servos, _, config, _, _ = flock
    monkeypatch.setattr("common.flock.random.choice", lambda birds: leader)
    sequence = FlockSequence(config, servos, 0)
    assert sequence.leader == leader
    assert sequence.paused_servos == set(config["flock"]["members"][leader])


def test_followers_join_after_one_or_two_calls_with_independent_timelines(flock, monkeypatch):
    _, _, config, _, lengths = flock
    joins = iter([1, 2])
    repeats = iter([3, 4, 5])
    monkeypatch.setattr("common.sequence_config.random.randint", lambda a, b: next(repeats))
    monkeypatch.setattr("common.sequence_config.random.choice",
                        lambda choices: next(joins) if choices == [1, 2] else choices[0])
    monkeypatch.setattr("common.sequence_config.random.uniform", lambda a, b: (a + b) / 2)
    timeline = build_timeline(config, lengths, "seagull-2")
    members = timeline["members"]
    leader = members["seagull-2"]
    assert [len(members[bird]["beats"]) for bird in
            ["seagull-2", "seagull-1", "seagull-3"]] == [5, 6, 7]
    for bird, call in [("seagull-1", 1), ("seagull-3", 2)]:
        trigger = leader["beats"][call - 1]
        expected_start = max(trigger["audio_ms"] + lengths[trigger["path"]] + 20, 120)
        assert members[bird]["beats"][0]["audio_ms"] == expected_start
        assert members[bird]["prepare_ms"] == expected_start - 120
        assert members[bird]["beats"][0]["audio_ms"] >= members[bird]["prepare_ms"] + 20
        assert members[bird]["end_ms"] > leader["end_ms"]
    assert timeline["beats"] == sorted(timeline["beats"], key=lambda beat: beat["audio_ms"])
    assert {beat["member"] for beat in timeline["beats"]} == set(members)
    for beat in timeline["beats"]:
        assert beat["audio_ms"] == beat["movement_ms"]
    assert timeline["end_ms"] == max(item["end_ms"] for item in members.values())


def test_flock_preserves_signed_clip_offsets_and_nonoverlapping_pulses(flock):
    _, _, config, _, lengths = flock
    config["timing"].update(min_beat_interval_ms=90, final_pause_ms=90)
    config["audio"]["files"][0]["animation_offset_ms"] = -20
    config["audio"]["files"][1]["animation_offset_ms"] = 20
    offsets = {clip["path"]: clip["animation_offset_ms"] for clip in config["audio"]["files"]}
    for _ in range(10):
        timeline = build_timeline(config, lengths, "seagull-1")
        for bird, item in timeline["members"].items():
            beats = item["beats"]
            assert all(beat["movement_ms"] - beat["audio_ms"] == pytest.approx(
                offsets[beat["path"]]) for beat in beats)
            assert all(b["movement_ms"] - a["movement_ms"] >= 40
                       for a, b in zip(beats, beats[1:]))
            if bird != timeline["leader"]:
                first = min(beats[0]["audio_ms"], beats[0]["movement_ms"])
                assert first - item["prepare_ms"] == pytest.approx(120)


def test_followers_stay_idle_until_join_and_birds_finish_individually(flock, monkeypatch):
    servos, _, config, _, lengths = flock
    rng = random.Random(14)
    monkeypatch.setattr("common.flock.random.choice", rng.choice)
    sequence = FlockSequence(config, servos, 0)
    assert sequence.update(0.02) == "ready"
    timeline = build_timeline(config, lengths, sequence.leader)
    sequence.arm(timeline, 0.02, 100)
    followers = set(sequence.members) - {sequence.leader}
    assert all(not servo.history for servo in servos
               if any(servo.get_name() in sequence.members[bird] for bird in followers))
    completed_at = {}
    for tick in range(3, 500):
        now = tick / 1000 * 10
        before = set(sequence.completed)
        result = sequence.update(now)
        for bird in sequence.completed - before:
            completed_at[bird] = now
            assert not set(sequence.members[bird]).intersection(sequence.paused_servos)
        for bird in followers - sequence.completed - sequence.active.keys():
            assert all(not servo.history for servo in servos
                       if servo.get_name() in sequence.members[bird])
        if result == "complete":
            break
    assert result == "complete"
    assert set(completed_at) == set(sequence.members)
    assert len(set(completed_at.values())) > 1
    assert all(servo.current == pytest.approx(90) for servo in servos)


@pytest.mark.parametrize("when", ["waiting", "playing"])
def test_flock_cancellation_restores_only_active_birds(flock, when):
    servos, _, config, _, lengths = flock
    sequence = FlockSequence(config, servos, 0)
    sequence.update(0.02)
    if when == "playing":
        sequence.arm(build_timeline(config, lengths, sequence.leader), 0.02, 100)
        for tick in range(3, 70):
            sequence.update(tick / 100)
    active = set(sequence.active)
    histories = {servo.get_name(): len(servo.history) for servo in servos}
    sequence.abort(0.7)
    sequence.update(0.7)
    assert sequence.update(0.75) == "complete"
    assert sequence.aborted
    assert not sequence.paused_servos
    for bird in sequence.members.keys() - active - sequence.completed:
        assert all(len(servo.history) == histories[servo.get_name()] for servo in servos
                   if servo.get_name() in sequence.members[bird])
    assert all(servo.current == pytest.approx(90) for servo in servos)


@pytest.mark.parametrize("invalid", ["shared-servo", "missing-member", "bad-join", "bad-stagger"])
def test_invalid_flock_settings_fail(flock, invalid):
    _, _, config, _, _ = flock
    group = config["flock"]
    if invalid == "shared-servo":
        group["members"]["seagull-2"].append("seagull-1-beak")
    elif invalid == "missing-member":
        del group["members"]["seagull-2"]
    elif invalid == "bad-join":
        group["join_after_beats"] = [True]
    else:
        group["min_stagger_ms"] = 1000
    with pytest.raises(ValueError):
        validate_sequence(config)


@pytest.mark.parametrize("invalid", ["leader", "member", "preparation", "overlap"])
def test_invalid_flock_schedules_fail_before_playback(flock, invalid):
    servos, _, config, _, lengths = flock
    sequence = FlockSequence(config, servos, 0)
    sequence.update(0.02)
    timeline = build_timeline(config, lengths, sequence.leader)
    if invalid == "leader":
        timeline["leader"] = "unknown"
    elif invalid == "member":
        timeline["members"].pop(sequence.leader)
    else:
        follower = next(bird for bird in sequence.members if bird != sequence.leader)
        item = timeline["members"][follower]
        if invalid == "preparation":
            item["prepare_ms"] = item["beats"][0]["movement_ms"]
        else:
            item["beats"][1]["movement_ms"] = item["beats"][0]["movement_ms"]
    with pytest.raises(ValueError):
        sequence.arm(timeline, 0.02, 100)
    assert sequence.phase == "waiting"


def test_unknown_servos_timeout_and_missed_preparation_fail_explicitly(flock):
    servos, _, config, _, lengths = flock
    with pytest.raises(ValueError, match="Unknown flock"):
        FlockSequence(config, servos[:-1], 0)
    sequence = FlockSequence(config, servos, 0)
    with pytest.raises(ValueError, match="waiting"):
        sequence.arm({}, 0, 100)
    sequence.update(0.02)
    with pytest.raises(TimeoutError):
        sequence.update(11)
    sequence.arm(build_timeline(config, lengths, sequence.leader), 0.02, 100)
    sequence.update(5)
    with pytest.raises(RuntimeError, match="preparation deadline"):
        sequence.update(5.1)


def test_idle_controllers_only_restart_for_the_bird_that_finishes(flock, monkeypatch):
    servos, idle, config, _, lengths = flock
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", servos)
    project = Project(init_servos=False)
    project._generative_settings = idle

    class Controller:
        def __init__(self, servo, settings):
            self.calls = 0
            self.start = servo.get_current_position()

        def update(self):
            self.calls += 1

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    controllers = {servo.get_name(): Controller(servo, idle[servo.get_name()])
                   for servo in servos if servo.get_name() in idle}
    sequence = FlockSequence(config, servos, 0)
    sequence.update(0.02)
    sequence.arm(build_timeline(config, lengths, sequence.leader), 0.02, 100)
    paused = sequence.paused_servos
    restarted = set()
    for tick in range(3, 500):
        result = sequence.update(tick / 100)
        next_paused = sequence.paused_servos
        old = dict(controllers)
        calls = {name: controller.calls for name, controller in controllers.items()}
        paused = project._Project__update_idle(
            controllers, None if result == "complete" else sequence, paused
        )
        assert paused == next_paused
        for name, controller in controllers.items():
            if controller is not old[name]:
                assert name not in restarted
                assert name not in paused
                assert controller.start == pytest.approx(90)
                restarted.add(name)
            elif name in paused:
                assert controller.calls == calls[name]
            else:
                assert controller.calls == calls[name] + 1
        if result == "complete":
            break
    assert result == "complete"
    assert restarted == set(idle)


@pytest.mark.parametrize("cancel", [None, "waiting", "playing"])
def test_auto_worker_preserves_other_birds_idle_and_cancels_group(flock, monkeypatch, cancel):
    servos, idle, config, _, lengths = flock
    monkeypatch.setenv("PROJECT_ID", "seagull")
    monkeypatch.setattr(project_module, "load_dotenv", lambda: None)
    monkeypatch.setitem(project_module.servos_data_object, "seagull", servos)
    project = Project(init_servos=False)
    project._generative_settings = idle
    project._sequence_settings = {"mine": config}
    controllers = {}
    sent = []
    prepared = threading.Event()
    completed = threading.Event()

    class Controller:
        def __init__(self, servo, settings):
            self.calls = 0
            controllers[servo.get_name()] = self

        def update(self):
            self.calls += 1

    monkeypatch.setattr(project_module, "GenerativeMovement", Controller)
    deadlines = iter([time.monotonic() + 0.03, time.monotonic() + 1000])
    monkeypatch.setattr(Project, "_Project__next_sequence_due",
                        staticmethod(lambda cfg: next(deadlines)))

    def send(action, data):
        sent.append((action, data))
        if action == WEBSOCKET_MESSAGES["sequence-ready"]:
            if cancel != "waiting":
                project.sequence_command(WEBSOCKET_MESSAGES["sequence-arm"], {
                    "id": data["id"], "lead_ms": 100,
                    "timeline": build_timeline(config, lengths, data["leader"]),
                })
            prepared.set()
        elif action == WEBSOCKET_MESSAGES["sequence-complete"]:
            completed.set()

    project.sequence_sender = send
    try:
        project.auto_start()
        assert prepared.wait(2)
        leader = next(data["leader"] for action, data in sent
                      if action == WEBSOCKET_MESSAGES["sequence-ready"])
        leader_controller = controllers[f"{leader}-head-yaw"]
        follower = next(bird for bird in config["flock"]["members"] if bird != leader)
        follower_controller = controllers[f"{follower}-head-yaw"]
        initial = (leader_controller.calls, follower_controller.calls)
        threading.Event().wait(0.06)
        assert leader_controller.calls == initial[0]
        assert follower_controller.calls > initial[1]
        if not cancel:
            assert completed.wait(4)
        elif cancel == "playing":
            threading.Event().wait(0.2)
    finally:
        project.auto_stop()
    assert all(servo.current == 90 for servo in servos)
    actions = [action for action, _ in sent]
    if cancel:
        assert actions[-1] == WEBSOCKET_MESSAGES["sequence-cancel"]
    else:
        assert WEBSOCKET_MESSAGES["sequence-armed"] in actions
        assert WEBSOCKET_MESSAGES["sequence-complete"] in actions


@pytest.mark.parametrize("audio_fixture", ["flock", "voiced_flock"])
def test_server_plays_every_birds_independent_audio_and_stops(
    request, monkeypatch, audio_fixture
):
    _, _, config, _, lengths = request.getfixturevalue(audio_fixture)
    played = []
    stopped = []
    monkeypatch.setitem(sys.modules, "pygame", types.SimpleNamespace(error=RuntimeError))
    monkeypatch.setattr("common.sequence_audio.LEAD_MS", 100)

    class Channel:
        def get_busy(self):
            return False

        def play(self, sound):
            played.append(sound)

        def stop(self):
            stopped.append(True)

    async def exercise():
        sent = []

        async def send(action, data):
            sent.append((action, data))
            audio.acknowledge(data)

        audio = SequenceAudio(send)
        audio.configure({"mine": config})
        audio.channel = Channel()
        audio.sounds = {path: path for path in lengths}

        async def load(settings):
            return lengths

        monkeypatch.setattr(audio, "_load_async", load)
        await audio.ready({"id": "flock", "name": "mine", "leader": "seagull-3"})
        await audio.task
        schedule = sent[0][1]["timeline"]
        assert schedule["leader"] == "seagull-3"
        assert played == [beat["path"] for beat in schedule["beats"]]
        assert {beat["member"] for beat in schedule["beats"]} == set(config["flock"]["members"])
        normalized = validate_sequence(config)
        for beat in schedule["beats"]:
            files = member_config(normalized, beat["member"])["audio"]["files"]
            assert beat["path"] in {clip["path"] for clip in files}
        await audio.stop({"id": "flock"})
        assert audio.active_id is None
        assert stopped

    asyncio.run(exercise())


@pytest.mark.parametrize("shared_fallback", [False, True])
def test_server_preloads_all_member_voices_and_shared_fallback(
    voiced_flock, monkeypatch, tmp_path, shared_fallback
):
    _, _, config, _, _ = voiced_flock
    if shared_fallback:
        del config["flock"]["audio_by_member"]["seagull-3"]
    config = validate_sequence(config)
    files = {clip["path"] for bird in config["flock"]["members"]
             for clip in member_config(config, bird)["audio"]["files"]}
    monkeypatch.chdir(tmp_path)
    for path in files:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"test audio")
    loaded = []

    class Sound:
        def __init__(self, path):
            loaded.append(path)

        def get_length(self):
            return 0.25

    class Channel:
        def stop(self):
            pass

    mixer = types.SimpleNamespace(get_init=lambda: True, Sound=Sound)
    monkeypatch.setitem(sys.modules, "pygame", types.SimpleNamespace(
        error=RuntimeError, mixer=mixer,
    ))
    monkeypatch.setattr(SequenceAudio, "_allocate_channel", lambda self, mixer: (123, Channel()))

    async def exercise():
        async def send(*args):
            return None

        audio = SequenceAudio(send)
        try:
            audio.configure({"mine": config})
            await audio.preload()
            assert set(audio.sounds) == files
            assert len(loaded) == len(files)
            lengths = await audio._load_async(audio.settings["mine"])
            assert set(lengths) == files
            assert set(lengths.values()) == {250}
            assert len(loaded) == len(files)
            voice = config["flock"]["audio_by_member"]["seagull-1"]["files"][0]["path"]
            (tmp_path / voice).unlink()
            with pytest.raises(ValueError, match="missing or outside sound/"):
                await audio._load_async(audio.settings["mine"])
        finally:
            await audio.close()

    asyncio.run(exercise())
