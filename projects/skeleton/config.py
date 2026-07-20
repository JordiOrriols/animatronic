"""Skeleton configuration module. Add here all servos for the animatronic."""

from common.config import MG996R_TYPE, MG90S_TYPE, GHS37A_TYPE
from common.servo import AniServo

skeleton_servos_data = [
    # BODY
    AniServo("body-flexion", 0, MG996R_TYPE, 50, 115, 75),
    AniServo("body-rotation", 1, MG90S_TYPE, 0, 180, 95),
    # HEAD
    AniServo("head-rotation", 2, MG90S_TYPE, 40, 140, 90),
    AniServo("head-flexion-left", 3, MG90S_TYPE, 20, 155, 90),
    AniServo("head-flexion-right", 4, MG90S_TYPE, 45, 170, 90),
    # SHOULDER
    AniServo("shoulder-left-flexion", 5, MG90S_TYPE, 15, 180, 145),
    AniServo("shoulder-right-flexion", 6, MG90S_TYPE, 10, 170, 45),  # Replace Servo
    AniServo("shoulder-left-rotation", 7, MG90S_TYPE, 15, 120, 120),
    AniServo("shoulder-right-rotation", 8, MG90S_TYPE, 50, 165, 50),
    # ARM
    AniServo("arm-left-rotation", 9, GHS37A_TYPE, 80, 160, 100),  # Refine Better
    AniServo("arm-right-rotation", 10, GHS37A_TYPE, 0, 70, 10),  # Move Limit Physically
    AniServo("arm-left-flexion", 11, GHS37A_TYPE, 40, 140, 70),
    AniServo("arm-right-flexion", 12, GHS37A_TYPE, 25, 130, 130),
    # HAND
    AniServo("hand-left-rotation", 13, GHS37A_TYPE, 0, 155, 90),
    AniServo("hand-right-rotation", 14, GHS37A_TYPE, 0, 155, 90),
    # MANDIBLE
    AniServo("mandible", 15, GHS37A_TYPE, 40, 70, 45),
]

# Per-servo Xbox controller mapping (used by XboxServoMapper on the client).
# "input" refers to a named axis from common/xbox_controller.py AXIS_INDEX:
# left_stick_x, left_stick_y, right_stick_x, right_stick_y, left_trigger, right_trigger
#
# An Xbox controller only exposes 6 usable analog inputs, so this maps a fixed subset
# of 6 servos out of the 16 available. There is no "bank switching" - adjust which
# servo goes on which axis below if you want to control different servos.
xbox_settings = {
    "head-rotation": {"input": "left_stick_x", "min_angle": 40, "max_angle": 140},
    "body-flexion": {"input": "left_stick_y", "invert": True, "min_angle": 50, "max_angle": 115},
    "body-rotation": {"input": "right_stick_x"},
    "head-flexion-left": {"input": "right_stick_y", "invert": True},
    "mandible": {"input": "left_trigger", "min_angle": 40, "max_angle": 70},
    "arm-right-flexion": {"input": "right_trigger", "min_angle": 25, "max_angle": 130},
}

