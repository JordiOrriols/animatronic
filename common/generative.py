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

        self.is_movement_in_progress = False
        self.next_target_position = None
        self.next_duration = None

    def generate_smooth_movement(self, target_position, duration):
        current_position = self.kit.servo[self.servo.getPin()].angle
        angle_change = (target_position - current_position) / self.steps

        for _ in range(self.steps):
            current_position += angle_change
            self.servo.move_to_angle(int(current_position))
            time.sleep(duration / self.steps)

    def perform_random_movement(self):
        if not self.is_movement_in_progress:
            # Si no hay un movimiento en curso, generar nuevos valores aleatorios
            min_limit = self.servo.getPhysicalLimitMin()
            max_limit = self.servo.getPhysicalLimitMax()

            # Generar una posición aleatoria dentro de los límites físicos del servo
            self.next_target_position = random.randint(min_limit, max_limit)

            # Duración aleatoria para el movimiento
            self.next_duration = random.uniform(self.min_duration, self.max_duration)

            # Actualizar el indicador de movimiento en curso
            self.is_movement_in_progress = True

        # Mover suavemente el servo a la posición almacenada
        self.generate_smooth_movement(self.next_target_position, self.next_duration)

        # Actualizar el indicador de movimiento en curso
        self.is_movement_in_progress = False


class RandomMovementsController:
    def __init__(self, servos_data):
        self.kit = ServoKit(channels=16)  # Asegúrate de ajustar el número de canales según tu configuración
        self.animatronic_controllers = [
            AnimatronicController(servo) for servo in servos_data
        ]

    def perform_all_movements(self):
        for controller in self.animatronic_controllers:
            controller.perform_random_movement()

if __name__ == "__main__":
    # Crear una instancia de RandomMovementsController
    random_controller = RandomMovementsController(skeleton_servos_data)

    try:
        while True:
            # Realizar todos los movimientos
            random_controller.perform_all_movements()

    except KeyboardInterrupt:
        print("\nMovimientos aleatorios suaves detenidos.")
