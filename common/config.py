# Configuration

big_type = 'big'
blue_type = 'blue'

fabric_servo_data = {
    big_type: {'pulse_width': {'min': 600, 'max': 2400}, 'actuation_range': 180},
    blue_type: {'pulse_width': {'min': 600,
                                'max': 2400}, 'actuation_range': 180}
}

servos_data = [
    {'type': big_type, 'physical_limits': {'min': 0, 'max': 180},
        'connection': {'servo': 1, 'type': 'inverted'}},  # 0
    {'type': big_type, 'physical_limits': {'min': 0, 'max': 180}},  # 1

    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 2
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}},  # 3
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
    'A': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'O': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'B': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'G': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'S': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'Th': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'L': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ],
    'F': [
        { 'servo': 0, 'angle': 90},
        { 'servo': 2, 'angle': 90},
        { 'servo': 3, 'angle': 90},
        { 'servo': 4, 'angle': 90},
        { 'servo': 5, 'angle': 90},
        { 'servo': 6, 'angle': 90},
        { 'servo': 7, 'angle': 90},
        { 'servo': 8, 'angle': 90},
    ]
}