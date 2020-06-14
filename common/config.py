# Configuration

big_type = 'big'
blue_type = 'blue'

fabric_servo_data = {
    big_type: {'pulse_width': {'min': 600, 'max': 2400}, 'actuation_range': 180},
    blue_type: {'pulse_width': {'min': 600,
                                'max': 2400}, 'actuation_range': 180}
}

servos_data = [
    {'type': big_type, 'physical_limits': {'min': 70, 'max': 90},
        'connection': {'servo': 1, 'type': 'inverted'}},  # 0
    {'type': big_type, 'physical_limits': {'min': 90, 'max': 110}},  # 1

    {'type': blue_type, 'physical_limits': {'min': 40, 'max': 155}},  # 2
    {'type': blue_type, 'physical_limits': {'min': 30, 'max': 135}},  # 3
    {'type': blue_type, 'physical_limits': {'min': 15, 'max': 125}},  # 4
    {'type': blue_type, 'physical_limits': {'min': 30, 'max': 150}},  # 5
    {'type': blue_type, 'physical_limits': {'min': 45, 'max': 110}},  # 6
    {'type': blue_type, 'physical_limits': {'min': 85, 'max': 135}},  # 7
    {'type': blue_type, 'physical_limits': {'min': 30, 'max': 95}},  # 8

    {'type': 'disabled'},

    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 10
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 11
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 12
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 13
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 14
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 15
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