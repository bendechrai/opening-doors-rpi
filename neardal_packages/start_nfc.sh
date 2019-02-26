#!/bin/bash

#avoid conflicts with kernel SPI driver

rmmod    spi_bcm2835
modprobe spi_bcm2835


sudo xc3sprog -c  matrix_pi  ../blob/nfc.bit  -p 1

sleep 0.2
service neard-explorenfc stop
service neard-explorenfc start 
sleep 1

explorenfc-basic


