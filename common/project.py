"""Project module to handle all different data for projects."""

import os
import json
import importlib
import time
from dotenv import load_dotenv
from adafruit_servokit import ServoKit

from projects.skeleton.config import skeleton_servos_data
from projects.seagull.config import seagull_servos_data

from common.servo import initialize_servos, AniServo
from common.animation import Animation
from common.logger import Logger
from common.generative import GenerativeMovement
from common.xbox_controller import XboxServoMapper

servos_data_object = {
    "skeleton": skeleton_servos_data,
    "seagull": seagull_servos_data,
}


class Project(Logger):
    """Class to handle all Project specific information."""

    def __init__(self, init_servos=True):
        super().__init__("Project")

        self.info("Loading environment...")
        load_dotenv()

        self.__project = os.getenv("PROJECT_ID")
        self.__animation_data = None
        self.__automatic_mode = False
        self.__xbox_mapper = None

        self.info("Initializing for project: ", self.__project)
        self.__servos_data: list[AniServo] = servos_data_object[self.__project]

        # Try to load per-project generative/xbox settings if present in project config
        try:
            project_cfg_module = importlib.import_module(
                f"projects.{self.__project}.config"
            )
            self._generative_settings = getattr(
                project_cfg_module, "generative_settings", {}
            )
            self._xbox_settings = getattr(project_cfg_module, "xbox_settings", {})
        except (ImportError, AttributeError):
            self._generative_settings = {}
            self._xbox_settings = {}

        if self.__validate_servos_data():
            kit = ServoKit(channels=16)
            self.kit = kit
            if init_servos:
                initialize_servos(kit, self.__servos_data)

    def __validate_servos_data(self):
        if self.__servos_data is None:
            self.error("Servo Data not initialized. Wrong Project ID", self.__project)
            return False
        return True

    def get_servos_data(self):
        """Get servos data."""
        return self.__servos_data

    def load_animation(self, animation_name):
        """Load animation on memory."""
        with open(
            "projects/" + str(self.__project) + "/" + animation_name + ".json",
            encoding="utf-8",
        ) as json_file:
            self.__animation_data = json.load(json_file)
    def evaluate(self):
        """Validate animation and generate error report."""
        if self.__validate_servos_data():
            animation = Animation(
                self.__animation_data
            )  # maybe we can move to load animation

            report = {
                'total_errors': 0,
                'min_limit_errors': 0,
                'max_limit_errors': 0,
                'servos': {}
            }

            for servo in self.__servos_data:
                self.info("Servo: ", servo.get_name())
                data = [int(num) for num in animation.get_positions()[servo.get_name()]]

                min_value = min(data)
                max_value = max(data)

                min_limit = servo.get_physical_limit_min()
                max_limit = servo.get_physical_limit_max()

                servo_report = {
                    'errors': 0,
                    'min_deviation': 0,
                    'max_deviation': 0
                }

                if min_value < min_limit:
                    self.error(
                        f"Minimum: limit ({min_limit}) exceed with ({min_value})"
                    )
                    servo_report['errors'] += 1
                    servo_report['min_deviation'] = min_limit - min_value
                    report['min_limit_errors'] += 1
                    report['total_errors'] += 1
                else:
                    self.info(
                        f"Minimum: limit ({min_limit}) in range with ({min_value})"
                    )

                if max_value > max_limit:
                    self.error(
                        f"Maximum: limit ({max_limit}) exceed with ({max_value})"
                    )
                    servo_report['errors'] += 1
                    servo_report['max_deviation'] = max_value - max_limit
                    report['max_limit_errors'] += 1
                    report['total_errors'] += 1
                else:
                    self.info(
                        f"Maximum: limit ({max_limit}) in range with ({max_value})"
                    )

                if servo_report['errors'] > 0:
                    report['servos'][servo.get_name()] = servo_report

            self.info("=== Error Report ===")
            self.info(f"Total errors found: {report['total_errors']}")
            self.info(f"Minimum limit errors: {report['min_limit_errors']}")
            self.info(f"Maximum limit errors: {report['max_limit_errors']}")
            self.info("=== Servo Details ===")
            for servo_name, servo_data in report['servos'].items():
                self.info(f"Servo {servo_name}:")
                self.info(f"  Errors: {servo_data['errors']}")
                self.info(f"  Min deviation: {servo_data['min_deviation']}")
                self.info(f"  Max deviation: {servo_data['max_deviation']}")

    def play(self):
        """Play animation."""
        if self.__validate_servos_data():
            animation = Animation(
                self.__animation_data
            )  # maybe we can move to load animation

            animation.start()

            while animation.in_progress():
                animation.refresh()

                for servo in self.__servos_data:
                    if servo.get_name() in animation.get_positions().keys():
                        new_position = animation.get_current_position(servo)
                        servo.move_to_angle(int(new_position))

            animation.end()

    def auto_start(self):
        """Start automatic generative movements."""
        if self.__validate_servos_data():
            self.__automatic_mode = True

            # Build per-servo controllers using per-servo generative settings
            animatronic_controllers = []
            for servo in self.__servos_data:
                cfg = self._generative_settings.get(servo.get_name(), None)
                animatronic_controllers.append(GenerativeMovement(servo, cfg))

            # Main loop: call update on each controller and yield CPU briefly
            while self.__automatic_mode:
                for controller in animatronic_controllers:
                    controller.update()

                # short sleep to avoid CPU spin; controllers are time-driven
                time.sleep(0.02)

    def auto_stop(self):
        """Stop automatic generative movements."""
        self.__automatic_mode = False  # Not sure if this will work

    def calibrate(self, servo_pin: int, position: int):
        """Calibrate manually a servo."""
        for servo in self.__servos_data:
            if servo.get_pin() == servo_pin:
                servo.move_to_angle(position)

    def standby(self):
        """Put the animatronic in standby mode."""
        if self.__validate_servos_data():
            for servo in self.__servos_data:
                servo.sleep()

    def xbox_start(self):
        """Start Xbox controller mode. Prepares a mapper seeded at current positions."""
        if self.__validate_servos_data():
            self.__xbox_mapper = XboxServoMapper(self.__servos_data, self._xbox_settings)

    def xbox_update(self, raw_axes: dict):
        """Apply a new set of raw controller axis values received from the server."""
        if self.__xbox_mapper is not None:
            self.__xbox_mapper.update(raw_axes)

    def xbox_stop(self):
        """Stop Xbox controller mode. Servos hold their last commanded position."""
        self.__xbox_mapper = None
