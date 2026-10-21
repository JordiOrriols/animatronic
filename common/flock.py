"""One group event with independently timed birds and a randomly selected leader."""

import random
from typing import Optional

from common.sequence import ServoSequence
from common.sequence_config import (
    member_config, number, validate_movement_timeline, validate_sequence,
)
from common.servo import AniServo


class FlockSequence:
    """Share a start trigger, not a beat clock, across independent servo sequences."""

    def __init__(self, config: dict, servos: list[AniServo], now: float):
        self.config = validate_sequence(config)
        self.members = self.config["flock"]["members"]
        known = {servo.get_name() for servo in servos}
        unknown = {name for names in self.members.values() for name in names} - known
        if unknown:
            raise ValueError(f"Unknown flock servos: {sorted(unknown)}")
        self.servos = servos
        self.leader = random.choice(list(self.members))
        self.active = {
            self.leader: ServoSequence(member_config(self.config, self.leader), servos, now)
        }
        self.completed: set[str] = set()
        self.schedule: dict = {}
        self.origin = now
        self.phase = "preparing"
        self.aborted = False

    @property
    def paused_servos(self) -> set[str]:
        """Only birds currently preparing, calling, or restoring relinquish idle."""
        return {name for bird in self.active for name in self.members[bird]}

    def arm(self, timeline: dict, now: float, lead_ms: float) -> None:
        """Validate every bird's schedule before acknowledging any group audio."""
        if self.phase != "waiting":
            raise ValueError("Flock is not waiting for a schedule")
        lead_ms = number(lead_ms, "lead_ms", minimum=100)
        if not isinstance(timeline, dict) or timeline.get("leader") != self.leader:
            raise ValueError("Flock timeline leader does not match")
        members = timeline.get("members")
        if not isinstance(members, dict) or members.keys() != self.members.keys():
            raise ValueError("Flock timeline must schedule every member")
        schedule = {}
        for bird, item in members.items():
            config = member_config(self.config, bird)
            validated = validate_movement_timeline(config, item)
            prepare_ms = number(item.get("prepare_ms"), "prepare_ms")
            preparation = max(s["transition_ms"] for s in config["servos"].values())
            first_movement = validated["beats"][0]["movement_ms"]
            first_audio = number(validated["beats"][0].get("audio_ms"), "audio_ms")
            if bird == self.leader:
                if prepare_ms != 0:
                    raise ValueError("Leader must already be prepared")
            elif min(first_movement, first_audio) < prepare_ms + preparation:
                raise ValueError("Follower must have time to prepare before calling")
            schedule[bird] = {**validated, "prepare_ms": prepare_ms}
        self.active[self.leader].arm(schedule[self.leader], now, lead_ms)
        self.schedule = schedule
        self.origin = now + lead_ms / 1000
        self.phase = "playing"

    def abort(self, now: float) -> None:
        """Restore active birds and prevent followers that have not joined from starting."""
        self.aborted = True
        self.phase = "restoring"
        for sequence in self.active.values():
            sequence.abort(now)

    def update(self, now: float) -> Optional[str]:
        """Prepare followers in their own windows and finish each bird separately."""
        if self.phase == "playing":
            for bird, timeline in self.schedule.items():
                if bird in self.active or bird in self.completed:
                    continue
                if (now - self.origin) * 1000 >= timeline["prepare_ms"]:
                    self.active[bird] = ServoSequence(
                        member_config(self.config, bird), self.servos, now
                    )
        for bird, sequence in list(self.active.items()):
            result = sequence.update(now)
            if result == "ready":
                if self.phase == "preparing":
                    self.phase = "waiting"
                    return "ready"
                first = self.schedule[bird]["beats"][0]
                if (now - self.origin) * 1000 >= min(first["audio_ms"], first["movement_ms"]):
                    raise RuntimeError(f"Flock preparation deadline missed for {bird}")
                sequence.arm(self.schedule[bird], self.origin - 0.1, 100)
            elif result == "complete":
                del self.active[bird]
                self.completed.add(bird)
        if not self.active and (self.aborted or len(self.completed) == len(self.members)):
            self.phase = "complete"
            return "complete"
        return None
