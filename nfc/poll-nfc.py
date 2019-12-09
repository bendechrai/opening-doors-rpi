#!/usr/bin/env python
# -*- coding: <encoding unicode > -*-

import string
import nxppy
import json
import time
import datetime
import jwt
import RPi.GPIO as GPIO
import emoji

mifare = nxppy.Mifare()
debug = False

# Get the PEM file from Auth0, and run `openssl x509 -pubkey -noout -in cert.pem  > pubkey.pem`
key=b'''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvupG3F3hKRzg8cxvF9Nr
QwPyCaJ0Vzi+jj/c3F3hCdhMEjZ8hFFq3VOK4R47B97bi9cft5J9gqVZ5QYjppMq
idWn10HvIvxSfXvaGdMCrAyhJaCSYOVFk2g7ZrxEwl1pv4l8rrTqs1cwWo+6m1kK
mxs8tF7PvyECVWx0jUoJOskDj/2LK2x4KfZdJztlvtB8J8yd8L/Pa/HQNSlIyB2i
7njosJxiW5cIMaB4GUIORmX4apnThuMH0jtSwBJyo/CNUGcGyEhAQww/uwBnFhtV
pPpKN1cyF/4iKV+zhDmnKkyHASoqzN+2uOFoDpL9CoxC8mbslWy/85zEQSR5Nqlb
5QIDAQAB
-----END PUBLIC KEY-----'''
aud='opensesame://door1/'

ServoPin = 32
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ServoPin, GPIO.OUT)
Servo = GPIO.PWM(ServoPin, 50)
Servo.start(0)
DoorLocked = True

def loop():
    while True:
        try:

            # READ NFC CARD
            uid = mifare.select()
            data = mifare.read()
            
            # DECODE JWT
            token = getNFCPayload(data)
            token_payload = jwt.decode(token, key, audience=aud)

            printTokenPayload(token_payload)

            # CALC SECONDS TO TOKEN EXPIRY
            timeNow=datetime.datetime.now().replace(microsecond=0)
            timeExp=datetime.datetime.fromtimestamp(token_payload['exp'])
            timeRemaining=timeExp-timeNow

            # PRINT SUCCESS MESSAGE
            print('Door 1 can be unlocked until ' + timeExp.strftime('%a %d %B at %H:%M:%S') + ' (' + str(timeRemaining.total_seconds()) + ' seconds remaining)')

            # UNLOCK THE DOOR
            unlockDoor()

        # IF TOKEN EXPIRED
        except jwt.exceptions.ExpiredSignatureError:

            # DECODE TOKEN WITHOUT VERIFICATION
            token_payload = jwt.decode(token, verify=False)

            printTokenPayload(token_payload)

            # HOW LONG AGO DID IT EXPIRE?
            timeNow=datetime.datetime.now().replace(microsecond=0)
            timeExp=datetime.datetime.fromtimestamp(token_payload['exp'])
            timeAgo=timeNow-timeExp

            # PRINT ERROR MESSAGE
            print('Access denied - token expired at ' + timeExp.strftime('%a %d %B at %H:%M:%S') + ' (' + str(timeAgo.total_seconds()) + ' seconds ago)')

            # MAKE SURE DOOR IS LOCKED
            lockDoor()
            pass

        # SOME UNKNOWN ERROR
        except nxppy.SelectError:
            # MAKE SURE DOOR IS LOCKED
            lockDoor()
            pass

        # NFC VALUE NOT A JWT?
        except jwt.exceptions.DecodeError:
            print('Card content did not look like a JWT')
            pass

        except MemoryError:
            pass

        print(emoji.emojize('\n:eyes:'))
        time.sleep(0.5)

def printTokenPayload(token_payload):
        # SHOW TOKEN PAYLOAD
        timeIat=datetime.datetime.fromtimestamp(token_payload['iat'])
        timeExp=datetime.datetime.fromtimestamp(token_payload['exp'])
        print('+---------------------------------------------------------------------------------------------------+')
        print('| TOKEN:                                                                                            |')
        print(string.ljust('|      SUB: ' + token_payload['sub'],                     100, ' ') +                 '|')
        print(string.ljust('|      IAT: ' + timeIat.strftime('%a %d %B at %H:%M:%S'), 100, ' ') +                 '|')
        print(string.ljust('|      EXP: ' + timeExp.strftime('%a %d %B at %H:%M:%S'), 100, ' ') +                 '|')
        print(string.ljust('|      AUD: ' + str(token_payload['aud']),                100, ' ') +                 '|')
        print(string.ljust('|      ISS: ' + token_payload['iss'],                     100, ' ') +                 '|')
        print(string.ljust('|      AZP: ' + token_payload['azp'],                     100, ' ') +                 '|')
        print(string.ljust('|    SCOPE: ' + token_payload['scope'],                   100, ' ') +                 '|')
        print('+---------------------------------------------------------------------------------------------------+')

