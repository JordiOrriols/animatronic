"""Skeleton V2 configuration module. Add here all servos for the animatronic."""

from common.config import MG996R_TYPE, MG90S_TYPE, GHS37A_TYPE
from common.servo import AniServo

skeleton_v2_servos_data = [
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
