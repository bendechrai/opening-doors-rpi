#!/usr/bin/python

import serial
import json
import time
import datetime
import jwt
import RPi.GPIO as GPIO

key=b'''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDPBrl5ukoX48PHQqKVMbJEqPzF
7TwUv057U6GXrXX0leak5N+QuieFmBiXYmOYd2RX3EvIfCHqw9WmhccIEfGvXejC
WGnASqeJ6NH1KSTFwuiiAPIDzvipkWboIK4grir7H7sc/amGNiBsGrb0kJM/Urmx
EXArjIISZLUcp1QSFQIDAQAB
-----END PUBLIC KEY-----'''
aud='opensesame://door1/'

ser = serial.Serial('/dev/ttyACM0', 115200, 8, 'N', 1, timeout=5)

ServoPin = 32
ServoUnlockPosition = 5
ServoLockPosition = 10

GPIO.setmode(GPIO.BOARD)               # Set the board mode to numbers pins by physical location
GPIO.setup(ServoPin, GPIO.OUT)         # Set Servo Pin mode as output
ServoPosition = GPIO.PWM(ServoPin, 50) # Set PWM to 50Hz
ServoPosition.start(ServoLockPosition) # Default servo to locked position

def loop():
    DoorLocked = True
    status = 'inactive'
    while True:
        input = ser.readline()

        if (input == ".\r\n"):
            print("No activity")
            stauts = 'inactive'
            DoorLocked = True
            print("Lock Door")
            ServoPosition.ChangeDutyCycle(ServoLockPosition)

        elif (input == "!\r\n"):
            if (status != 'pending'):
                print("Reading key")
                status = 'pending'

        elif (input[0:5] == "JWT: "):

            try:
                token = input[5:].strip()
                token_payload = jwt.decode(token, key, audience=aud)

                timeNow=datetime.datetime.now().replace(microsecond=0)
                timeExp=datetime.datetime.fromtimestamp(token_payload['exp'])
                timeRemaining=timeExp-timeNow

                print('Door 1 can be unlocked until ' + timeExp.strftime('%a %d %B at %H:%M:%S') + ' (' + str(timeRemaining.total_seconds()) + ' seconds remaining)')
                if(DoorLocked):
                    DoorLocked = False
                    print("Unlock Door")
                    ServoPosition.ChangeDutyCycle(ServoUnlockPosition)
                    print("Wait 5 seconds (let someone open the door)")
                    time.sleep(5)

            except jwt.exceptions.ExpiredSignatureError:
                print('Access denied')
                if(not DoorLocked):
                    DoorLocked = True
                    print("Lock Door")
                    ServoPosition.ChangeDutyCycle(ServoLockPosition)
                pass
                
            except jwt.exceptions.DecodeError:
                print('Card content did not look like a JWT')
                pass


def destroy():
    GPIO.cleanup()


if __name__ == '__main__':     # Program start from here
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        destroy()