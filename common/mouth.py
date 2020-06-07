from common.config import phonemes_data
from common.servo import move_servo_to_angle

def adopt_phoneme(kit, phoneme):
    current_phoneme = phonemes_data[phoneme]
    for data in current_phoneme:
        move_servo_to_angle(kit, data.servo, data.angle)