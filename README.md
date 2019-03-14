# Opening Doors - RaspberryPI code

This repo is the RPi code for Ben Dechrai's talk, "Opening Doors with JSON Web Tokens"

## Steps to set up the RPi

### Using the Explore NFC RPi module

(This section is still rough - mainly because my Explore NFC module died in transit, and I needed to read the JWT from a serial stream instead.)

0. Install Raspbian from https://www.raspberrypi.org/downloads/raspbian/
1. Run `sudo raspi-config` and go to option "5 Interfacing Options  Configure connections to peripherals"
   0. Enable "P4 SPI         Enable/Disable automatic loading of SPI kernel module"
   1. Enable "P5 I2C         Enable/Disable automatic loading of I2C kernel module"
2. In the `neardal_packages` directory, install all the `.deb` files with `sudo dpkg -i *.deb`.
3. pip install nxppy
4. pip install PyJWT
5. sudo update-rc.d -f neard-explorenfc remove
6. Install the NFC Reader Library for Linux (DEB package from https://www.nxp.com/webapp/sps/download/license.jsp?colCode=NFC-Reader-Library-4.010-2&appType=file1&DOWNLOAD_ID=null&lang_cd=en)

### Reading JWTs from a serial stream

I used a PN532 NFC reader connected to an Arduino Uno R3 compatible board, which returns meta data about the NFC cards over serial. You can [see the code for the Arduino board here](https://github.com/bendechrai/opening-doors-arduino).

The RPi needs to be running `poll-usb.py`, which will read the data frmo the Arduino, and process JWTs received that way instead. I believe all modules used in this script are already available in a base Raspian install, but I've not tested this assumption.

## Third party code

The NXP libraries on the NXP web site don't include all the DEB files required. A previous version does, and I found them at https://github.com/matrix-io/matrix-creator-nfc-unstable-preview/tree/master/neardal_packages (commit c47f50d) and stored here in the `neardal_packages` directory (just in case they disappear from the matrix-io repo in the future).
