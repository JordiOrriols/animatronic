"""Configuration module to expose constants for different servos."""

# Configuration

MG996R_TYPE = "MG996R"  # Standard Servo
MG92B_TYPE = "MG92B"  # Blue Metal Micro Servo
MG90S_TYPE = "MG90S"  # Purple Metal Micro Servo, 180 degree version
MG90S_90_TYPE = "MG90S-90"  # Purple Metal Micro Servo, 90 degree version
TS90MD_TYPE = "TS90MD"  # Purple Metal Micro Servo, 180 degree version
GHS37A_TYPE = "GHS37A"  # Nano Servo

fabric_servo_data = {
    MG996R_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
    MG92B_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
    MG90S_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
    MG90S_90_TYPE: {"pulse_width": {"min": 1000, "max": 2000}, "actuation_range": 90},
    TS90MD_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
    GHS37A_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
}

DISCOVERY_PORT = 50000
DISCOVERY_MAGIC = "jordiorriols-animatronic@"

WEBSOCKET_PORT = 8765
WEBSOCKET_MESSAGES = {
    "connected": "client-connected",
    "ready": "client-ready",
    "waiting": "server-waiting",
    "play": "play-animation",
    "finished": "animation-finished",
    "auto-start": "automatic-mode-start",
    "auto-stop": "automatic-mode-stop",
    "calibrate-move": "calibrate-move",
    "calibrate-save": "calibrate-save",
    "calibrate-commit": "calibrate-commit",
    "evaluate": "evaluate",
    "standby": "standby",
    "reboot": "reboot",
    "exit": "exit",
    "xbox-start": "xbox-controller-start",
    "xbox-position": "xbox-controller-position",
    "xbox-stop": "xbox-controller-stop",
}
