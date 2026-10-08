"""GenerativeMovement module to generate random movements for animatronics.

This implementation accepts a per-servo configuration dict (see project configs)
and runs a small state machine producing non-blocking movements. Config values
use milliseconds for durations/waits and degrees for angles. Easing factors are
numeric in the 0.0..1.0 range.
"""

import time
import random
import math
from typing import Optional

from common.servo import AniServo
from common.logger import Logger


class GenerativeMovement(Logger):
    """Generates random movements for a single `AniServo` using a config.

    Config dictionary supported keys (all optional):
      - min_duration_ms, max_duration_ms: movement duration range in ms
      - min_wait_ms, max_wait_ms: waiting time between cycles in ms
      - min_angle, max_angle: bounds (deg) to use for targets (clipped to servo limits)
      - random_factor: 0.0..1.0 fraction of the available range to actually use
      - min_range_fraction, max_range_fraction: 0..1 travel from neutral to each limit
      - ease_in: 0.0..1.0 numeric ease-in factor
      - ease_out: 0.0..1.0 numeric ease-out factor
      - return_to_rest: bool, if true movement goes rest->target->rest each cycle
      - rest_hold_ms: optional hold time at rest after returning (ms)
    """

    DEFAULTS = {
        "min_duration_ms": 200,
        "max_duration_ms": 1200,
        "min_wait_ms": 200,
        "max_wait_ms": 1000,
        "min_angle": None,
        "max_angle": None,
        "random_factor": 1.0,
        "min_range_fraction": 1.0,
        "max_range_fraction": 1.0,
        "ease_in": 0.0,
        "ease_out": 0.0,
        "return_to_rest": False,
        "rest_hold_ms": 0,
    }

    def __init__(self, servo: AniServo, config: Optional[dict] = None):
        super().__init__("GenerativeMovement - Servo " + servo.get_name())

        self.__servo = servo
        cfg = {} if config is None else dict(config)
        # merge defaults
        for key, value in self.DEFAULTS.items():
            cfg.setdefault(key, value)

        self.cfg = cfg
        for key in ("min_range_fraction", "max_range_fraction"):
            value = cfg[key]
            if (
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not 0 <= value <= 1
            ):
                raise ValueError(f"{key} must be a finite number between 0 and 1")

        # convert ms -> seconds for internal timing
        self._min_duration = self.cfg["min_duration_ms"] / 1000.0
        self._max_duration = self.cfg["max_duration_ms"] / 1000.0
        self._min_wait = self.cfg["min_wait_ms"] / 1000.0
        self._max_wait = self.cfg["max_wait_ms"] / 1000.0
        self._rest_hold = self.cfg.get("rest_hold_ms", 0) / 1000.0

        self._random_factor = float(self.cfg.get("random_factor", 1.0))
        self._ease_in = float(self.cfg.get("ease_in", 0.0))
        self._ease_out = float(self.cfg.get("ease_out", 0.0))
        self._return_to_rest = bool(self.cfg.get("return_to_rest", False))

        # servo limits
        self._min_limit = self.__servo.get_physical_limit_min()
        self._max_limit = self.__servo.get_physical_limit_max()
        rest = self.__servo.get_rest_position()
        if not self._min_limit <= rest <= self._max_limit:
            raise ValueError("Servo neutral position must be within calibrated limits")
        self._min_limit = math.ceil(rest - (rest - self._min_limit) * cfg["min_range_fraction"])
        self._max_limit = math.floor(rest + (self._max_limit - rest) * cfg["max_range_fraction"])

        # optional angle override from config; if None use full servo limits
        self._cfg_min_angle = self.cfg.get("min_angle")
        self._cfg_max_angle = self.cfg.get("max_angle")
        self._get_angle_bounds()

        # initial runtime state
        self._state = "waiting"  # waiting | moving | moving_rest
        self._start_time = time.monotonic()
        self._move_start = self._start_time
        self._wait_until = self._start_time + self._random_wait()
        self._start_pos = self.__servo.get_current_position()
        self._target_pos = self._start_pos
        self._duration = 0.0

    def _random_wait(self):
        return random.uniform(self._min_wait, self._max_wait)

    def _random_duration(self):
        return random.uniform(self._min_duration, self._max_duration)

    def _get_angle_bounds(self):
        lower_bound = (
            self._min_limit
            if self._cfg_min_angle is None
            else max(self._min_limit, int(self._cfg_min_angle))
        )
        upper_bound = (
            self._max_limit
            if self._cfg_max_angle is None
            else min(self._max_limit, int(self._cfg_max_angle))
        )
        if lower_bound > upper_bound:
            raise ValueError("Generative angle overrides do not intersect the permitted range")
        return lower_bound, upper_bound

    def _choose_target(self):
        lower_bound, upper_bound = self._get_angle_bounds()
        if lower_bound == upper_bound:
            return lower_bound
        span = upper_bound - lower_bound
        # reduce span by random factor and center it
        limited_span = int(span * self._random_factor)
        if limited_span <= 0:
            return self.__servo.get_current_position()

        offset = int((span - limited_span) / 2)
        return random.randint(lower_bound + offset, upper_bound - offset)

    def _apply_easing(self, progress_value: float) -> float:
        return AniServo.apply_easing(progress_value, self._ease_in, self._ease_out)

    def update(self):
        """Advance the controller state and move the servo as needed.

        This method is non-blocking and should be called frequently (e.g. in the
        main auto loop)."""

        now = time.monotonic()

        if self._state == "waiting":
            if now >= self._wait_until:
                # select a new target and start moving
                self._start_pos = self.__servo.get_current_position()
                self._target_pos = self._choose_target()
                self._duration = self._random_duration()
                self._move_start = now
                # decide next state: moving to target
                self._state = "moving"
                self.log(
                    "Start moving",
                    {
                        "from": self._start_pos,
                        "to": self._target_pos,
                        "duration": self._duration,
                    },
                )
        elif self._state in ("moving", "moving_rest"):
            elapsed = now - self._move_start
            progress = min(elapsed / max(self._duration, 1e-6), 1.0)
            returning = self._state == "moving_rest"
            eased = AniServo.apply_easing(progress) if returning else self._apply_easing(progress)
            current_pos = self._start_pos + (self._target_pos - self._start_pos) * eased
            self.__servo.move_to_angle(current_pos)

            if progress >= 1.0:
                # finished movement to target
                if self._return_to_rest and not returning:
                    rest = self.__servo.get_rest_position()
                    self._start_pos = self.__servo.get_current_position()
                    self._target_pos = rest
                    self._move_start = now
                    self._duration = self._random_duration()
                    self._state = "moving_rest"
                else:
                    self._wait_until = now + (
                        self._rest_hold
                        if returning and self._rest_hold > 0
                        else self._random_wait()
                    )
                    self._state = "waiting"
