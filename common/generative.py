import time
import random
from adafruit_servokit import ServoKit  # Asegúrate de tener instalada esta biblioteca

# Aquí deberías tener definidas las variables mg996r_type, mg90s_type y ghs37a_type
# ...

# Aquí deberías tener definidas las clases AniServo, fabric_servo_data y initialize_servos
# ...

class AnimatronicController:
    def __init__(self, servo, max_duration=2.0, min_duration=0.5, steps=50):
        self.kit = ServoKit(channels=16)  # Asegúrate de ajustar el número de canales según tu configuración
        self.servo = servo
        self.max_duration = max_duration
        self.min_duration = min_duration
        self.steps = steps

        initialize_servos(self.kit, [self.servo])

    def generate_smooth_movement(self, target_position, duration):
        current_position = self.kit.servo[self.servo.getPin()].angle
        angle_change = (target_position - current_position) / self.steps

        for _ in range(self.steps):
            current_position += angle_change
            self.servo.move_to_angle(int(current_position))
            time.sleep(duration / self.steps)

    def generate_random_smooth_movement(self):
        min_limit = self.servo.getPhysicalLimitMin()
        max_limit = self.servo.getPhysicalLimitMax()

        # Generar una posición aleatoria dentro de los límites físicos del servo
        random_position = random.randint(min_limit, max_limit)

        # Duración aleatoria para el movimiento
        duration = random.uniform(self.min_duration, self.max_duration)

        # Mover suavemente el servo a la posición aleatoria
        self.generate_smooth_movement(random_position, duration)


class RandomMovementsController:
    def __init__(self, servos_data):
        self.kit = ServoKit(channels=16)  # Asegúrate de ajustar el número de canales según tu configuración
        self.servos_data = servos_data
        self.animatronic_controllers = [
            AnimatronicController(servo) for servo in self.servos_data
        ]

    def perform_random_smooth_movements(self, duration_between_movements=2.0):
        while True:
            # Realizar movimientos suaves aleatorios para cada servo
            for controller in self.animatronic_controllers:
                controller.generate_random_smooth_movement()

            # Esperar un tiempo antes de realizar el próximo conjunto de movimientos
            time.sleep(duration_between_movements)

if __name__ == "__main__":
    # Crear una instancia de RandomMovementsController
    random_controller = RandomMovementsController(skeleton_servos_data)

    try:
        # Iniciar movimientos suaves aleatorios para todos los servos
        random_controller.perform_random_smooth_movements()
    except KeyboardInterrupt:
        print("\nMovimientos aleatorios suaves detenidos.")
