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
#
# min_angle/max_angle are intentionally omitted - GenerativeMovement falls back to
# each servo's own calibrated physical limits (see servo_calibration.json).
generative_settings = {
    "head-yaw": {
        "min_duration_ms": 300,
        "max_duration_ms": 1200,
        "min_wait_ms": 800,
        "max_wait_ms": 2500,
        "random_factor": 0.8,
        "ease_in": 0.2,
        "ease_out": 0.2,
        "return_to_rest": False,
    },
    "head-pitch": {
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
