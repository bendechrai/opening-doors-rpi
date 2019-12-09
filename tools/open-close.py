#!/usr/bin/env python
# -*- coding: <encoding unicode > -*-

import time
import RPi.GPIO as GPIO

ServoPin = 32
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ServoPin, GPIO.OUT)
Servo = GPIO.PWM(ServoPin, 50)
Servo.start(0)

def loop():
    while True:
        SetAngle(0)
        time.sleep(1)
        SetAngle(90)
        time.sleep(1)

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(ServoPin, True)
    Servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(ServoPin, False)
    Servo.ChangeDutyCycle(0)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        destroy()
