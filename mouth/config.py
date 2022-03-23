# Configuration

from common.config import mg996r_type, mg92b_type
from common.servo import AniServo

servos_data: list[AniServo] = [

    AniServo(0, mg996r_type, 70, 90)
    .connect(AniServo(1, mg996r_type, 90, 110)),  

    AniServo(2, mg92b_type, 40, 155), 
    AniServo(3, mg92b_type, 30, 135), 
    AniServo(4, mg92b_type, 15, 125), 
    AniServo(5, mg92b_type, 30, 150), 
    AniServo(6, mg92b_type, 45, 110), 
    AniServo(7, mg92b_type, 85, 135), 
    AniServo(8, mg92b_type, 30, 95), 

    AniServo(10, mg92b_type, 0, 180),  
    AniServo(11, mg92b_type, 0, 180),  
    AniServo(12, mg92b_type, 0, 180),  
    AniServo(13, mg92b_type, 0, 180),  
    AniServo(14, mg92b_type, 0, 180),  
    AniServo(15, mg92b_type, 0, 180),  
]

phonemes_data = {
    'RELAX': [
        {'servo': 0, 'angle': 70},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 30},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 150},
        {'servo': 6, 'angle': 110},
        {'servo': 7, 'angle': 85},
        {'servo': 8, 'angle': 95},
    ],
    'A': [
        {'servo': 0, 'angle': 90},
        {'servo': 2, 'angle': 135},
        {'servo': 3, 'angle': 135},
        {'servo': 4, 'angle': 45},
        {'servo': 5, 'angle': 30},
        {'servo': 6, 'angle': 90},
        {'servo': 7, 'angle': 85},
        {'servo': 8, 'angle': 80},
    ],
    'O': [
        {'servo': 0, 'angle': 90},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 70},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 100},
        {'servo': 6, 'angle': 110},
        {'servo': 7, 'angle': 85},
        {'servo': 8, 'angle': 95},
    ],
    'B': [
        {'servo': 0, 'angle': 80},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 90},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 100},
        {'servo': 6, 'angle': 80},
        {'servo': 7, 'angle': 105},
        {'servo': 8, 'angle': 95},
    ],
    'G': [
        {'servo': 0, 'angle': 75},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 90},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 110},
        {'servo': 6, 'angle': 70},
        {'servo': 7, 'angle': 105},
        {'servo': 8, 'angle': 75},
    ],
    'S': [
        {'servo': 0, 'angle': 70},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 60},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 110},
        {'servo': 6, 'angle': 95},
        {'servo': 7, 'angle': 105},
        {'servo': 8, 'angle': 85},
    ],
    'Th': [
        {'servo': 0, 'angle': 70},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 60},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 110},
        {'servo': 6, 'angle': 80},
        {'servo': 7, 'angle': 135},
        {'servo': 8, 'angle': 85},
    ],
    'L': [
        {'servo': 0, 'angle': 70},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 60},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 110},
        {'servo': 6, 'angle': 80},
        {'servo': 7, 'angle': 135},
        {'servo': 8, 'angle': 85},
    ],
    'F': [
        {'servo': 0, 'angle': 70},
        {'servo': 2, 'angle': 155},
        {'servo': 3, 'angle': 60},
        {'servo': 4, 'angle': 15},
        {'servo': 5, 'angle': 110},
        {'servo': 6, 'angle': 85},
        {'servo': 7, 'angle': 85},
        {'servo': 8, 'angle': 85},
    ]
}
