#!/usr/bin/env python
# -*- coding: <encoding unicode > -*-

import time
import RPi.GPIO as GPIO

ServoPin = 32
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ServoPin, GPIO.OUT)
Servo = GPIO.PWM(ServoPin, 25)
Servo.start(0)

def loop():
    print('Close')
    SetAngle(90)

def SetAngle(angle):
    duty = angle / 34 + 3
    GPIO.output(ServoPin, True)
    Servo.ChangeDutyCycle(duty)
    time.sleep(0.2)
    GPIO.output(ServoPin, False)
    Servo.ChangeDutyCycle(0)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
    try:
        loop()
        destroy()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        destroy()
