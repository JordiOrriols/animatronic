# Configuration

from common.config import mg996r_type, mg90s_type, ghs37a_type
from common.servo import AniServo

servos_data: list[AniServo] = [
    AniServo('ReplaceNameServo', 0, mg996r_type, 0, 180, 90),

    AniServo('TestServo', 1, mg90s_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 2, mg90s_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 3, mg90s_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 4, mg90s_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 5, mg90s_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 6, mg90s_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 7, mg90s_type, 0, 180, 90),

    AniServo('ReplaceNameServo', 8, ghs37a_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 9, ghs37a_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 10, ghs37a_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 11, ghs37a_type, 0, 180, 90),
    AniServo('ReplaceNameServo', 12, ghs37a_type, 0, 180, 90),
]
