"""Configuration module to expose constants for different servos."""
# Configuration

MG996R_TYPE = "MG996R"  # Standard Servo
MG92B_TYPE = "MG92B"  # Blue Metal Micro Servo
MG90S_TYPE = "MG90S"  # Purple Metal Micro Servo
GHS37A_TYPE = "GHS37A"  # Nano Servo

fabric_servo_data = {
    MG996R_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
    MG92B_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
    MG90S_TYPE: {"pulse_width": {"min": 600, "max": 2400}, "actuation_range": 180},
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
    "auto": "automatic-mode",
    "stop": "stop",
    "finished": "animation-finished",
    "exit": "exit",
}
