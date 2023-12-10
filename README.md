# Animatronic Control System

Hello everybody!
This is a small code built in Python to control several DIY Animatronics. It is intended to work with Raspberry Pi.
I really think that using Raspberry Pi Zero instead of Arduino will provide a lot of interesting tools.

And it's smaller and cheaper:

Raspberry Pi Zero: https://www.adafruit.com/product/5291

Servo Bonnet: https://www.adafruit.com/product/3416

I am still working on this code and adding different features. But this is the basic list:

- Configure all your animatronics in one repository
  - Using environment variables
  - Adding configuration files to calibrate your servos, adding physical limits for each servo
- Play JSON animations
  - If you have the models in Blender, you can build the JSON animation files using the Plugin from Tim Hendriks.
    Currently, I'm adding basic configuration and using the physical limits from the configuration file.
    This allows running several animatronics and configuring each physical device separately,
    detaching the animatronic physical limits from the animation itself.
    https://www.youtube.com/watch?v=yeJxMaNQAzg
- Generative Mode
  - You can randomly generate movements on your animatronic, making a random smooth movement when it is on standby
- Control everything with a server (Can be another Raspberry Pi or a Mac/PC)
  - The server will be connected to all animatronics via WebSocket
  - The animatronics will discover automatically the server and connect to it on the local network
  - The servo will be responsible for playing the music and sounds so all animatronics can be in sync
  - You have a CLI to control the animatronics

These are some examples of animatronics I'm building:

Skeleton V2 - https://www.youtube.com/watch?v=p53LTbVnqZs

Skeleton - https://www.youtube.com/watch?v=jwxCnF2dbwg

Jack Sparrow - https://www.youtube.com/watch?v=WWEPXgQNn7I

If you plan to test the code, please leave a comment on Issues if you have any doubts.
I will be happy to know if someone is using it and happy to help!

## To Install

### CLIENT On Raspberry Pi

```
sudo apt-get install python-smbus
sudo apt-get install i2c-tools

sudo pip3 install adafruit-circuitpython-servokit
sudo pip3 install python-dotenv
sudo pip3 install websockets

sudo echo "PROJECT_ID=skeleton" > .env
```

### SERVER On MacOs

```
pip3 install playsound
pip3 install websockets
pip3 install simple-term-menu
brew install python-tk
```

### Connect to your Raspberry Pi

This script is used to connect to the raspberry pi zero and start the project.
You need to have the repository cloned to `git/animatronic` folder.

`ssh pi@raspberrypi.local`
`. git/animatronic/startup.sh`

### Project Configuration

This scripts are used to run:
Tim Hendriks
Phantom DIY Animatronic from Phantom Manor
https://www.youtube.com/watch?v=jwxCnF2dbwg

But can be used to run all kind of servo animations.
To play this scripts it's important to know that python code from common and skeleton will be used.

You must change the `projects/skeleton/config.py` with your servos information.

### Calibrate Servos

`python3 calibrate_servos_cli.py`

This script allow you to select a servo via CLI.
You need to select the servo Pin, and then select a start position. Recommended 90 deg. After that you can use + and - keys to move the servo in 5 deg steps.

`python3 calibrate_servos_app.py`

This script will be deprecated.
This script opens a graphical interface with range controls. All servos will be set with their rest position defined on the configuration.
After that, you can drag and drop the controls to move the servos and see the limits.

### Play Animation from JSON

`python3 play_deprecated.py`

This script will play a JSON animation. Will work as a film, so will send the current position to the servo, and then wait until the new position time arrives. This will work like a film in frames per second.

`python3 client.py`

This script is similar to the `python3 play_fps.py`, but with the difference that instead of waiting for the next position, will send the position to the servo, and when the code has finished, will interpolate the position to be rendered from the animation JSON file. This will increase the FPS when possible and the animation should be smother.

Also this file will be syncronized via websockets, so we can start the animation from the server where we can syncronize with the music.

## Mouth Scripts (Not tested since a lot of time) Not stable

This scripts are used to run:
Will Cogley
Making Teeth and Tongue For an Animatronic Mouth
https://www.youtube.com/watch?v=ci4pCjzCIQU

To play this scripts it's important to know that python code from common and mouth will be used.

You must change the `mouth/config.py` with your servos information.

`python3 projects/mouth/play_phonemes.py`

This script allow us to change the pose of a mouth with the different phonemes. It is intended to be used with some script to extract phonemes from an audio.
