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

# Per-servo generative configuration (all values in ms or degrees where noted)
# This file uses only per-servo settings as requested.
generative_settings = {
    "head-rotation": {
        "min_duration_ms": 300,
        "max_duration_ms": 1200,
        "min_wait_ms": 800,
        "max_wait_ms": 2500,
        "min_angle": 50,
        "max_angle": 130,
        "random_factor": 0.8,
        "ease_in": 0.2,
        "ease_out": 0.2,
        "return_to_rest": False,
    },
    "head-up-down": {
        "min_duration_ms": 300,
        "max_duration_ms": 900,
        "min_wait_ms": 600,
        "max_wait_ms": 2000,
        "min_angle": 30,
        "max_angle": 140,
        "random_factor": 0.7,
        "ease_in": 0.15,
        "ease_out": 0.15,
        "return_to_rest": False,
    },
    "wings": {
        "min_duration_ms": 200,
        "max_duration_ms": 600,
        "min_wait_ms": 400,
        "max_wait_ms": 1200,
        "min_angle": 20,
        "max_angle": 160,
        "random_factor": 1.0,
        "ease_in": 0.0,
        "ease_out": 0.0,
        "return_to_rest": True,
        "rest_hold_ms": 150,
    },
}
