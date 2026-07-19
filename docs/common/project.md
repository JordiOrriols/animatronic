# Project

The `Project` class loads project-specific servo data, animations, and automatic behavior.

## What it does

It ties together the selected project configuration, servo definitions, animation playback, and generative mode.

## Main methods

- `__init__(init_servos=True)`: loads the project from the `PROJECT_ID` environment variable and initializes the servos.
- `get_servos_data()`: returns the servo objects for the current project.
- `load_animation(animation_name)`: loads an animation JSON file from the project folder into memory.
- `evaluate()`: checks the animation against servo limits and generates a report.
- `play()`: plays the loaded animation.
- `auto_start()`: starts generative movement mode for all servos.
- `auto_stop()`: stops the automatic loop.
- `calibrate(servo_pin, position)`: moves a servo to a manual position.
- `standby()`: returns all servos to their rest position.

## Example

```python
import os
from common.project import Project

os.environ["PROJECT_ID"] = "skeleton"
project = Project()
project.load_animation("animation")
project.play()
```

## Notes

Per-project generative settings can be defined in the project config module, for example under `projects/skeleton/config.py` or `projects/seagull/config.py`.
