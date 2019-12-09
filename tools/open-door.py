#!/usr/bin/env python
# -*- coding: <encoding unicode > -*-

import time
import RPi.GPIO as GPIO

ServoPin = 32
ServoUnlockPosition = 1
ServoLockPosition = 10.5

GPIO.setmode(GPIO.BOARD)                 # Set the board mode to numbers pins by physical location
GPIO.setup(ServoPin, GPIO.OUT)           # Set Servo Pin mode as output
ServoPosition = GPIO.PWM(ServoPin, 50)   # Set PWM to 50Hz
ServoPosition.start(ServoUnlockPosition) # Default servo to locked position
time.sleep(0.1)
GPIO.cleanup()
