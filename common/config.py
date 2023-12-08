# Configuration

mg996r_type = 'MG996R'  # Standard Servo
mg92b_type = 'MG92B'  # Blue Metal Micro Servo
mg90s_type = 'MG90S'  # Purple Metal Micro Servo
ghs37a_type = 'GHS37A'  # Nano Servo

fabric_servo_data = {
    mg996r_type: {'pulse_width': {'min': 600, 'max': 2400}, 'actuation_range': 180},
    mg92b_type: {'pulse_width': {'min': 600, 'max': 2400}, 'actuation_range': 180},
    mg90s_type: {'pulse_width': {'min': 600, 'max': 2400}, 'actuation_range': 180},
    ghs37a_type: {'pulse_width': {'min': 600, 'max': 2400}, 'actuation_range': 180}
}
