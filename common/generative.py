import time
import random
from adafruit_servokit import ServoKit  # Asegúrate de tener instalada esta biblioteca

# Aquí deberías tener definidas las variables mg996r_type, mg90s_type y ghs37a_type
# ...

# Aquí deberías tener definidas las clases AniServo, fabric_servo_data y initialize_servos
# ...

def generate_random_movement(servo):
    min_limit = servo.getPhysicalLimitMin()
    max_limit = servo.getPhysicalLimitMax()

    # Generar una posición aleatoria dentro de los límites físicos del servo
    random_position = random.randint(min_limit, max_limit)

    # Mover el servo a la posición aleatoria
    servo.move_to_angle(random_position)

def perform_random_movements(servos):
    while True:
        # Seleccionar un servo aleatorio
        random_servo = random.choice(servos)

        # Generar y aplicar un movimiento aleatorio
        generate_random_movement(random_servo)

        # Esperar un tiempo antes de realizar el próximo movimiento
        time.sleep(random.uniform(0.5, 2.0))  # Puedes ajustar estos valores según tus necesidades

if __name__ == "__main__":
    kit = ServoKit(channels=16)  # Asegúrate de ajustar el número de canales según tu configuración
    servos_data = skeleton_servos_data

    initialize_servos(kit, servos_data)

    try:
        perform_random_movements(servos_data)
    except KeyboardInterrupt:
        print("\nMovimientos aleatorios detenidos.")