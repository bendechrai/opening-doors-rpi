# MATRIX Creator - NFC Support - unstable
Unstable support for PN512 with NXP neard-explorenfc package.

Installation.
====

```sh
cd neardal_packages
sudo dpkg -i libneardal0_0.14.2-1_armhf.deb  libneardal-dev_0.14.2-1_armhf.deb  neard-explorenfc_0.9-1_armhf.deb
sudo update-rc.d -f neard-explorenfc  remove
```
Usage
====
```sh
cd scripts
sudo ./start_nfc.sh
XC3SPROG (c) 2004-2011 xc3sprog project $Rev: 774 $ OS: Linux
Free software: If you contribute nothing, expect nothing!
Feedback on success/failure/enhancement requests:
	http://sourceforge.net/mail/?group_id=170565 
Check Sourceforge for updates:
	http://sourceforge.net/projects/xc3sprog/develop

DNA is 0x3922f565b99158fc
Waiting for tag or device...
on_name_acquired(): :org.neardal
Tag found
ISO14443A ATQA: 	0400
ISO14443A SAK: 	08
ISO14443A UID: 	FE69109F
```
It disables the SPI driver, starts a neard-explorenfc service and sets up a new core on the FPGA. **This core does not support MATRIX Creator-HAL**

Stop
====
```sh
sudo ./stop_nfc.sh 
XC3SPROG (c) 2004-2011 xc3sprog project $Rev: 774 $ OS: Linux
Free software: If you contribute nothing, expect nothing!
Feedback on success/failure/enhancement requests:
	http://sourceforge.net/mail/?group_id=170565 
Check Sourceforge for updates:
	http://sourceforge.net/projects/xc3sprog/develop

DNA is 0x3922f565b99158fc
****  FPGA programmed!
```
It stops all NFC process and **sets up MATRIX Creator-HAL core on the FPGA**. 

How to uninstall.
====
```sh
sudo  aptitude purge libneardal0 libneardal-dev neard-explorenfc
```
