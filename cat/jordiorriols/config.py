# Configuration

fabric_servo_data = {
    'big': { 'pulse_width': { 'min': 600, 'max': 2400}, 'actuation_range': 180},
    'blue': { 'pulse_width': { 'min': 600, 'max': 2400}, 'actuation_range': 180}
}

servos_data = [
    {'type': 'big', 'physical_limits': {'min': 0, 'max': 180}}, #0
    {'type': 'big', 'physical_limits': {'min': 0, 'max': 180}}, #1

    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #2
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #3
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #4
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #5
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #6
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #7
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #8
]