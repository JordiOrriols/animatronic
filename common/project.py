"""Project module to handle all different data for projects."""

import os
import json
import importlib
import threading
import time
import random
import queue
import uuid
from collections.abc import Callable
from dotenv import load_dotenv
from adafruit_servokit import ServoKit
from websockets.exceptions import ConnectionClosed

from projects.skeleton.config import skeleton_servos_data
from projects.seagull.config import seagull_servos_data

from common.servo import initialize_servos, AniServo
from common.animation import Animation
from common.calibration import has_calibration, save_calibration
from common.logger import Logger
from common.generative import GenerativeMovement
from common.xbox_servo_mapper import XboxServoMapper
from common.sequence import ServoSequence
from common.sequence_config import validate_sequence
from common.config import WEBSOCKET_MESSAGES

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
        self.__auto_thread: threading.Thread | None = None
        self.__auto_stop_event = threading.Event()
        self.__auto_lock = threading.Lock()
        self.__auto_error: Exception | None = None
        self.__xbox_mapper = None
        self.__pending_calibration: dict = {}
        self.sequence_sender: Callable[[str, dict], None] | None = None
        self.__sequence_commands = queue.Queue()

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
            self._sequence_settings = getattr(project_cfg_module, "generative_sequences", {})
        except (ImportError, AttributeError):
            self._generative_settings = {}
            self._xbox_settings = {}
            self._sequence_settings = {}

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

    def get_servo_summary(self):
        """Report name/pin/current calibration for every servo, sent to the server
        on the client-ready handshake so it can build the calibration menu without
        importing any project-specific config."""
        return [
            {"name": servo.get_name(), "pin": servo.get_pin(), **servo.to_calibration_dict()}
            for servo in self.__servos_data
        ]

    def load_animation(self, animation_name):
        """Load animation on memory. Not every project ships an animation.json
        (e.g. seagull), so a missing file just disables animation-related
        features instead of crashing the client."""
        path = "projects/" + str(self.__project) + "/" + animation_name + ".json"
        try:
            with open(path, encoding="utf-8") as json_file:
                self.__animation_data = json.load(json_file)
        except FileNotFoundError:
            self.warning(
                f"No {animation_name}.json found for project '{self.__project}'; "
                "animation features disabled."
            )
            self.__animation_data = None

    def get_capabilities(self):
        """Report which optional features this project's configuration supports,
        so the server can only show options the client can actually run."""
        return {
            "animation": self.__animation_data is not None,
            "generative": bool(self._generative_settings) or bool(self.get_sequence_settings()),
            "xbox": bool(self._xbox_settings),
            "calibrated": has_calibration(self.__project),
        }

    def get_sequence_settings(self):
        """Report enabled, validated sequences to the audio-playing server."""
        for name, config in self._sequence_settings.items():
            if not isinstance(config.get("enabled", True), bool):
                raise ValueError(f"{name}.enabled must be a boolean")
        return {
            name: validate_sequence(config) for name, config in self._sequence_settings.items()
            if config.get("enabled", True)
        }

    def sequence_command(self, action: str, data: dict):
        """Queue sequence messages for the single servo-owning Auto worker."""
        if not isinstance(data, dict) or not isinstance(data.get("id"), str):
            raise ValueError("Sequence command requires an id")
        self.__sequence_commands.put((action, data, time.monotonic()))

    def __send_sequence(self, action: str, data: dict):
        sender = self.sequence_sender
        if sender is None:
            raise RuntimeError("Generative sequences require a server message sender")
        sender(action, data)

    def evaluate(self):
        """Validate animation and generate error report."""
        if self.__animation_data is None:
            self.error("No animation loaded for project", self.__project)
            return
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
        self.auto_stop()
        if self.__animation_data is None:
            self.error("No animation loaded for project", self.__project)
            return
        if self.__validate_servos_data():
            animation = Animation(
                self.__animation_data
            )  # maybe we can move to load animation

            try:
                animation.start()
                while animation.in_progress():
                    animation.refresh()
                    for servo in self.__servos_data:
                        if servo.get_name() in animation.get_positions().keys():
                            new_position = animation.get_current_position(servo)
                            servo.move_to_angle(int(new_position))
            finally:
                try:
                    animation.end()
                finally:
                    self.standby()

    def auto_start(self):
        """Start a worker for configured servos without blocking message reception."""
        if not self.__validate_servos_data():
            return
        with self.__auto_lock:
            if self.__auto_thread is not None and self.__auto_thread.is_alive():
                self.warning("Automatic mode is already running.")
                return
            self.__auto_stop_event.clear()
            self.__auto_error = None
            while not self.__sequence_commands.empty():
                self.__sequence_commands.get_nowait()
            sequences = self.get_sequence_settings()
            if sequences and self.sequence_sender is None:
                raise RuntimeError("Generative sequences require a server message sender")

            # Build per-servo controllers using per-servo generative settings
            animatronic_controllers = []
            for servo in self.__servos_data:
                if servo.get_name() not in self._generative_settings:
                    servo.sleep()
                    continue
                cfg = self._generative_settings[servo.get_name()]
                animatronic_controllers.append(GenerativeMovement(servo, cfg))

            self.__auto_thread = threading.Thread(
                target=self.__run_auto,
                args=(animatronic_controllers, sequences),
                name="animatronic-auto",
                daemon=True,
            )
            self.__auto_thread.start()

    @staticmethod
    def __next_sequence_due(config):
        return time.monotonic() + random.uniform(
            config["min_wait_ms"], config["max_wait_ms"]
        ) / 1000

    def __run_auto(self, controllers: list[GenerativeMovement], sequences=None):
        sequences = sequences or {}
        due = {name: self.__next_sequence_due(config) for name, config in sequences.items()}
        active = None
        sequence_id = None
        sequence_name = None
        try:
            while not self.__auto_stop_event.is_set():
                now = time.monotonic()
                while not self.__sequence_commands.empty():
                    action, data, received = self.__sequence_commands.get_nowait()
                    if active is None or data.get("id") != sequence_id:
                        self.warning("Ignoring stale sequence command:", data.get("id"))
                        continue
                    if action == WEBSOCKET_MESSAGES["sequence-cancel"]:
                        raise RuntimeError(f"Server cancelled sequence: {data.get('reason')}")
                    if action == WEBSOCKET_MESSAGES["sequence-arm"]:
                        active.arm(data.get("timeline"), received, data.get("lead_ms"))
                        self.__send_sequence(WEBSOCKET_MESSAGES["sequence-armed"],
                                             {"id": sequence_id})
                if active is None:
                    ready = [name for name, deadline in due.items() if now >= deadline]
                    if ready:
                        sequence_name = min(ready, key=lambda name: due[name])
                        sequence_id = str(uuid.uuid4())
                        active = ServoSequence(sequences[sequence_name], self.__servos_data, now)
                if active is not None:
                    result = active.update(now)
                    if result == "ready":
                        self.__send_sequence(WEBSOCKET_MESSAGES["sequence-ready"],
                                             {"id": sequence_id, "name": sequence_name})
                    elif result == "complete":
                        self.__send_sequence(WEBSOCKET_MESSAGES["sequence-complete"],
                                             {"id": sequence_id})
                        active = None
                        sequence_id = None
                        due = {
                            name: self.__next_sequence_due(config)
                            for name, config in sequences.items()
                        }
                        controllers = [
                            GenerativeMovement(servo, self._generative_settings[servo.get_name()])
                            for servo in self.__servos_data
                            if servo.get_name() in self._generative_settings
                        ]
                else:
                    for controller in controllers:
                        if self.__auto_stop_event.is_set():
                            break
                        controller.update()
                self.__auto_stop_event.wait(0.02)
        except (OSError, ValueError, RuntimeError, ConnectionClosed) as error:
            self.error("Automatic movement failed:", error)
            self.__auto_error = error
        finally:
            self.__finish_auto(sequence_id)

    def __finish_auto(self, sequence_id):
        try:
            if sequence_id is not None and self.sequence_sender is not None:
                self.__send_sequence(WEBSOCKET_MESSAGES["sequence-cancel"],
                                     {"id": sequence_id, "reason": "Auto stopped"})
        except (OSError, RuntimeError, ConnectionClosed) as error:
            self.error("Could not notify server of sequence cancellation:", error)
        finally:
            try:
                self.__return_to_rest()
            except (OSError, ValueError, RuntimeError) as error:
                self.error("Automatic mode neutral return failed:", error)
                self.__auto_error = error

    def auto_stop(self):
        """Stop and join the worker, including its eased return to neutral."""
        with self.__auto_lock:
            self.__auto_stop_event.set()
            if self.__auto_thread is not None:
                self.__auto_thread.join()
                self.__auto_thread = None
            if self.__auto_error is not None:
                error = self.__auto_error
                self.__auto_error = None
                raise error

    def calibrate_neutral(self, servo_pin: int):
        """Ease the selected servo to neutral before manual calibration nudges."""
        self.auto_stop()
        for servo in self.__servos_data:
            if servo.get_pin() == servo_pin:
                servo.sleep()

    def calibrate_move(self, servo_pin: int, position: int):
        """Live-preview a servo position while searching for new calibration
        bounds, bypassing its currently configured limits."""
        self.auto_stop()
        for servo in self.__servos_data:
            if servo.get_pin() == servo_pin:
                servo.move_to_calibration_angle(position)

    def calibrate_save(self, servo_pin: int, neutral: int, min_val: int, max_val: int):
        """Confirm new calibration values for a servo, apply them immediately, and
        stage them to be persisted on the next calibrate_commit()."""
        self.auto_stop()
        for servo in self.__servos_data:
            if servo.get_pin() == servo_pin:
                servo.set_calibration(min_val, max_val, neutral)
                self.__pending_calibration[servo.get_name()] = servo.to_calibration_dict()

    def calibrate_commit(self):
        """Persist all staged calibration values to this unit's local calibration
        file on disk (see common/calibration.py; these files are gitignored and
        never committed/pushed automatically)."""
        if self.__pending_calibration:
            save_calibration(self.__project, self.__pending_calibration)
            self.__pending_calibration = {}

    def standby(self):
        """Put the animatronic in standby mode."""
        self.auto_stop()
        if self.__validate_servos_data():
            self.__return_to_rest()

    def __return_to_rest(self):
        failure = None
        for servo in self.__servos_data:
            try:
                servo.sleep()
            except (OSError, ValueError, RuntimeError) as error:
                self.error(f"Cannot return {servo.get_name()} to neutral:", error)
                failure = error
        if failure is not None:
            raise failure

    def xbox_start(self):
        """Start Xbox controller mode. Prepares a mapper seeded at current positions."""
        self.auto_stop()
        if self.__validate_servos_data():
            self.__xbox_mapper = XboxServoMapper(self.__servos_data, self._xbox_settings)

    def xbox_update(self, raw_axes: dict):
        """Apply a new set of raw controller axis values received from the server."""
        if self.__xbox_mapper is not None:
            self.__xbox_mapper.update(raw_axes)

    def xbox_stop(self):
        """Stop Xbox controller mode and return softly to neutral."""
        self.__xbox_mapper = None
        self.standby()
