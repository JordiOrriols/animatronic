"""Skeleton configuration module. Add here all servos for the animatronic."""

from common.calibration import load_calibration
from common.config import MG996R_TYPE, MG90S_TYPE, GHS37A_TYPE
from common.logger import Logger
from common.servo import AniServo

logger = Logger("SkeletonConfig")

# (pin, servo_type) for every servo on this animatronic. Min/max/rest limits are
# calibration data, sourced from servo_calibration.json (see common/calibration.py)
# and kept up to date via the server's "Calibrate" menu option.
_SERVO_TYPES = {
    # BODY
    "body-flexion": (0, MG996R_TYPE),
    "body-rotation": (1, MG90S_TYPE),
    # HEAD
    "head-rotation": (2, MG90S_TYPE),
    "head-flexion-left": (3, MG90S_TYPE),
    "head-flexion-right": (4, MG90S_TYPE),
    # SHOULDER
    "shoulder-left-flexion": (5, MG90S_TYPE),
    "shoulder-right-flexion": (6, MG90S_TYPE),  # Replace Servo
    "shoulder-left-rotation": (7, MG90S_TYPE),
    "shoulder-right-rotation": (8, MG90S_TYPE),
    # ARM
    "arm-left-rotation": (9, GHS37A_TYPE),  # Refine Better
    "arm-right-rotation": (10, GHS37A_TYPE),  # Move Limit Physically
    "arm-left-flexion": (11, GHS37A_TYPE),
    "arm-right-flexion": (12, GHS37A_TYPE),
    # HAND
    "hand-left-rotation": (13, GHS37A_TYPE),
    "hand-right-rotation": (14, GHS37A_TYPE),
    # MANDIBLE
    "mandible": (15, GHS37A_TYPE),
}

_DEFAULT_LIMITS = {"min": 0, "max": 180, "rest": 90}


def _build_servos_data():
    """Build every AniServo from calibration data, falling back to sane defaults
    for any servo not yet present in servo_calibration.json."""
    calibration = load_calibration("skeleton")
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


skeleton_servos_data = _build_servos_data()

# Per-servo Xbox controller mapping (used by XboxServoMapper on the client).
# "input" refers to a named axis from common/xbox_input.py AXIS_INDEX:
# left_stick_x, left_stick_y, right_stick_x, right_stick_y, left_trigger, right_trigger
#
# An Xbox controller only exposes 6 usable analog inputs, so this maps a fixed subset
# of 6 servos out of the 16 available. There is no "bank switching" - adjust which
# servo goes on which axis below if you want to control different servos.
#
# min_angle/max_angle are intentionally omitted - XboxServoMapper falls back to each
# servo's own calibrated physical limits (see servo_calibration.json).
xbox_settings = {
    "head-rotation": {"input": "left_stick_x"},
    "body-flexion": {"input": "left_stick_y", "invert": True},
    "body-rotation": {"input": "right_stick_x"},
    "head-flexion-left": {"input": "right_stick_y", "invert": True},
    "mandible": {"input": "left_trigger"},
    "arm-right-flexion": {"input": "right_trigger"},
}
