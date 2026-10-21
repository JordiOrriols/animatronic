"""Seagull configuration module. Add here all servos for the animatronic."""

import os
from copy import deepcopy

from common.calibration import load_calibration
from common.config import MG90S_TYPE, GHS37A_TYPE
from common.logger import Logger
from common.servo import AniServo

logger = Logger("SeagullConfig")

# (pin, servo_type) for every servo on this animatronic. Min/max/rest limits are
# calibration data, sourced from servo_calibration.json (see common/calibration.py)
# and kept up to date via the server's "Calibrate" menu option.
_SERVO_TYPES = {
    # HEAD
    "head-yaw": (0, MG90S_TYPE),
    "head-pitch": (1, MG90S_TYPE),
    # WINGS
    "wings": (2, MG90S_TYPE),
    # MANDIBLE
    "beak": (3, GHS37A_TYPE),
}

_DEFAULT_LIMITS = {"min": 0, "max": 180, "rest": 90}


def _build_servos_data(count=1):
    """Build every AniServo from calibration data, falling back to sane defaults
    for any servo not yet present in servo_calibration.json."""
    calibration = load_calibration("seagull")
    servos = []
    for index in range(count):
        for part, (pin, servo_type) in _SERVO_TYPES.items():
            name = part if count == 1 else f"seagull-{index + 1}-{part}"
            limits = calibration.get(name)
            if limits is None:
                logger.warning(f"No calibration data for servo '{name}'; using defaults.")
                limits = _DEFAULT_LIMITS
            servos.append(
                AniServo(name, pin + index * 4, servo_type,
                         limits["min"], limits["max"], limits["rest"])
            )
    return servos


# Per-servo generative configuration (all values in ms or degrees where noted)
# This file uses only per-servo settings as requested.
# Unlisted servos (such as the beak) stay at their calibrated rest position in Auto mode.
#
# min_angle/max_angle are intentionally omitted - GenerativeMovement falls back to
# each servo's own calibrated physical limits (see servo_calibration.json).
generative_settings = {
    "head-yaw": {
        "min_range_fraction": 1.0,
        "max_range_fraction": 1.0,
        "min_duration_ms": 200,
        "max_duration_ms": 1200,
        "min_wait_ms": 800,
        "max_wait_ms": 3000,
        "random_factor": 0.8,
        "ease_in": 0.15,
        "ease_out": 0.15,
        "return_to_rest": False,
    },
    "head-pitch": {
        "min_range_fraction": 0.2,
        "max_range_fraction": 0.2,
        "min_duration_ms": 300,
        "max_duration_ms": 900,
        "min_wait_ms": 600,
        "max_wait_ms": 2000,
        "random_factor": 0.7,
        "ease_in": 0.15,
        "ease_out": 0.15,
        "return_to_rest": False,
    },
    "wings": {
        "min_range_fraction": 1.0,
        "max_range_fraction": 1.0,
        "min_duration_ms": 200,
        "max_duration_ms": 600,
        "min_wait_ms": 400,
        "max_wait_ms": 1200,
        "random_factor": 1.0,
        "ease_in": 0.0,
        "ease_out": 0.0,
        "return_to_rest": True,
        "rest_hold_ms": 150,
    },
}

# These clips are played on the server; overlapping beats play each clip fully.
generative_sequences = {
    "mine": {
        "enabled": True,
        "min_wait_ms": 15000,
        "max_wait_ms": 45000,
        "audio": {
            "files": [
                {"path": "sound/seagull/voice-1/mine-1.mp3", "animation_offset_ms": 0},
                {"path": "sound/seagull/voice-1/mine-2.mp3", "animation_offset_ms": 0},
                {"path": "sound/seagull/voice-1/mine-3.mp3", "animation_offset_ms": 0},
            ],
            "random_per_beat": True,
        },
        "timing": {
            "intro_pause_ms": 200,
            # Each gap between rhythmic beats is chosen randomly in this range.
            "min_beat_interval_ms": 400,
            "max_beat_interval_ms": 800,
            "min_repeated_beats": 3,
            "max_repeated_beats": 9,
            "final_pause_ms": 500,
        },
        # Pulses (out_ms + back_ms) must fit in min_beat_interval_ms.
        "servos": {
            "head-pitch": {
                "mode": "pulse",
                "position_1": {"reference": "max", "fraction": 0.5},
                "position_2": {"reference": "max", "fraction": 0.9},
                "transition_ms": 600,
                "out_ms": 150,
                "back_ms": 180,
                "ease_in": 0.2,
                "ease_out": 0.2,
            },
            "beak": {
                "mode": "pulse",
                "position_1": {"reference": "max", "fraction": 0.2},
                "position_2": {"reference": "max", "fraction": 0.9},
                "transition_ms": 300,
                "out_ms": 140,
                "back_ms": 190,
                "ease_in": 0.1,
                "ease_out": 0.1,
            },
            # Wings rest at Max, so their travel goes toward Min.
            "wings": {
                "mode": "pulse",
                "position_1": {"reference": "min", "fraction": 0.5},
                "position_2": {"reference": "min", "fraction": 0.9},
                "transition_ms": 300,
                "out_ms": 150,
                "back_ms": 180,
                "ease_in": 0.2,
                "ease_out": 0.2,
            },
        },
        "restore_ms": 600,
    },
}

