# Configuration

from common.config import mg996r_type, mg92b_type

servos_data = [
    {'type': mg996r_type, 'physical_limits': {'min': 70, 'max': 90},
        'connection': {'servo': 1, 'type': 'inverted'}},  # 0
    {'type': mg996r_type, 'physical_limits': {'min': 90, 'max': 110}},  # 1

    {'type': mg92b_type, 'physical_limits': {'min': 40, 'max': 155}},  # 2
    {'type': mg92b_type, 'physical_limits': {'min': 30, 'max': 135}},  # 3
    {'type': mg92b_type, 'physical_limits': {'min': 15, 'max': 125}},  # 4
    {'type': mg92b_type, 'physical_limits': {'min': 30, 'max': 150}},  # 5
    {'type': mg92b_type, 'physical_limits': {'min': 45, 'max': 110}},  # 6
    {'type': mg92b_type, 'physical_limits': {'min': 85, 'max': 135}},  # 7
    {'type': mg92b_type, 'physical_limits': {'min': 30, 'max': 95}},  # 8

    {'type': 'disabled'},

    {'type': mg92b_type, 'physical_limits': {'min': 0, 'max': 180}},  # 10
    {'type': mg92b_type, 'physical_limits': {'min': 0, 'max': 180}},  # 11
    {'type': mg92b_type, 'physical_limits': {'min': 0, 'max': 180}},  # 12
    {'type': mg92b_type, 'physical_limits': {'min': 0, 'max': 180}},  # 13
    {'type': mg92b_type, 'physical_limits': {'min': 0, 'max': 180}},  # 14
    {'type': mg92b_type, 'physical_limits': {'min': 0, 'max': 180}},  # 15
]

phonemes_data = {
    'RELAX': [
        { 'servo': 0, 'angle': 70},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 30},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 150},
        { 'servo': 6, 'angle': 110},
        { 'servo': 7, 'angle': 85},
        { 'servo': 8, 'angle': 95},
    ],
    'A': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 135},
        { 'servo': 3, 'angle': 135},
        { 'servo': 4, 'angle': 45},
        { 'servo': 5, 'angle': 30},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 85},
        { 'servo': 8, 'angle': 80},
    ],
    'O': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 70},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 100},
        { 'servo': 6, 'angle': 110},
        { 'servo': 7, 'angle': 85},
        { 'servo': 8, 'angle': 95},
    ],
    'B': [
        { 'servo': 0, 'angle': 80},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 100},
        { 'servo': 6, 'angle': 80},
        { 'servo': 7, 'angle': 105},
        { 'servo': 8, 'angle': 95},
    ],
    'G': [
        { 'servo': 0, 'angle': 75},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 110},
        { 'servo': 6, 'angle': 70},
        { 'servo': 7, 'angle': 105},
        { 'servo': 8, 'angle': 75},
    ],
    'S': [
        { 'servo': 0, 'angle': 70},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 60},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 110},
        { 'servo': 6, 'angle': 95},
        { 'servo': 7, 'angle': 105},
        { 'servo': 8, 'angle': 85},
    ],
    'Th': [
        { 'servo': 0, 'angle': 70},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 60},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 110},
        { 'servo': 6, 'angle': 80},
        { 'servo': 7, 'angle': 135},
        { 'servo': 8, 'angle': 85},
    ],
    'L': [
        { 'servo': 0, 'angle': 70},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 60},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 110},
        { 'servo': 6, 'angle': 80},
        { 'servo': 7, 'angle': 135},
        { 'servo': 8, 'angle': 85},
    ],
    'F': [
        { 'servo': 0, 'angle': 70},
        { 'servo': 2, 'angle': 155},
        { 'servo': 3, 'angle': 60},
        { 'servo': 4, 'angle': 15},
        { 'servo': 5, 'angle': 110},
        { 'servo': 6, 'angle': 85},
        { 'servo': 7, 'angle': 85},
        { 'servo': 8, 'angle': 85},
    ]
}