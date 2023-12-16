"""Mouth module. Here you have specific code for mouth."""

from projects.mouth.config import phonemes_data
from common.servo import AniServo


def adopt_phoneme(phoneme: str, servos_data: list[AniServo]):
    """Call this function to adopt a phoneme on all the mouth servos."""

    if phoneme not in phonemes_data.keys():
        print("Not defined phoneme", phoneme)
        return

    current_phoneme = phonemes_data[phoneme]
    print("Adopting phoneme", phoneme)

    for data in current_phoneme:
        print("Phoneme data", data)
        for servo in servos_data:
            if servo.get_pin() == data["servo"]:
                servo.move_to_angle(data["angle"])
