# Configuration

from common.config import mg996r_type, mg90s_type, ghs37a_type
from common.servo import AniServo

servos_data: list[AniServo] = [
    AniServo(0, mg996r_type, 0, 180, 90),

    AniServo(1, mg90s_type, 0, 180, 90),
    AniServo(2, mg90s_type, 0, 180, 90),
    AniServo(3, mg90s_type, 0, 180, 90),
    AniServo(4, mg90s_type, 0, 180, 90),
    AniServo(5, mg90s_type, 0, 180, 90),
    AniServo(6, mg90s_type, 0, 180, 90),
    AniServo(7, mg90s_type, 0, 180, 90),

    AniServo(8, ghs37a_type, 0, 180, 90),
    AniServo(9, ghs37a_type, 0, 180, 90),
    AniServo(10, ghs37a_type, 0, 180, 90),
    AniServo(11, ghs37a_type, 0, 180, 90),
    AniServo(12, ghs37a_type, 0, 180, 90),
]
