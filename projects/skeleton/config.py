# Configuration

from common.config import MG996R_TYPE, MG90S_TYPE, GHS37A_TYPE
from common.servo import AniServo

skeleton_servos_data = [
    # BODY
    AniServo("body-flexion", 0, MG996R_TYPE, 55, 120, 80),
    AniServo("body-rotation", 1, MG90S_TYPE, 45, 145, 95),
    # HEAD
    AniServo("head-rotation", 2, MG90S_TYPE, 40, 155, 90),
    AniServo("head-flexion", 3, MG90S_TYPE, 60, 140, 90),
    # SHOULDER
    AniServo("shoulder-left-flexion", 4, MG90S_TYPE, 10, 170, 140),
    AniServo("shoulder-right-flexion", 5, MG90S_TYPE, 10, 170, 45),
    AniServo("shoulder-left-rotation", 6, MG90S_TYPE, 5, 90, 90),
    AniServo("shoulder-right-rotation", 7, MG90S_TYPE, 95, 180, 100),
    # ARM
    AniServo("arm-left-rotation", 8, GHS37A_TYPE, 80, 150, 100),
    AniServo("arm-right-rotation", 9, GHS37A_TYPE, 50, 130, 90),
    # HAND
    AniServo("hand-left-rotation", 10, GHS37A_TYPE, 0, 155, 90),
    AniServo("hand-right-rotation", 11, GHS37A_TYPE, 0, 155, 90),
    # MANDIBLE
    AniServo("mandible", 12, GHS37A_TYPE, 60, 110, 90),
]
