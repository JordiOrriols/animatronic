import time
import random
from adafruit_servokit import ServoKit  # Asegúrate de tener instalada esta biblioteca

# Aquí deberías tener definidas las variables mg996r_type, mg90s_type y ghs37a_type
# ...

# Aquí deberías tener definidas las clases AniServo, fabric_servo_data y initialize_servos
# ...

def generate_smooth_movement(servo, target_position, duration=1.0, steps=50):
    current_position = servo.__kit.servo[servo.getPin()].angle
    angle_change = (target_position - current_position) / steps

    for _ in range(steps):
        current_position += angle_change
        servo.move_to_angle(int(current_position))
        time.sleep(duration / steps)

def generate_random_smooth_movement(servo, duration=1.0, steps=50):
    min_limit = servo.getPhysicalLimitMin()
    max_limit = servo.getPhysicalLimitMax()

    # Generar una posición aleatoria dentro de los límites físicos del servo
    random_position = random.randint(min_limit, max_limit)

    # Mover suavemente el servo a la posición aleatoria
    generate_smooth_movement(servo, random_position, duration, steps)

def perform_random_smooth_movements(servos, duration=1.0, steps=50):
    while True:
        # Seleccionar un servo aleatorio
        random_servo = random.choice(servos)

        # Generar y aplicar un movimiento suave aleatorio
        generate_random_smooth_movement(random_servo, duration, steps)

        # Esperar un tiempo antes de realizar el próximo movimiento
        time.sleep(random.uniform(0.5, 2.0))  # Puedes ajustar estos valores según tus necesidades

if __name__ == "__main__":
    kit = ServoKit(channels=16)  # Asegúrate de ajustar el número de canales según tu configuración
    servos_data = skeleton_servos_data

    initialize_servos(kit, servos_data)

    try:
        perform_random_smooth_movements(servos_data)
    except KeyboardInterrupt:
        print("\nMovimientos aleatorios suaves detenidos.")