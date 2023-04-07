# animatronic

## To Install


### On Raspberry Pi

`sudo apt-get install python-smbus`

`sudo apt-get install i2c-tools`


`sudo pip3 install adafruit-circuitpython-servokit`

Pending to validate

`sudo pip3 install tk`

`sudo apt-get install python-tk python3-tk tk-dev`


### On MacOs

`sudo pip3 install adafruit-circuitpython-servokit`

`brew install python-tk`


NOTE: ServoKit will not work, but will avoid errors when coding


## Skeleton Scripts


This scripts are used to run:
    Tim Hendriks
    Phantom DIY Animatronic from Phantom Manor
    https://www.youtube.com/watch?v=jwxCnF2dbwg

But can be used to run all kind of servo animations.
To play this scripts it's important to know that python code from common and skeleton will be used.

You must change the `skeleton/config.py` with your servos information.


### Calibrate Servos
`python3 calibrate_servos_cli.py`

This script allow you to select a servo via CLI.
You need to select the servo Pin, and then select a start position. Recommended 90 deg. After that you can use + and - keys to move the servo in 5 deg steps.


`python3 calibrate_servos_app.py`

This script opens a graphical interface with range controls. All servos will be set with their rest position defined on the configuration.

After that, you can drag and drop the controls to move the servos and see the limits.


### Play Animation from JSON
`python3 play_fps.py`

This script will play a JSON animation. Will work as a film, so will send the current position to the servo, and then wait until the new position time arrives. This will work like a film in frames per second.


`python3 play.py`

This script is similar to the `python3 play_fps.py`, but with the difference that instead of waiting for the next position, will send the position to the servo, and when the code has finished, will interpolate the position to be rendered from the animation JSON file. This will increase the FPS when possible and the animation should be smother.


## Mouth Scripts

This scripts are used to run:
    Will Cogley
    Making Teeth and Tongue For an Animatronic Mouth
    https://www.youtube.com/watch?v=ci4pCjzCIQU

To play this scripts it's important to know that python code from common and mouth will be used.

You must change the `mouth/config.py` with your servos information.

`python3 play_phonemes.py`
This script allow us to change the pose of a mouth with the different phonemes. It is intended to be used with some script to extract phonemes from an audio.