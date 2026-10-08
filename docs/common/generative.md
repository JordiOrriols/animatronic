# GenerativeMovement

`GenerativeMovement` creates smooth, non-blocking servo motion for automatic or idle-mode behavior.

## What it does

It keeps a simple state machine with a waiting phase and a moving phase. Each cycle chooses a target angle, applies easing, and optionally returns to the servo rest position.

In project Auto mode, only servos explicitly listed in `generative_settings` on the client/Pi are enabled. Unlisted servos return to their calibrated neutral/rest position and stay there. An entry such as `"wings": {}` enables movement with default settings; remove the entry to disable that servo's automatic movement. Creating `GenerativeMovement(servo)` directly still uses defaults.

The project runs Auto updates in a background worker, leaving websocket reception available for `automatic-mode-stop`. Stop waits for any current update and the eased return to neutral to finish before the client sends its completion message.

## Audio-backed generative sequences

Sequence annotations support Python 3.9; Python 3.10 is not required.

`generative_sequences` in the Pi project configuration adds occasional coordinated
events alongside `generative_settings`. The `mine` example in
[the seagull configuration](../../projects/seagull/config.py) is **enabled** and
uses the three MP3s in `sound/seagull/` on the **server**. Install the server's
`pygame` dependency and restart both server and client after updating.
The first event starts after a random 15–45 second wait in Auto mode, then repeats
after another random wait from completion. No audio is played on the Pi.
Auto does not play the shared skeleton background track; only configured
sequence audio is played. Set `"enabled": False` to disable this event.

Each event has:

- `min_wait_ms` / `max_wait_ms`: random wait before the next event. Waits restart
  after completion; the event plays once, not for a random duration.
- `audio.files`: a list of `{"path": "sound/seagull/mine-1.mp3",
  "animation_offset_ms": 100}` objects. Paths must stay under the server's
  `sound/` directory. Positive offsets start movement **after** audio; negative
  offsets start movement **before** audio. Zero starts them together.
- `audio.random_per_beat`: choose a new clip for each vocal beat (default `True`).
- `timing`: `intro_pause_ms` (2000), `min_beat_interval_ms` /
  `max_beat_interval_ms` (each gap between rhythmic beats is picked randomly in
  this range; a fixed `beat_interval_ms`, default 500, may be used instead),
  `min_repeated_beats` (3), `max_repeated_beats` (6), `final_pause_ms` (500).
  One intro, 3–6 rhythmic beats, and one final beat gives 5–8 vocal beats.
  The intro pause starts after both its sound and movement finish.
- `servos`: named entries using `mode`, `position_1`, `position_2`,
  `transition_ms`, `ease_in` and `ease_out`. A position is
  `{"reference": "min" | "max" | "neutral", "fraction": 0.0..1.0}`.
  Fractions describe calibrated travel relative to neutral, not absolute angles.
- `restore_ms`: eased restoration duration (default 600).

For `mode: "hold"`, the servo eases to `position_1`, holds through the
sequence, then eases to `position_2`. For `mode: "pulse"`, it prepares at
`position_1`, moves to `position_2` over `out_ms`, and back over `back_ms` per
beat, then restores its pre-event position. The seagull example pulses
head-pitch between 50% and 90% of Max, the beak between 20% and 80% of Max,
and the wings between 50% and 90% toward Min (their neutral is Max), leaving
head-yaw at its existing position. A pulse needs enough `out_ms` for the servo
to physically reach `position_2`; very short pulses barely move it.

All ordinary generative controllers pause during preparation, playback, and
restoration. Unlisted servos do not receive event commands. Normal movement
resumes from current positions with fresh waits, without replaying an old target.
With multiple enabled events, only one runs at a time and all waits restart
after it finishes.

Pulse durations plus the spread of clip offsets must fit within the shortest
beat/final interval. Audio clips may exceed that interval:
each beat gets a free audio channel so clips overlap and play fully without
being cut off. The sequence waits for all clips and pulses to finish before
restoration. Cancellation stops every channel owned by the connection.

The Pi prepares the servos before requesting a schedule. The server preselects
clips and sends a relative timeline with a 500 ms lead, and waits for the Pi's
acknowledgement before starting audio. Signed offsets get additional lead when
needed; acknowledgement round-trip time estimates the one-way network delay.
This avoids sharing machine clocks, but network and audio-device latency
still affect alignment: this is not sample-accurate synchronization.

Auto stop, mode changes, and disconnect cancel sequence audio and return the Pi
to neutral with the existing easing. Missing files, invalid settings, decoding
failures, missed audio deadlines, and missing acknowledgements fail explicitly
and stop Auto safely; they are not silently retried. Servo preparation times out
if the server does not send a schedule within ten seconds. Older servers cannot
run enabled sequences: update both server and client together.

## Configuration keys

The configuration dictionary may contain:

- `min_duration_ms`, `max_duration_ms`: movement time range.
- `min_wait_ms`, `max_wait_ms`: time between movements.
- `min_angle`, `max_angle`: target bounds in degrees.
- `random_factor`: how much of the allowed range is used.
- `min_range_fraction`, `max_range_fraction`: independent fractions of calibrated travel from neutral toward Min and Max. Each must be a finite number from `0.0` to `1.0`, with `1.0` (100%) as the default. `0.0` disables travel on that side; both zero target neutral. The allowed interval is `neutral - (neutral - min) * min_range_fraction` through `neutral + (max - neutral) * max_range_fraction`, rounded inward to integer degrees.
- `ease_in`, `ease_out`: easing strength.
- `return_to_rest`: whether the servo should return to its rest position after each movement. Returns use a non-blocking ease-in/ease-out phase with a duration chosen from the configured movement duration range, not an immediate position jump. The shared `AniServo.apply_easing()` formula uses 0.2 ease-in and ease-out for returns; outbound movements retain their configured easing factors.
- `rest_hold_ms`: hold duration at rest before the next move.

Angle overrides intersect the fractional interval; they cannot expand it. `random_factor` further narrows that interval using the existing centered-randomness behavior. For example, with Min 20, neutral 80, and Max 160, fractions `0.5` and `0.25` permit 50 through 100 degrees. Neutral must lie within the calibrated limits. Invalid fractions or disjoint angle overrides raise an error instead of silently allowing unsafe motion.

## Main methods

- `__init__(servo, config=None)`: creates the controller for one servo.
- `update()`: advances the movement state and moves the servo if needed.

## Example

```python
from common.generative import GenerativeMovement

controller = GenerativeMovement(
    servo,
    {
        "min_duration_ms": 150,
        "max_duration_ms": 600,
        "min_wait_ms": 100,
        "max_wait_ms": 500,
        "min_angle": 40,
        "max_angle": 140,
        "random_factor": 0.8,
        "min_range_fraction": 1.0,
        "max_range_fraction": 1.0,
        "ease_in": 0.2,
        "ease_out": 0.2,
        "return_to_rest": True,
        "rest_hold_ms": 200,
    },
)

while True:
    controller.update()
    time.sleep(0.02)
```
