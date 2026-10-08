"""Server-owned, cancellable audio timelines for Pi generative sequences."""

import asyncio
import importlib
from pathlib import Path

from common.config import WEBSOCKET_MESSAGES
from common.logger import Logger
from common.sequence_config import build_timeline, validate_sequence


class SequenceAudio(Logger):
    """One audio channel per connection; pygame is loaded only for enabled events."""

    _channel_indices: set[int] = set()

    def __init__(self, send):
        super().__init__("SequenceAudio")
        self.send = send
        self.settings = {}
        self.sounds = {}
        self.channel = None
        self.channel_index = None
        self.active_id = None
        self.task = None
        self.armed = asyncio.Event()

    def configure(self, settings: dict):
        """Validate settings reported by the Pi without opening an audio device yet."""
        self.settings = {name: validate_sequence(config) for name, config in settings.items()}

    def _load(self, config):
        pygame = importlib.import_module("pygame")

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if self.channel is None:
                count = pygame.mixer.get_num_channels()
                index = next(
                    (i for i in range(count) if i not in self._channel_indices
                     and not pygame.mixer.Channel(i).get_busy()), count,
                )
                if index == count:
                    pygame.mixer.set_num_channels(count + 1)
                self.channel_index = index
                self._channel_indices.add(index)
                self.channel = pygame.mixer.Channel(index)
            root = Path("sound").resolve()
            for clip in config["audio"]["files"]:
                path = Path(clip["path"]).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    raise ValueError(f"Sequence audio file missing or outside sound/: {path}")
                if clip["path"] not in self.sounds:
                    self.sounds[clip["path"]] = pygame.mixer.Sound(str(path))
        except pygame.error as error:
            raise RuntimeError(f"Cannot initialize sequence audio: {error}") from error
        return {path: sound.get_length() * 1000 for path, sound in self.sounds.items()}

    async def ready(self, data: dict):
        """Prepare the audio and send a complete schedule only after Pi preparation."""
        if self.active_id is not None:
            raise ValueError("A sequence is already active on this connection")
        self.active_id = data["id"]
        self.armed.clear()
        self.task = asyncio.create_task(self._run(data))

    async def handle(self, action: str, data: list):
        """Route sequence protocol messages for this connection."""
        if action not in {
            WEBSOCKET_MESSAGES[key] for key in (
                "sequence-ready", "sequence-armed", "sequence-complete", "sequence-cancel"
            )
        }:
            return
        if not data or not isinstance(data[0], dict) or not isinstance(data[0].get("id"), str):
            raise ValueError("Sequence message requires an id")
        if action == WEBSOCKET_MESSAGES["sequence-ready"]:
            await self.ready(data[0])
        elif action == WEBSOCKET_MESSAGES["sequence-armed"]:
            self.acknowledge(data[0])
        else:
            await self.stop(data[0])

    async def _run(self, data: dict):
        try:
            config = self.settings[data["name"]]
            lengths = self._load(config)
            channel = self.channel
            if channel is None:
                raise RuntimeError("Sequence audio channel was not initialized")
            timeline = build_timeline(config, lengths)
            lead_ms = 500
            loop = asyncio.get_running_loop()
            sent_at = loop.time()
            await self.send(WEBSOCKET_MESSAGES["sequence-arm"], {
                "id": data["id"], "timeline": timeline, "lead_ms": lead_ms,
            })
            await asyncio.wait_for(self.armed.wait(), timeout=lead_ms / 1000)
            # Estimate one-way latency without comparing clocks across machines.
            origin = sent_at + lead_ms / 1000 + (loop.time() - sent_at) / 2
            for beat in timeline["beats"]:
                deadline = origin + beat["audio_ms"] / 1000
                delay = deadline - asyncio.get_running_loop().time()
                if delay < -0.1:
                    raise RuntimeError("Sequence audio deadline missed; cancelling playback")
                await asyncio.sleep(max(0, delay))
                channel.stop()
                channel.play(self.sounds[beat["path"]])
            await asyncio.sleep(max(
                0, origin + timeline["end_ms"] / 1000 - asyncio.get_running_loop().time()
            ))
        except (OSError, ValueError, RuntimeError, KeyError, ImportError, TimeoutError) as error:
            self.error("Sequence playback failed:", error)
            await self.send(WEBSOCKET_MESSAGES["sequence-cancel"],
                            {"id": data["id"], "reason": str(error)})
        finally:
            if self.channel is not None:
                self.channel.stop()

    def acknowledge(self, data: dict):
        """Ignore obsolete acknowledgements instead of arming a newer event."""
        if data.get("id") == self.active_id:
            self.armed.set()
        else:
            self.warning("Ignoring stale sequence acknowledgement:", data.get("id"))

    async def stop(self, data=None):
        """Cancel playback and silence this channel before any neutral-return command."""
        if data is not None and data.get("id") != self.active_id:
            self.warning("Ignoring stale sequence completion/cancellation:", data.get("id"))
            return
        if self.task is not None:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        if self.channel is not None:
            self.channel.stop()
        self.active_id = None

    async def close(self):
        """Release this connection's channel even when pending playback failed."""
        try:
            await self.stop()
        finally:
            if self.channel_index is not None:
                self._channel_indices.discard(self.channel_index)
                self.channel_index = None
            self.channel = None
            self.sounds.clear()
