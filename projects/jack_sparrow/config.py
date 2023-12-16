"""Jack Sparrow configuration module. Add here all servos for the animatronic."""

from common.config import MG996R_TYPE
from common.servo import AniServo

jack_sparrow_servos_data = [AniServo("body-flexion", 0, MG996R_TYPE, 0, 180, 70)]
