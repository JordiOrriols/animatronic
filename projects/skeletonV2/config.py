# Configuration

from common.config import MG996R_TYPE, MG90S_TYPE, GHS37A_TYPE
from common.servo import AniServo

skeletonV2_servos_data = [
    # BODY
    AniServo("body-flexion", 0, MG996R_TYPE, 0, 180, 70),  # Arreglar
    AniServo("body-rotation", 1, MG90S_TYPE, 0, 180, 145),  # Arreglar
    # HEAD
    AniServo("head-rotation", 2, MG90S_TYPE, 0, 180, 90),
    AniServo("head-flexion-left", 3, MG90S_TYPE, 0, 180, 90),
    AniServo("head-flexion-right", 4, MG90S_TYPE, 0, 180, 90),
    # SHOULDER
    AniServo("shoulder-left-flexion", 5, MG90S_TYPE, 0, 180, 145),
    AniServo("shoulder-right-flexion", 6, MG90S_TYPE, 0, 180, 45),  # No va
    AniServo("shoulder-left-rotation", 7, MG90S_TYPE, 0, 180, 90),
    AniServo("shoulder-right-rotation", 8, MG90S_TYPE, 0, 180, 100),
    # ARM
    AniServo("arm-left-rotation", 9, GHS37A_TYPE, 0, 180, 100),
    AniServo("arm-right-rotation", 10, GHS37A_TYPE, 0, 180, 90),
    AniServo("arm-left-flexion", 11, GHS37A_TYPE, 0, 180, 100),
    AniServo("arm-right-flexion", 12, GHS37A_TYPE, 0, 180, 90),
    # HAND
    AniServo("hand-left-rotation", 13, GHS37A_TYPE, 0, 180, 90),
    AniServo("hand-right-rotation", 14, GHS37A_TYPE, 0, 180, 90),
    # MANDIBLE
    AniServo("mandible", 15, GHS37A_TYPE, 0, 180, 90),
]

servos_data_done = [
    AniServo("body-flexion", 0, MG996R_TYPE, 40, 120, 70),  # Arreglar
    AniServo("body-rotation", 1, MG90S_TYPE, 50, 145, 145),  # Arreglar
    AniServo("head-rotation", 2, MG90S_TYPE, 45, 140, 90),
    AniServo("head-flexion-left", 3, MG90S_TYPE, 70, 140, 90),
    AniServo("head-flexion-right", 4, MG90S_TYPE, 65, 140, 90),
    AniServo("shoulder-left-flexion", 5, MG90S_TYPE, 15, 165, 145),
    AniServo("shoulder-right-flexion", 6, MG90S_TYPE, 10, 170, 45),  # No va
    AniServo("shoulder-left-rotation", 7, MG90S_TYPE, 5, 90, 90),
    AniServo("shoulder-right-rotation", 8, MG90S_TYPE, 95, 180, 100),
    AniServo("arm-left-rotation", 9, GHS37A_TYPE, 80, 150, 100),
    AniServo("arm-right-rotation", 10, GHS37A_TYPE, 50, 130, 90),
    AniServo("arm-left-flexion", 11, GHS37A_TYPE, 80, 150, 100),
    AniServo("arm-right-flexion", 12, GHS37A_TYPE, 50, 130, 90),
    AniServo("hand-left-rotation", 13, GHS37A_TYPE, 0, 155, 90),
    AniServo("hand-right-rotation", 14, GHS37A_TYPE, 0, 155, 90),
    AniServo("mandible", 15, GHS37A_TYPE, 60, 110, 90),
]
