from mouth.config import phonemes_data
from common.servo import AniServo


def adopt_phoneme(phoneme: str, servos_data: list[AniServo]):

    if phoneme not in phonemes_data.keys():
        print('Not defined phoneme', phoneme)
        return

    current_phoneme = phonemes_data[phoneme]
    print('Adopting phoneme', phoneme)

    for data in current_phoneme:
        print('Phoneme data', data)
        for servo in servos_data:
            if(servo.pin == data['servo']):
                servo.move_to_angle(data['angle'])
