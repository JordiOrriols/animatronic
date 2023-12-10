import time
import random
from adafruit_servokit import ServoKit  # Asegúrate de tener instalada esta biblioteca

# Aquí deberías tener definidas las variables mg996r_type, mg90s_type y ghs37a_type
# ...

# Aquí deberías tener definidas las clases AniServo, fabric_servo_data y initialize_servos
# ...

class AnimatronicController:
    def __init__(self, servos_data, max_duration=2.0, min_duration=0.5, steps=50):
        self.kit = ServoKit(channels=16)  # Asegúrate de ajustar el número de canales según tu configuración
        self.servos_data = servos_data
        self.max_duration = max_duration
        self.min_duration = min_duration
        self.steps = steps

        initialize_servos(self.kit, self.servos_data)

    def generate_smooth_movement(self, servo, target_position, duration):
        current_position = servo.__kit.servo[servo.getPin()].angle
        angle_change = (target_position - current_position) / self.steps

        for _ in range(self.steps):
            current_position += angle_change
            servo.move_to_angle(int(current_position))
            time.sleep(duration / self.steps)

    def generate_random_smooth_movement(self, servo):
        min_limit = servo.getPhysicalLimitMin()
        max_limit = servo.getPhysicalLimitMax()

        # Generar una posición aleatoria dentro de los límites físicos del servo
        random_position = random.randint(min_limit, max_limit)

        # Duración aleatoria para el movimiento
        duration = random.uniform(self.min_duration, self.max_duration)

        # Mover suavemente el servo a la posición aleatoria
        self.generate_smooth_movement(servo, random_position, duration)

    def perform_random_smooth_movements(self):
        while True:
            # Lista de servos seleccionados aleatoriamente para este movimiento
            random_servos = random.sample(self.servos_data, k=random.randint(1, len(self.servos_data)))

            # Generar y aplicar movimientos suaves aleatorios para cada servo seleccionado
            for random_servo in random_servos:
                self.generate_random_smooth_movement(random_servo)

if __name__ == "__main__":
    # Crear una instancia de AnimatronicController
    animatronic_controller = AnimatronicController(skeleton_servos_data)

    try:
        # Iniciar movimientos suaves aleatorios
        animatronic_controller.perform_random_smooth_movements()
    except KeyboardInterrupt:
        print("\nMovimientos aleatorios suaves detenidos.")
