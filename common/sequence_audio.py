"""Server-owned, cancellable audio timelines for Pi generative sequences."""

import asyncio
import importlib
import threading
from pathlib import Path

from common.config import WEBSOCKET_MESSAGES
from common.logger import Logger
from common.sequence_config import build_timeline, validate_sequence

# Time the Pi gets between receiving the schedule and the first beat.
LEAD_MS = 1000
LOAD_TIMEOUT_S = 15
_LOAD_LOCK = threading.Lock()


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
        self.extra_channels = {}
        self.active_id = None
        self.task = None
        self.armed = asyncio.Event()

    def configure(self, settings: dict):
        """Validate settings reported by the Pi without opening an audio device yet."""
        self.settings = {name: validate_sequence(config) for name, config in settings.items()}
        self.info("Enabled audio sequences:", ", ".join(self.settings) or "none")

    @classmethod
    def _allocate_channel(cls, mixer):
        count = mixer.get_num_channels()
        index = next(
            (i for i in range(count) if i not in cls._channel_indices
             and not mixer.Channel(i).get_busy()), count,
        )
        if index == count:
            mixer.set_num_channels(count + 1)
        channel = mixer.Channel(index)
        cls._channel_indices.add(index)
        return index, channel

    def _play(self, sound):
        """Use a free owned channel without interrupting earlier vocal beats."""
        pygame = importlib.import_module("pygame")
        try:
            channels = [self.channel, *self.extra_channels.values()]
            channel = next((item for item in channels if item is not None
                            and not item.get_busy()), None)
            if channel is None:
                index, channel = self._allocate_channel(pygame.mixer)
                self.extra_channels[index] = channel
            channel.play(sound)
        except pygame.error as error:
            raise RuntimeError(f"Cannot play sequence audio: {error}") from error

    def _silence(self):
        for channel in [self.channel, *self.extra_channels.values()]:
            if channel is not None:
                channel.stop()

    def _load(self, config):
        with _LOAD_LOCK:
            return self._load_locked(config)

    def _load_locked(self, config):
        pygame = importlib.import_module("pygame")

        try:
            if not pygame.mixer.get_init():
                self.info("Opening audio mixer...")
                pygame.mixer.init()
                self.info("Audio mixer opened:", pygame.mixer.get_init())
            if self.channel is None:
                self.channel_index, self.channel = self._allocate_channel(pygame.mixer)
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
            self.warning("Replacing unfinished sequence:", self.active_id)
            await self.stop()
        self.active_id = data["id"]
        self.info("Preparing sequence audio:", data.get("name"), data["id"])
        self.armed.clear()
        self.task = asyncio.create_task(self._run(data))

    async def preload(self):
        """Open the mixer and decode clips at connect time so problems show early."""
        for name, config in self.settings.items():
            try:
                lengths = await self._load_async(config)
                self.info(f"Sequence audio '{name}' ready:", len(lengths), "clips")
            except Exception as error:  # pylint: disable=broad-exception-caught
                self.error(f"Sequence audio '{name}' cannot be loaded:",
                           f"{type(error).__name__}: {error}")

    async def _load_async(self, config):
        # pygame.mixer.init() and MP3 decoding block; keep the websocket loop responsive.
        return await asyncio.wait_for(
            asyncio.to_thread(self._load, config), timeout=LOAD_TIMEOUT_S
        )

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
            lengths = await self._load_async(config)
            if self.channel is None:
                raise RuntimeError("Sequence audio channel was not initialized")
            timeline = build_timeline(config, lengths)
            lead_ms = LEAD_MS
            loop = asyncio.get_running_loop()
            sent_at = loop.time()
            await self.send(WEBSOCKET_MESSAGES["sequence-arm"], {
                "id": data["id"], "timeline": timeline, "lead_ms": lead_ms,
            })
            await asyncio.wait_for(self.armed.wait(), timeout=lead_ms / 1000)
            # Estimate one-way latency without comparing clocks across machines.
            origin = sent_at + lead_ms / 1000 + (loop.time() - sent_at) / 2
            beats = timeline["beats"]
            self.info(f"Sequence armed; playing {len(beats)} beats")
            for number_, beat in enumerate(beats, start=1):
                deadline = origin + beat["audio_ms"] / 1000
                delay = deadline - loop.time()
                if delay < -0.1:
                    raise RuntimeError("Sequence audio deadline missed; cancelling playback")
                await asyncio.sleep(max(0, delay))
                self._play(self.sounds[beat["path"]])
                self.info(f"Beat {number_}/{len(beats)}:", beat["path"])
            await asyncio.sleep(max(0, origin + timeline["end_ms"] / 1000 - loop.time()))
        except asyncio.CancelledError:
            raise
        except Exception as error:  # pylint: disable=broad-exception-caught
            # Never fail silently: the Pi is waiting and must be told to resume Auto.
            reason = f"{type(error).__name__}: {error}" if str(error) else type(error).__name__
            self.error("Sequence playback failed:", reason)
            try:
                await self.send(WEBSOCKET_MESSAGES["sequence-cancel"],
                                {"id": data["id"], "reason": reason})
            except Exception as send_error:  # pylint: disable=broad-exception-caught
                self.error("Could not send sequence cancellation:", send_error)
        finally:
            self._silence()

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
            except Exception as error:  # pylint: disable=broad-exception-caught
                self.error("Sequence audio task failed:", error)
            self.task = None
        self._silence()
        self.active_id = None

    async def close(self):
        """Release this connection's channel even when pending playback failed."""
        try:
            await self.stop()
        finally:
            if self.channel_index is not None:
                self._channel_indices.discard(self.channel_index)
                self.channel_index = None
            for index in self.extra_channels:
                self._channel_indices.discard(index)
            self.extra_channels.clear()
            self.channel = None
            self.sounds.clear()
