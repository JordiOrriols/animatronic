from common.config import phonemes_data
from common.servo import move_servo_to_angle

def adopt_phoneme(kit, phoneme):
    current_phoneme = phonemes_data[phoneme]
    print('\n\n\n', 'Adopting phoneme', phoneme)
    for data in current_phoneme:
        print('\n', 'Phoneme data', data)
        move_servo_to_angle(kit, data.servo, data.angle)