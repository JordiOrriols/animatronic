import os
import json
import time

from common.project import Project

# Initialization
project = Project()

# Run code

with open(
    f"projects/{os.getenv('PROJECT_ID')}/animation.json", encoding="utf-8"
) as json_file:
    data = json.load(json_file)

    print("Animation loaded")

    while 1:
        print("\n\n", "System Ready")
        print("\n", "Playing at ", data["fps"], "fps")
        print("\n", data["frames"], "Frames")
        print("\n", "Estimated duration: ", data["frames"] / data["fps"], " seconds")
        initialize = input("Press any key to start: ")

        current_frame = 0
        positions = data["positions"]
        initialize = time.time()
        frameDuration = 1 / data["fps"]

        while current_frame < data["frames"]:
            frameStart = time.time()

            for servo in project.get_servos_data():
                if servo.get_name() in positions.keys():
                    new_position = positions[servo.get_name()][current_frame]
                    servo.move_to_angle(int(new_position))

            frameEnd = time.time()
            frameElapsed = frameEnd - frameStart
            sleepTime = frameDuration - frameElapsed

            if sleepTime > 0:
                time.sleep(sleepTime)

            current_frame = current_frame + 1

        end = time.time()

        print("\n", "Estimated duration: ", data["frames"] / data["fps"], " seconds")
        print("\n", "Final duration: ", end - initialize, " seconds")
