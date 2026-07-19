"""Seagull configuration module. Add here all servos for the animatronic."""

from common.config import MG90S_TYPE, GHS37A_TYPE
from common.servo import AniServo

seagull_servos_data = [
    # HEAD
    AniServo("head-rotation", 0, MG90S_TYPE, 40, 140, 90),
    AniServo("head-up-down", 1, MG90S_TYPE, 20, 155, 90),
    # WINGS
    AniServo("wings", 2, MG90S_TYPE, 15, 180, 145),
    # MANDIBLE
    AniServo("mandible", 3, GHS37A_TYPE, 40, 70, 45),
]
