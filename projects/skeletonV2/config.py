# Configuration

from common.config import mg996r_type, mg90s_type, ghs37a_type
from common.servo import AniServo

skeletonV2_servos_data = [
    # BODY
    AniServo("body-flexion", 0, mg996r_type, 0, 180, 70),  # Arreglar
    AniServo("body-rotation", 1, mg90s_type, 0, 180, 145),  # Arreglar
    # HEAD
    AniServo("head-rotation", 2, mg90s_type, 0, 180, 90),
    AniServo("head-flexion-left", 3, mg90s_type, 0, 180, 90),
    AniServo("head-flexion-right", 4, mg90s_type, 0, 180, 90),
    # SHOULDER
    AniServo("shoulder-left-flexion", 5, mg90s_type, 0, 180, 145),
    AniServo("shoulder-right-flexion", 6, mg90s_type, 0, 180, 45),  # No va
    AniServo("shoulder-left-rotation", 7, mg90s_type, 0, 180, 90),
    AniServo("shoulder-right-rotation", 8, mg90s_type, 0, 180, 100),
    # ARM
    AniServo("arm-left-rotation", 9, ghs37a_type, 0, 180, 100),
    AniServo("arm-right-rotation", 10, ghs37a_type, 0, 180, 90),
    AniServo("arm-left-flexion", 11, ghs37a_type, 0, 180, 100),
    AniServo("arm-right-flexion", 12, ghs37a_type, 0, 180, 90),
    # HAND
    AniServo("hand-left-rotation", 13, ghs37a_type, 0, 180, 90),
    AniServo("hand-right-rotation", 14, ghs37a_type, 0, 180, 90),
    # MANDIBLE
    AniServo("mandible", 15, ghs37a_type, 0, 180, 90),
]

servos_data_done = [
    AniServo("body-flexion", 0, mg996r_type, 40, 120, 70),  # Arreglar
    AniServo("body-rotation", 1, mg90s_type, 50, 145, 145),  # Arreglar
    AniServo("head-rotation", 2, mg90s_type, 45, 140, 90),
    AniServo("head-flexion-left", 3, mg90s_type, 70, 140, 90),
    AniServo("head-flexion-right", 4, mg90s_type, 65, 140, 90),
    AniServo("shoulder-left-flexion", 5, mg90s_type, 15, 165, 145),
    AniServo("shoulder-right-flexion", 6, mg90s_type, 10, 170, 45),  # No va
    AniServo("shoulder-left-rotation", 7, mg90s_type, 5, 90, 90),
    AniServo("shoulder-right-rotation", 8, mg90s_type, 95, 180, 100),
    AniServo("arm-left-rotation", 9, ghs37a_type, 80, 150, 100),
    AniServo("arm-right-rotation", 10, ghs37a_type, 50, 130, 90),
    AniServo("arm-left-flexion", 11, ghs37a_type, 80, 150, 100),
    AniServo("arm-right-flexion", 12, ghs37a_type, 50, 130, 90),
    AniServo("hand-left-rotation", 13, ghs37a_type, 0, 155, 90),
    AniServo("hand-right-rotation", 14, ghs37a_type, 0, 155, 90),
    AniServo("mandible", 15, ghs37a_type, 60, 110, 90),
]
