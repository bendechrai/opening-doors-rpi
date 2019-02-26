# Opening Doors - RaspberryPI code

This repo is the RPi code for Ben Dechrai's talk, "Opening Doors with JSON Web Tokens"

## Steps to set up the RPi

0. Install Raspbian from https://www.raspberrypi.org/downloads/raspbian/
1. Run `sudo raspi-config` and go to option "5 Interfacing Options  Configure connections to peripherals"
   0. Enable "P4 SPI         Enable/Disable automatic loading of SPI kernel module"
   1. Enable "P5 I2C         Enable/Disable automatic loading of I2C kernel module"
2. In the `neardal_packages` directory, install all the `.deb` files with `sudo dpkg -i *.deb`.

pip install nxppy
pip install PyJWT


sudo update-rc.d -f neard-explorenfc remove
4. Install the NFC Reader Library for Linux (DEB package from https://www.nxp.com/webapp/sps/download/license.jsp?colCode=NFC-Reader-Library-4.010-2&appType=file1&DOWNLOAD_ID=null&lang_cd=en)


## Third party code

The NXP libraries on the NXP web site don't include all the DEB files required. A previous version does, and I found them at https://github.com/matrix-io/matrix-creator-nfc-unstable-preview/tree/master/neardal_packages (commit c47f50d) and stored here in the `neardal_packages` directory (just in case they disappear from the matrix-io repo in the future).
