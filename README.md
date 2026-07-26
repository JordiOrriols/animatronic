# Animatronic Control System

Hello everybody!
This is a small code built in Python to control several DIY Animatronics. It is intended to work with Raspberry Pi.
I really think that using Raspberry Pi Zero instead of Arduino will provide a lot of interesting tools.

Raspberry Pi Zero 2 W: https://www.adafruit.com/product/5291

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

## Common module documentation

A set of module-specific guides for the shared classes lives in [docs/common/README.md](docs/common/README.md). They cover:

- [docs/common/animation.md](docs/common/animation.md)
- [docs/common/autodiscovery.md](docs/common/autodiscovery.md)
- [docs/common/generative.md](docs/common/generative.md)
- [docs/common/project.md](docs/common/project.md)
- [docs/common/servo.md](docs/common/servo.md)
- [docs/common/websocket.md](docs/common/websocket.md)

## To Install

### CLIENT On Raspberry Pi

#### Flashing the SD card

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your computer.
2. Insert the SD card and open Raspberry Pi Imager.
3. Choose OS: pick **Raspberry Pi OS Lite (64-bit)** (no desktop needed, since we boot to CLI).
4. Choose Storage: select your SD card.
5. Before writing, click the gear/settings icon (or press `Ctrl+Shift+X`) to open **Advanced Options** and configure:
   - **Hostname**: `raspberrypi-project` (change if you plan to run multiple animatronics, e.g. `raspberrypi-skeleton`)
   - **Enable SSH**: choose "Allow public-key authentication only" and paste your public key (e.g. contents of `~/.ssh/id_rsa.pub` or `~/.ssh/id_ed25519.pub`). If you don't have one yet, generate it with `ssh-keygen -t ed25519`.
   - **Set username and password**: e.g. username `jordiorriols` and a password of your choice (still useful as a fallback/for `sudo`).
   - **Configure wireless LAN**: enter your Wifi SSID, password, and the Wifi country code.
   - **Set locale settings**: choose your timezone and keyboard layout.
6. Save the settings and click **Write** to flash the SD card.

#### First boot and configuration

Insert the SD card into the Raspberry Pi and power it on. Wait a minute for the first boot to complete, then connect via ssh (change the user if you set a different one):

```
ssh jordiorriols@raspberrypi-project.local
```

Once connected, run the configuration tool:

```
sudo raspi-config
```

In the menu:

- Go to **Interface Options** → **I2C** → select **Yes** to enable the I2C protocol (required for the Servo Bonnet).
- Go to **System Options** → **Boot / Auto Login** → select **Console** (or **Console Autologin**) instead of any Desktop option, since this project runs headless from the CLI.

Select **Finish** and reboot when prompted (or run `sudo reboot`).

After the reboot, connect again via ssh (Change your user if you added other)

```
ssh jordiorriols@raspberrypi-project.local
```

Then start cloning the repo:

```
mkdir github
cd github
git clone https://github.com/JordiOrriols/animatronic.git
cd animatronic
```

Execute setup script

```
chmod +x setup.sh
./setup.sh
```

Set the env file with the project you are going to use

```
echo "PROJECT_ID=skeleton" > .env
echo "CALIBRATION_ID=default" >> .env
```

`CALIBRATION_ID` identifies which `servo_calibration/<id>.json` file this physical
unit uses (different physical builds of the same project can have different servo
limits, and each unit gets its own file so units never conflict with each other in
git). `default` is the file seeded with the project's original values; leave it
unset on a brand new unit and a UUIDv4 will be generated and saved automatically
the first time you calibrate it from the server's "Calibrate" menu.

### SERVER On MacOs or PI with sound capabilities

Then start cloning the repo:

```
mkdir github
cd github
git clone https://github.com/JordiOrriols/animatronic.git
```

Then start installing all dependencies:

```
pip install websockets
pip install playsound==1.2.2
pip install simple-term-menu
pip install pygame
```

### For development

Then start installing all dependencies:

```
pip install pylint
```

### Project Configuration

This scripts are used to run:
Tim Hendriks
Phantom DIY Animatronic from Phantom Manor
https://www.youtube.com/watch?v=jwxCnF2dbwg

But can be used to run all kind of servo animations.
To play this scripts it's important to know that python code from common and skeleton will be used.

You must change the `projects/skeleton/config.py` with your servos information.

## Mouth Scripts (Not tested since a lot of time) Not stable

This scripts are used to run:
Will Cogley
Making Teeth and Tongue For an Animatronic Mouth
https://www.youtube.com/watch?v=ci4pCjzCIQU

To play this scripts it's important to know that python code from common and mouth will be used.

You must change the `mouth/config.py` with your servos information.

`python3 projects/mouth/play_phonemes.py`

This script allow us to change the pose of a mouth with the different phonemes. It is intended to be used with some script to extract phonemes from an audio.
