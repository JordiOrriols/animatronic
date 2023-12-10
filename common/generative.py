import time
import random
from adafruit_servokit import ServoKit  # Asegúrate de tener instalada esta biblioteca

from common.servo import AniServo
from common.logger import Logger

# Aquí deberías tener definidas las variables mg996r_type, mg90s_type y ghs37a_type
# ...

# Aquí deberías tener definidas las clases AniServo, fabric_servo_data y initialize_servos
# ...

class GenerativeMovement(Logger):

    def __init__(self, servo: AniServo, max_duration=5.0, min_duration=1.0):
        super().__init__('GenerativeMovement')

        self.servo = servo
        self.max_duration = max_duration
        self.min_duration = min_duration

        self.__in_progress = False
        self.start_time = None
        self.current_position = None
        self.next_target_position = None
        self.next_duration = None

    def generate_smooth_movement(self, target_position, duration):
        if self.__in_progress:
            current_time = time.time() - self.start_time
            progress = current_time / duration

            if progress >= 1.0:
                progress = 1.0

            current_position = (
                self.current_position
                + progress * (target_position - self.current_position)
            )
            self.servo.move_to_angle(int(current_position))

            if progress == 1.0:
                self.__in_progress = False

    def perform_random_movement(self, random_factor=1.0):
        if not self.__in_progress:
            # Si no hay un movimiento en curso, generar nuevos valores aleatorios
            min_limit = self.servo.getPhysicalLimitMin()
            max_limit = self.servo.getPhysicalLimitMax()

            # Generar una posición aleatoria dentro de los límites físicos del servo,
            # considerando el factor aleatorio para ajustar la frecuencia cerca de los límites
            actual_range = (max_limit - min_limit)
            limited_range = (max_limit - min_limit) * (random.randint(0, 1) * random_factor)
            offset = actual_range - limited_range / 2
            self.next_target_position = random.randint(min_limit + offset, max_limit - offset)

            # Duración aleatoria para el movimiento
            self.next_duration = random.uniform(self.min_duration, self.max_duration)

            # Guardar la posición actual para referencia futura
            self.current_position = self.kit.servo[self.servo.getPin()].angle

            # Actualizar el indicador de movimiento en curso y el tiempo de inicio
            self.__in_progress = True
            self.start_time = time.time()

        # Mover suavemente el servo a la posición almacenada
        self.generate_smooth_movement(self.next_target_position, self.next_duration)


class RandomMovementsController:
    def __init__(self, servos_data):
        self.animatronic_controllers = [
            GenerativeMovement(servo) for servo in servos_data
        ]

    def perform_all_movements(self, random_factor=1.0):
        for controller in self.animatronic_controllers:
            controller.perform_random_movement(random_factor)

if __name__ == "__main__":
    # Crear una instancia de RandomMovementsController
    random_controller = RandomMovementsController(skeleton_servos_data)

    try:
        while True:
            # Configurar el factor aleatorio según tus preferencias (entre 0 y 1)
            random_factor = 0.5

            # Realizar todos los movimientos con el factor aleatorio
            random_controller.perform_all_movements(random_factor)

    except KeyboardInterrupt:
        print("\nMovimientos aleatorios suaves detenidos.")
