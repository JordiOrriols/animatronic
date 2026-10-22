"""Hardware-independent validation and timelines for generative sequences."""

import math
import random
from pathlib import PurePosixPath
from typing import Optional


def number(value, name: str, minimum: float = 0, maximum: float = math.inf) -> float:
    """Validate a finite numeric configuration value without coercing strings."""
    if (
        isinstance(value, bool) or not isinstance(value, (int, float))
        or not math.isfinite(value) or not minimum <= value <= maximum
    ):
        raise ValueError(f"{name} must be a finite number in [{minimum}, {maximum}]")
    return float(value)


def _object(value, name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _position(value, name: str) -> dict:
    value = _object(value, name)
    if value.get("reference") not in ("min", "max", "neutral"):
        raise ValueError(f"{name}.reference must be min, max or neutral")
    fraction = number(value.get("fraction", 0), f"{name}.fraction", maximum=1)
    return {"reference": value["reference"], "fraction": fraction}


def _timing(value) -> dict:
    timing = _object(value, "timing")
    times = {}
    for key, default in (
        ("intro_pause_ms", 2000), ("final_pause_ms", 500),
        ("min_repeated_beats", 3), ("max_repeated_beats", 6),
    ):
        times[key] = number(timing.get(key, default), key)
    has_range = "min_beat_interval_ms" in timing or "max_beat_interval_ms" in timing
    if has_range and "beat_interval_ms" in timing:
        raise ValueError("Use beat_interval_ms or min/max_beat_interval_ms, not both")
    # A fixed beat_interval_ms is shorthand for an equal min/max range.
    fixed = timing.get("beat_interval_ms", 500)
    for key in ("min_beat_interval_ms", "max_beat_interval_ms"):
        times[key] = number(timing.get(key, fixed) if has_range else fixed, key)
    for key in ("min_repeated_beats", "max_repeated_beats"):
        if not times[key].is_integer() or not 1 <= times[key] <= 100:
            raise ValueError(f"{key} must be an integer from 1 to 100")
        times[key] = int(times[key])
    if times["min_repeated_beats"] > times["max_repeated_beats"]:
        raise ValueError("min_repeated_beats exceeds max_repeated_beats")
    if times["min_beat_interval_ms"] <= 0:
        raise ValueError("min_beat_interval_ms must be positive")
    if times["min_beat_interval_ms"] > times["max_beat_interval_ms"]:
        raise ValueError("min_beat_interval_ms exceeds max_beat_interval_ms")
    for pause in ("intro_pause_ms", "final_pause_ms"):
        if f"min_{pause}" in timing or f"max_{pause}" in timing:
            minimum = number(timing.get(f"min_{pause}", times[pause]), f"min_{pause}")
            maximum = number(timing.get(f"max_{pause}", times[pause]), f"max_{pause}")
            if minimum > maximum:
                raise ValueError(f"min_{pause} exceeds max_{pause}")
            times[f"min_{pause}"], times[f"max_{pause}"] = minimum, maximum
    return times


def validate_sequence(config: dict) -> dict:
    """Normalize a sequence, failing before movement on invalid settings."""
    config = _object(config, "sequence")
    audio = _object(config.get("audio"), "audio")
    files = audio.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("audio.files must contain at least one clip")
    clips = []
    for item in files:
        item = _object(item, "audio.files entry")
        path = item.get("path")
        if not isinstance(path, str):
            raise ValueError("Audio path must be a string under sound/")
        parts = PurePosixPath(path).parts
        if not parts or parts[0] != "sound" or ".." in parts or "\\" in path:
            raise ValueError("Audio path must be a relative path under sound/")
        offset = number(item.get("animation_offset_ms", 0), "animation_offset_ms", -10000, 10000)
        clips.append({"path": path, "animation_offset_ms": offset})
    random_per_beat = audio.get("random_per_beat", True)
    if not isinstance(random_per_beat, bool):
        raise ValueError("audio.random_per_beat must be a boolean")
    times = _timing(config.get("timing", {}))
    servo_configs = _object(config.get("servos"), "servos")
    if not servo_configs:
        raise ValueError("servos must contain at least one servo")
    servos = {}
    for name, item in servo_configs.items():
        item = _object(item, f"servos.{name}")
        if not isinstance(name, str) or item.get("mode") not in ("hold", "pulse"):
            raise ValueError("Each sequence servo needs a name and a hold or pulse mode")
        settings = {
            "mode": item["mode"],
            "position_1": _position(item.get("position_1"), f"{name}.position_1"),
            "position_2": _position(item.get("position_2"), f"{name}.position_2"),
        }
        for key, default in (
            ("transition_ms", 600), ("out_ms", 100), ("back_ms", 200),
            ("ease_in", 0.2), ("ease_out", 0.2),
        ):
            settings[key] = number(
                item.get(key, default), f"{name}.{key}",
                maximum=1 if key.startswith("ease_") else math.inf,
            )
        if settings["mode"] == "pulse" and settings["out_ms"] + settings["back_ms"] <= 0:
            raise ValueError(f"{name}: a pulse must have a positive duration")
        servos[name] = settings
    offsets = [clip["animation_offset_ms"] for clip in clips]
    pulse_ms = max(
        (s["out_ms"] + s["back_ms"] for s in servos.values() if s["mode"] == "pulse"),
        default=0,
    )
    # Independent random variants may shorten the gap between movement starts.
    minimum_gap = min(times["min_beat_interval_ms"],
                      times.get("min_final_pause_ms", times["final_pause_ms"]))
    if pulse_ms and pulse_ms + max(offsets) - min(offsets) > minimum_gap:
        raise ValueError("Audio offsets and pulse durations would overlap consecutive beats")
    minimum_wait = number(config.get("min_wait_ms", 15000), "min_wait_ms")
    maximum_wait = number(config.get("max_wait_ms", 45000), "max_wait_ms")
    if minimum_wait > maximum_wait:
        raise ValueError("min_wait_ms exceeds max_wait_ms")
    result = {
        "min_wait_ms": minimum_wait, "max_wait_ms": maximum_wait,
        "audio": {"files": clips, "random_per_beat": random_per_beat},
        "timing": times, "servos": servos,
        "restore_ms": number(config.get("restore_ms", 600), "restore_ms"),
    }
    if "flock" in config:
        result["flock"] = _validate_flock(config["flock"], servos)
        if "audio_by_member" in config["flock"]:
            result["flock"]["audio_by_member"] = _member_audio(
                result, config["flock"]["audio_by_member"]
            )
    return result


def _member_audio(config: dict, value) -> dict:
    overrides = _object(value, "flock.audio_by_member")
    unknown = overrides.keys() - config["flock"]["members"].keys()
    if unknown:
        raise ValueError(f"Unknown flock audio members: {sorted(unknown, key=str)}")
    result = {}
    for member, audio in overrides.items():
        audio = _object(audio, f"flock.audio_by_member.{member}")
        settings = member_config(config, member)
        settings["audio"] = {**config["audio"], **audio}
        result[member] = validate_sequence(settings)["audio"]
    return result


def _validate_flock(value, servos: dict) -> dict:
    flock = _object(value, "flock")
    members = _object(flock.get("members"), "flock.members")
    if len(members) < 2:
        raise ValueError("flock.members requires at least two birds")
    assigned = set()
    for name, names in members.items():
        if (not isinstance(name, str) or not name or not isinstance(names, list)
                or not names or any(not isinstance(item, str) or not item for item in names)):
            raise ValueError("Each flock member needs a name and a list of servo names")
        if len(set(names)) != len(names) or assigned.intersection(names):
            raise ValueError("Flock members cannot share servos")
        if not set(names).intersection(servos):
            raise ValueError(f"Flock member {name} has no sequence servos")
        assigned.update(names)
    if servos.keys() - assigned:
        raise ValueError("All sequence servos must belong to a flock member")
    joins = flock.get("join_after_beats", [1, 2])
    if (not isinstance(joins, list) or not joins
            or any(isinstance(item, bool) or not isinstance(item, int)
                   or item not in (1, 2) for item in joins)):
        raise ValueError("flock.join_after_beats must contain 1 or 2")
    minimum = number(flock.get("min_stagger_ms", 100), "flock.min_stagger_ms")
    maximum = number(flock.get("max_stagger_ms", 400), "flock.max_stagger_ms")
    if minimum > maximum:
        raise ValueError("flock.min_stagger_ms exceeds max_stagger_ms")
    return {
        "members": {name: list(names) for name, names in members.items()},
        "join_after_beats": list(joins),
        "min_stagger_ms": minimum, "max_stagger_ms": maximum,
    }


def member_config(config: dict, member: str) -> dict:
    """Extract one bird's ordinary sequence from a validated flock event."""
    names = config["flock"]["members"][member]
    return {
        **{key: value for key, value in config.items() if key != "flock"},
        "audio": config["flock"].get("audio_by_member", {}).get(member, config["audio"]),
        "servos": {name: settings for name, settings in config["servos"].items()
                   if name in names},
    }


def build_timeline(config: dict, lengths_ms: dict[str, float],
                   leader: Optional[str] = None) -> dict:
    """Preselect variants and schedule audio/pulses with signed per-clip offsets."""
    config = validate_sequence(config)
    if "flock" in config:
        return _flock_timeline(config, lengths_ms, leader)
    timing = config["timing"]
    repeats = random.randint(timing["min_repeated_beats"], timing["max_repeated_beats"])
    files = config["audio"]["files"]
    first = random.choice(files)
    selected = [first]
    for _ in range(repeats + 1):
        selected.append(random.choice(files) if config["audio"]["random_per_beat"] else first)
    pulse_ms = max(
        (s["out_ms"] + s["back_ms"] for s in config["servos"].values() if s["mode"] == "pulse"),
        default=0,
    )
    for clip in files:
        number(lengths_ms.get(clip["path"]), "audio clip length", minimum=0.001)
    origin = max(0, -min(clip["animation_offset_ms"] for clip in selected))
    first_end = max(
        origin + lengths_ms[first["path"]],
        origin + first["animation_offset_ms"] + pulse_ms,
    )
    start = max(
        first_end + _random_pause(timing, "intro_pause_ms"),
        origin + pulse_ms + first["animation_offset_ms"] - selected[1]["animation_offset_ms"],
    )
    starts = [origin, start]
    for _ in range(repeats - 1):
        starts.append(starts[-1] + random.uniform(
            timing["min_beat_interval_ms"], timing["max_beat_interval_ms"]
        ))
    starts.append(starts[-1] + _random_pause(timing, "final_pause_ms"))
    beats = [
        {"path": clip["path"], "audio_ms": audio_start,
         "movement_ms": audio_start + clip["animation_offset_ms"]}
        for clip, audio_start in zip(selected, starts)
    ]
    end_ms = max(
        max(beat["audio_ms"] + lengths_ms[beat["path"]], beat["movement_ms"] + pulse_ms)
        for beat in beats
    )
    return {"beats": beats, "end_ms": end_ms}


def _random_pause(timing: dict, name: str) -> float:
    if f"min_{name}" not in timing:
        return timing[name]
    return random.uniform(timing[f"min_{name}"], timing[f"max_{name}"])


def _flock_timeline(config: dict, lengths_ms: dict[str, float],
                    leader: Optional[str]) -> dict:
    flock = config["flock"]
    if not isinstance(leader, str) or leader not in flock["members"]:
        raise ValueError("Flock schedule requires a valid leader")
    first = build_timeline(member_config(config, leader), lengths_ms)
    members = {leader: {**first, "prepare_ms": 0}}
    for bird in flock["members"]:
        if bird == leader:
            continue
        calls = random.choice(flock["join_after_beats"])
        beat = first["beats"][calls - 1]
        stagger_ms = random.uniform(
            flock["min_stagger_ms"], flock["max_stagger_ms"]
        )
        settings = member_config(config, bird)
        preparation = max(item["transition_ms"] for item in settings["servos"].values())
        timeline = build_timeline(settings, lengths_ms)
        first_beat = timeline["beats"][0]
        first_action = min(first_beat["audio_ms"], first_beat["movement_ms"])
        # Prepare ahead of the join cue, with margin for the Pi worker's 20 ms ticks.
        start_ms = max(beat["audio_ms"] + lengths_ms[beat["path"]], preparation + 100)
        start_ms += stagger_ms
        prepare_ms = start_ms - preparation - 100
        shift_ms = start_ms - first_action
        members[bird] = {
            "prepare_ms": prepare_ms,
            "beats": [{**item, "audio_ms": item["audio_ms"] + shift_ms,
                       "movement_ms": item["movement_ms"] + shift_ms}
                      for item in timeline["beats"]],
            "end_ms": timeline["end_ms"] + shift_ms,
        }
    return {
        "leader": leader, "members": members,
        "beats": sorted(
            [{**beat, "member": bird}
             for bird, timeline in members.items() for beat in timeline["beats"]],
            key=lambda beat: beat["audio_ms"],
        ),
        "end_ms": max(item["end_ms"] for item in members.values()),
    }


def validate_movement_timeline(config: dict, timeline: dict) -> dict:
    """Validate ordered, non-overlapping pulses before accepting a server schedule."""
    if not isinstance(timeline, dict):
        raise ValueError("Sequence timeline must be an object")
    beats = timeline.get("beats")
    if not isinstance(beats, list) or not beats:
        raise ValueError("Sequence timeline requires beats")
    if any(not isinstance(beat, dict) for beat in beats):
        raise ValueError("Each sequence beat must be an object")
    times = [number(beat.get("movement_ms"), "movement_ms") for beat in beats]
    if times != sorted(times):
        raise ValueError("Sequence movement timestamps must be ordered")
    pulse_ms = max(
        (s["out_ms"] + s["back_ms"] for s in config["servos"].values()
         if s["mode"] == "pulse"), default=0,
    )
    if any(b - a < pulse_ms and not math.isclose(b - a, pulse_ms, rel_tol=0, abs_tol=1e-6)
           for a, b in zip(times, times[1:])):
        raise ValueError("Sequence movement timestamps overlap")
    end_ms = number(timeline.get("end_ms"), "end_ms")
    last_end = times[-1] + pulse_ms
    if end_ms < last_end and not math.isclose(end_ms, last_end, rel_tol=0, abs_tol=1e-6):
        raise ValueError("Sequence end precedes the last pulse completion")
    return {"beats": [dict(beat) for beat in beats], "end_ms": end_ms}
