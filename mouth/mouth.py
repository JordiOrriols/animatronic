from common.config import phonemes_data
from common.servo import move_servo_to_angle

def adopt_phoneme(kit, phoneme):

    if phoneme not in phonemes_data.keys():
        print('Not defined phoneme', phoneme)
        return

    current_phoneme = phonemes_data[phoneme]
    print('Adopting phoneme', phoneme)
    for data in current_phoneme:
        print('Phoneme data', data)
        move_servo_to_angle(kit, data['servo'], data['angle'])