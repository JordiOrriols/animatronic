# Configuration

from common.config import mg996r_type, mg90s_type, ghs37a_type
from common.servo import AniServo

servos_data = [
    AniServo('body-flexion', 0, mg996r_type, 35, 120, 80),

    AniServo('body-rotation', 1, mg90s_type, 45, 145, 95),

    AniServo('head-rotation', 2, mg90s_type, 40, 155, 90),

    AniServo('head-flexion-left', 3, mg90s_type, 60, 140, 90),
    AniServo('head-flexion-right', 4, mg90s_type, 60, 140, 90),

    AniServo('shoulder-left-flexion', 5, mg90s_type, 10, 170, 140),
    AniServo('shoulder-right-flexion', 6, mg90s_type, 10, 170, 45),
    AniServo('shoulder-left-rotation', 7, mg90s_type, 5, 90, 90),
    AniServo('shoulder-right-rotation', 8, mg90s_type, 95, 180, 100),

    AniServo('arm-left-rotation', 9, ghs37a_type, 80, 150, 100),
    AniServo('arm-right-rotation', 10, ghs37a_type, 50, 130, 90),
    AniServo('arm-left-flexion', 11, ghs37a_type, 80, 150, 100),
    AniServo('arm-right-flexion', 12, ghs37a_type, 50, 130, 90),

    AniServo('hand-left-rotation', 13, ghs37a_type, 0, 155, 90),
    AniServo('hand-right-rotation', 14, ghs37a_type, 0, 155, 90),

    AniServo('mandible', 15, ghs37a_type, 60, 110, 90)
]