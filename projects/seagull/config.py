"""Seagull configuration module. Add here all servos for the animatronic."""

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


def _build_servos_data():
    """Build every AniServo from calibration data, falling back to sane defaults
    for any servo not yet present in servo_calibration.json."""
    calibration = load_calibration("seagull")
    servos = []
    for name, (pin, servo_type) in _SERVO_TYPES.items():
        limits = calibration.get(name)
        if limits is None:
            logger.warning(f"No calibration data for servo '{name}'; using defaults.")
            limits = _DEFAULT_LIMITS
        servos.append(
            AniServo(name, pin, servo_type, limits["min"], limits["max"], limits["rest"])
        )
    return servos


seagull_servos_data = _build_servos_data()

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
                {"path": "sound/seagull/mine-1.mp3", "animation_offset_ms": 0},
                {"path": "sound/seagull/mine-2.mp3", "animation_offset_ms": 0},
                {"path": "sound/seagull/mine-3.mp3", "animation_offset_ms": 0},
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
