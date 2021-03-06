from common.servo import move_servo_to_angle, initialize_servos
from common.helpers import get_fabric_data
from common.validators import validate_controllable_servo, validate_servo, validate_position, validate_servo_position
from common.config import fabric_servo_data, servos_data, phonemes_data
from common.mouth import adopt_phoneme