def lockDoor():
    global DoorLocked
    if(not DoorLocked):
        DoorLocked = True
        print(emoji.emojize(":lock: :lock: :lock:  LOCK DOOR  :lock: :lock: :lock:", use_aliases=True))
        SetAngle(90)

def unlockDoor():
    global DoorLocked
    if(DoorLocked):
        DoorLocked = False
        print(emoji.emojize(":unlock: :unlock: :unlock: UNLOCK DOOR :unlock: :unlock: :unlock:", use_aliases=True))
        SetAngle(0)

def SetAngle(angle):
    duty = angle / 23 + 2
    GPIO.output(ServoPin, True)
    Servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(ServoPin, False)
    Servo.ChangeDutyCycle(0)

def destroy():
    GPIO.cleanup()




































def getNFCPayload(data):

    # Remove the NFC tag header and length from the data - store them even though we ignore them
    printIfDebug("# Remove the NFC tag header and length from the data - store them even though we ignore them")
    printIfDebug(list(data))
    header = ord(data[0])
    length = ord(data[1])
    printIfDebug("Header: " + str(header))
    printIfDebug("Length: " + str(length))

    # NDEF Message is the data from char 3 onwards
    printIfDebug("# NDEF Message is the data from char 3 onwards")
    ndef_message = data[2:]
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))

    # Remove the NDEF header from the message
    printIfDebug("# Remove the NDEF header from the message")
    ndef_header = ord(ndef_message[0])
    ndef_message = ndef_message[1:]
    printIfDebug("NDEF Header: " + str(ndef_header))
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))

    # Remove the NDEF Type Length from the message
    printIfDebug("# Remove the NDEF Type Length from the message")
    #ndef_type_length = ord(ndef_message[0])
    ndef_type_length = 1
    ndef_message = ndef_message[1:]
    printIfDebug("NDEF Type Length: " + str(ndef_type_length))
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))


    # Remove the Payload Length from the message
    printIfDebug("# Remove the Payload Length from the message")
    # NDEF Header bit 4 is the SR flag. 1 = PAYLOAD LENGTH field is 1 byte. 0 = PAYLOAD Length field is 4 bytes.
    if(ndef_header & 16 == 0):
        ndef_message = ndef_message[2:] # For some reason, non SR lengths have two extra bytes before the length. @TODO why?
        payload_length = 0
        payload_length += ord(ndef_message[0]) * 256 * 256 * 256
        payload_length += ord(ndef_message[1]) * 256 * 256
        payload_length += ord(ndef_message[2]) * 256
        payload_length += ord(ndef_message[3])
        ndef_message = ndef_message[4:]
    else:
        payload_length = ord(ndef_message[0])
        ndef_message = ndef_message[1:]
    printIfDebug("Payload Length: " + str(payload_length))
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))

    # Remove ID Length from the message, if IL flag (bit 3) is set
    printIfDebug("# Remove ID Length from the message, if IL flag (bit 3) is set")
    if(ndef_header & 8 == 8):
        ndef_id_length = ord(ndef_message[0])
        ndef_message = ndef_message[1:]
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))

    # Remove Record Type from the message
    printIfDebug("# Remove Record Type from the message")
    ndef_type = ndef_message[:ndef_type_length]
    ndef_message = ndef_message[ndef_type_length:]
    printIfDebug("NDEF Type: " + ndef_type)
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))

    # Remove Payload from the message
    payload = ndef_message[:payload_length]
    ndef_message = ndef_message[payload_length:]
    printIfDebug("Payload: " + payload)
    printIfDebug("NDEF Message")
    printIfDebug(list(ndef_message))

    # Extract language and token from payload
    payload_encoding = ord(payload[0:1])
    payload_lang = payload[1:3]
    payload = payload[3:payload_length]
    printIfDebug("Payload Encoding: " + str(payload_encoding))
    printIfDebug("Payload Language: " + payload_lang)
    printIfDebug("Payload: " + payload)

    return payload



def printIfDebug(output):
    if(debug):
        print(output)

if __name__ == '__main__':     # Program start from here
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        destroy()
