# Configuration

big_type = 'big'
blue_type = 'blue'

fabric_servo_data = {
    big_type: { 'pulse_width': { 'min': 600, 'max': 2400}, 'actuation_range': 180},
    blue_type: { 'pulse_width': { 'min': 600, 'max': 2400}, 'actuation_range': 180}
}

servos_data = [
    {'type': big_type, 'physical_limits': {'min': 0, 'max': 180}, 'pair': 1}, #0
    {'type': big_type, 'physical_limits': {'min': 0, 'max': 180}, 'pair': 0}, #1

    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #2
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #3
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #4
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #5
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #6
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #7
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #8

    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #
    
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #10
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #11
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #12
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #13
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #14
    {'type': blue_type, 'physical_limits': {'min': 0, 'max': 180}}, #15
]