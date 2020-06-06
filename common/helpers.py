from common.config import servos_data, fabric_servo_data
from common.validators import validate_servo, validate_servo_position

def get_fabric_data(servo):
    servo = validate_servo(servo)
    servo_type = servos_data[servo]['type']
    return fabric_servo_data[servo_type]