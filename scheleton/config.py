# Configuration

from common.config import mg996r_type, mg90s_type, ghs37a_type

servos_data = [

    {'type': mg996r_type, 'physical_limits': {'min': 0, 'max': 180}},  # 0

    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 1
    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 2
    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 3
    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 4
    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 5
    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 6
    {'type': mg90s_type, 'physical_limits': {'min': 0, 'max': 180}},  # 7

    {'type': ghs37a_type, 'physical_limits': {'min': 0, 'max': 180}},  # 8
    {'type': ghs37a_type, 'physical_limits': {'min': 0, 'max': 180}},  # 9
    {'type': ghs37a_type, 'physical_limits': {'min': 0, 'max': 180}},  # 10
    {'type': ghs37a_type, 'physical_limits': {'min': 0, 'max': 180}},  # 11
    {'type': ghs37a_type, 'physical_limits': {'min': 0, 'max': 180}},  # 12

    {'type': 'disabled'},
    {'type': 'disabled'},
    {'type': 'disabled'},
]
