"""Non-blocking, coordinated servo playback owned by the existing Auto worker."""

from common.servo import AniServo
from common.sequence_config import number, validate_sequence


def resolve_position(servo: AniServo, position: dict) -> float:
    """Resolve a neutral-relative fraction without changing calibration."""
    neutral = servo.get_rest_position()
    minimum = servo.get_physical_limit_min()
    maximum = servo.get_physical_limit_max()
    if not minimum <= neutral <= maximum:
        raise ValueError(f"{servo.get_name()}: neutral is outside calibrated bounds")
    reference = {"min": minimum, "max": maximum, "neutral": neutral}[position["reference"]]
    return neutral + position["fraction"] * (reference - neutral)


class ServoSequence:
    """Prepare, wait for server timing, pulse on beats, then restore selected servos."""

    def __init__(self, config: dict, servos: list[AniServo], now: float):
        self.config = validate_sequence(config)
        by_name = {servo.get_name(): servo for servo in servos}
        unknown = self.config["servos"].keys() - by_name.keys()
        if unknown:
            raise ValueError(f"Unknown sequence servos: {sorted(unknown)}")
        self.servos = {name: by_name[name] for name in self.config["servos"]}
        self.original = {name: servo.get_current_position() for name, servo in self.servos.items()}
        if any(value is None for value in self.original.values()):
            raise ValueError("Cannot prepare a sequence with an unknown current servo angle")
        self.positions = {
            name: (resolve_position(servo, item["position_1"]),
                   resolve_position(servo, item["position_2"]))
            for name, servo in self.servos.items()
            for item in [self.config["servos"][name]]
        }
        self.phase = "preparing"
        self.started = now
        self.timeline: dict | None = None
        self.restore_from: dict = {}

    def arm(self, timeline: dict, now: float, lead_ms: float) -> None:
        """Accept relative timing only after preparation has completed."""
        if self.phase != "waiting":
            raise ValueError("Sequence is not waiting for a schedule")
        lead_ms = number(lead_ms, "lead_ms", minimum=100)
        if not isinstance(timeline, dict):
            raise ValueError("Sequence timeline must be an object")
        beats = timeline.get("beats")
        if not isinstance(beats, list) or not beats:
            raise ValueError("Sequence timeline requires beats")
        if any(not isinstance(beat, dict) for beat in beats):
            raise ValueError("Each sequence beat must be an object")
        movement_times = [number(beat.get("movement_ms"), "movement_ms") for beat in beats]
        if movement_times != sorted(movement_times):
            raise ValueError("Sequence movement timestamps must be ordered")
        pulse_ms = max(
            (s["out_ms"] + s["back_ms"] for s in self.config["servos"].values()
             if s["mode"] == "pulse"), default=0,
        )
        if any(b - a < pulse_ms for a, b in zip(movement_times, movement_times[1:])):
            raise ValueError("Sequence movement timestamps overlap")
        end_ms = number(timeline.get("end_ms"), "end_ms")
        if end_ms < movement_times[-1] + pulse_ms:
            raise ValueError("Sequence end precedes the last pulse completion")
        self.timeline = {"beats": [dict(beat) for beat in beats], "end_ms": end_ms}
        self.started = now + lead_ms / 1000
        self.phase = "playing"

    def _move(self, name: str, start: float, target: float, elapsed_ms: float,
              duration_ms: float) -> None:
        settings = self.config["servos"][name]
        progress = 1 if duration_ms == 0 else max(0, min(elapsed_ms / duration_ms, 1))
        eased = AniServo.apply_easing(progress, settings["ease_in"], settings["ease_out"])
        self.servos[name].move_to_angle(start + (target - start) * eased)

    def update(self, now: float) -> str | None:
        """Return ready/complete once, without sleeping or touching unlisted servos."""
        elapsed = (now - self.started) * 1000
        if self.phase == "preparing":
            duration = 0
            for name, settings in self.config["servos"].items():
                duration = max(duration, settings["transition_ms"])
                self._move(name, self.original[name], self.positions[name][0],
                           elapsed, settings["transition_ms"])
            if elapsed >= duration:
                self.phase = "waiting"
                self.started = now
                return "ready"
        elif self.phase == "waiting":
            if elapsed > 10000:
                raise TimeoutError(
                    "Server did not schedule the prepared sequence within 10 seconds"
                )
        elif self.phase == "playing" and elapsed >= 0:
            if self.timeline is None:
                raise RuntimeError("Playing sequence has no timeline")
            for name, settings in self.config["servos"].items():
                if settings["mode"] != "pulse":
                    continue
                beat = next(
                    (beat for beat in reversed(self.timeline["beats"])
                     if beat["movement_ms"] <= elapsed), None,
                )
                if beat is None:
                    continue
                pulse_elapsed = elapsed - beat["movement_ms"]
                closed, opened = self.positions[name]
                if pulse_elapsed < settings["out_ms"]:
                    self._move(name, closed, opened, pulse_elapsed, settings["out_ms"])
                else:
                    self._move(name, opened, closed, pulse_elapsed - settings["out_ms"],
                               settings["back_ms"])
            if elapsed >= self.timeline["end_ms"]:
                self.restore_from = {
                    name: servo.get_current_position() for name, servo in self.servos.items()
                }
                self.phase = "restoring"
                self.started = now
        elif self.phase == "restoring":
            for name, settings in self.config["servos"].items():
                target = (self.positions[name][1] if settings["mode"] == "hold"
                          else self.original[name])
                self._move(name, self.restore_from[name], target,
                           elapsed, self.config["restore_ms"])
            if elapsed >= self.config["restore_ms"]:
                self.phase = "complete"
                return "complete"
        return None
