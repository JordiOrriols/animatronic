"""Hardware-independent validation and timelines for generative sequences."""

import math
import random
from pathlib import PurePosixPath


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
    timing = _object(config.get("timing", {}), "timing")
    times = {}
    for key, default in (
        ("intro_pause_ms", 2000), ("beat_interval_ms", 500),
        ("final_pause_ms", 500), ("min_repeated_beats", 3), ("max_repeated_beats", 6),
    ):
        times[key] = number(timing.get(key, default), key)
    for key in ("min_repeated_beats", "max_repeated_beats"):
        if not times[key].is_integer() or not 1 <= times[key] <= 100:
            raise ValueError(f"{key} must be an integer from 1 to 100")
        times[key] = int(times[key])
    if times["min_repeated_beats"] > times["max_repeated_beats"]:
        raise ValueError("min_repeated_beats exceeds max_repeated_beats")
    if times["beat_interval_ms"] <= 0:
        raise ValueError("beat_interval_ms must be positive")
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
    minimum_gap = min(times["beat_interval_ms"], times["final_pause_ms"])
    if pulse_ms and pulse_ms + max(offsets) - min(offsets) > minimum_gap:
        raise ValueError("Audio offsets and pulse durations would overlap consecutive beats")
    minimum_wait = number(config.get("min_wait_ms", 15000), "min_wait_ms")
    maximum_wait = number(config.get("max_wait_ms", 45000), "max_wait_ms")
    if minimum_wait > maximum_wait:
        raise ValueError("min_wait_ms exceeds max_wait_ms")
    return {
        "min_wait_ms": minimum_wait, "max_wait_ms": maximum_wait,
        "audio": {"files": clips, "random_per_beat": random_per_beat},
        "timing": times, "servos": servos,
        "restore_ms": number(config.get("restore_ms", 600), "restore_ms"),
    }


def build_timeline(config: dict, lengths_ms: dict[str, float]) -> dict:
    """Preselect variants and schedule audio/pulses with signed per-clip offsets."""
    config = validate_sequence(config)
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
        first_end + timing["intro_pause_ms"],
        origin + pulse_ms + first["animation_offset_ms"] - selected[1]["animation_offset_ms"],
    )
    starts = [origin] + [start + i * timing["beat_interval_ms"] for i in range(repeats)]
    starts.append(starts[-1] + timing["final_pause_ms"])
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