# Per-servo Xbox controller mapping (used by XboxServoMapper on the client).
# "input" refers to a named axis from common/xbox_input.py AXIS_INDEX:
# left_stick_x, left_stick_y, right_stick_x, right_stick_y, left_trigger, right_trigger
#
# min_angle/max_angle are intentionally omitted - XboxServoMapper falls back to each
# servo's own calibrated physical limits (see servo_calibration.json).
xbox_settings = {
    "head-yaw": {"input": "left_stick_x"},
    "head-pitch": {"input": "left_stick_y", "invert": True},
    "wings": {"input": "right_stick_y", "invert": True},
    "beak": {"input": "right_trigger"},
}

_IDLE_TEMPLATE = generative_settings
_SEQUENCE_TEMPLATE = generative_sequences
_XBOX_TEMPLATE = xbox_settings

# Optional audio overrides keyed by seagull-1, seagull-2, etc.; omitted birds
# use the shared mine audio. Files must exist under sound/ on the server.
seagull_voices = {
    "seagull-1": {
        "files": [
            {"path": "sound/seagull/voice-1/mine-1.mp3", "animation_offset_ms": 0},
            {"path": "sound/seagull/voice-1/mine-2.mp3", "animation_offset_ms": 0},
            {"path": "sound/seagull/voice-1/mine-3.mp3", "animation_offset_ms": 0},
        ],
    },
    "seagull-2": {
        "files": [
            {"path": "sound/seagull/voice-2/mine-1.mp3", "animation_offset_ms": 0},
            {"path": "sound/seagull/voice-2/mine-2.mp3", "animation_offset_ms": 0},
            {"path": "sound/seagull/voice-2/mine-3.mp3", "animation_offset_ms": 0},
        ],
    },
    "seagull-3": {
        "files": [
            {"path": "sound/seagull/voice-3/mine-1.mp3", "animation_offset_ms": 0},
            {"path": "sound/seagull/voice-3/mine-2.mp3", "animation_offset_ms": 0},
            {"path": "sound/seagull/voice-3/mine-3.mp3", "animation_offset_ms": 0},
        ],
    },
}


def build_seagull_configuration(count: int) -> tuple:
    """Build independently calibrated birds on consecutive four-channel blocks."""
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 4:
        raise ValueError("SEAGULL_COUNT must be an integer from 1 to 4")
    if seagull_voices.keys() - {f"seagull-{index}" for index in range(1, 5)}:
        raise ValueError("seagull_voices keys must be seagull-1 through seagull-4")
    servos = _build_servos_data(count)
    if count == 1:
        sequences = deepcopy(_SEQUENCE_TEMPLATE)
        if "seagull-1" in seagull_voices:
            sequences["mine"]["audio"].update(deepcopy(seagull_voices["seagull-1"]))
        return servos, deepcopy(_IDLE_TEMPLATE), sequences, deepcopy(_XBOX_TEMPLATE)
    idle, sequences, xbox = {}, deepcopy(_SEQUENCE_TEMPLATE), {}
    members = {}
    for index in range(1, count + 1):
        bird = f"seagull-{index}"
        members[bird] = [f"{bird}-{part}" for part in _SERVO_TYPES]
        idle.update({f"{bird}-{part}": deepcopy(settings)
                     for part, settings in _IDLE_TEMPLATE.items()})
        xbox.update({f"{bird}-{part}": deepcopy(settings)
                     for part, settings in _XBOX_TEMPLATE.items()})
    for name, config in sequences.items():
        config["servos"] = {
            f"{bird}-{part}": deepcopy(settings)
            for bird in members
            for part, settings in _SEQUENCE_TEMPLATE[name]["servos"].items()
        }
        config["flock"] = {
            "members": members,
            "join_after_beats": [1, 2],
            "min_stagger_ms": 100,
            "max_stagger_ms": 400,
        }
        if name == "mine":
            config["flock"]["audio_by_member"] = {
                bird: deepcopy(seagull_voices[bird]) for bird in members
                if bird in seagull_voices
            }
    return servos, idle, sequences, xbox


try:
    _COUNT = int(os.getenv("SEAGULL_COUNT", "1"))
except ValueError as error:
    raise ValueError("SEAGULL_COUNT must be an integer from 1 to 4") from error

seagull_servos_data, generative_settings, generative_sequences, xbox_settings = (
    build_seagull_configuration(_COUNT)
)
