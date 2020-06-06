from common.config import servos_data, fabric_servo_data

def get_fabric_data(servo):
    servo_type = servos_data[servo]['type']
    return fabric_servo_data[servo_type]