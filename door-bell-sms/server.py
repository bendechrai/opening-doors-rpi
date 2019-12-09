#!/usr/bin/env python

import string
import json
import http.client
import socket
import time
import datetime
import jwt
import RPi.GPIO as GPIO
import emoji
from twilio.rest import Client

ServoPin = 32
ServoLockPosition = 5
ServoUnlockPosition = 10.5

auth_client_id = "vJF3okNM6n1ryyRU7jH4uomKCH4fMw04"
auth_domain='opening-doors.auth0.com'
auth_audience='opensesame://door1/'
auth_pubkey='''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvupG3F3hKRzg8cxvF9Nr
QwPyCaJ0Vzi+jj/c3F3hCdhMEjZ8hFFq3VOK4R47B97bi9cft5J9gqVZ5QYjppMq
idWn10HvIvxSfXvaGdMCrAyhJaCSYOVFk2g7ZrxEwl1pv4l8rrTqs1cwWo+6m1kK
mxs8tF7PvyECVWx0jUoJOskDj/2LK2x4KfZdJztlvtB8J8yd8L/Pa/HQNSlIyB2i
7njosJxiW5cIMaB4GUIORmX4apnThuMH0jtSwBJyo/CNUGcGyEhAQww/uwBnFhtV
pPpKN1cyF/4iKV+zhDmnKkyHASoqzN+2uOFoDpL9CoxC8mbslWy/85zEQSR5Nqlb
5QIDAQAB
-----END PUBLIC KEY-----'''

twilio_sid='ACc3e25e6d1a9a5b1303e2d7d00a28533f'
twilio_token='5c190d53523ed37117b67f119dda8145'
twilio_config_domain='jsonbox.io'
twilio_config='https://jsonbox.io/box_a4a70d5f6a6c7c395d3e/door'

GPIO.setmode(GPIO.BOARD)               # Set the board mode to numbers pins by physical location
GPIO.setup(ServoPin, GPIO.OUT)         # Set Servo Pin mode as output
ServoPosition = GPIO.PWM(ServoPin, 50) # Set PWM to 50Hz
ServoPosition.start(ServoLockPosition) # Default servo to locked position
GPIO.cleanup()
DoorLocked = True

def waitForDoorBell():

    host = '192.168.43.11'
    port = 5000  # initiate port no above 1024
    server_socket = socket.socket()  # get instance
    server_socket.bind((host, port))  # bind host address and port together
    server_socket.listen(1)

    while True:
        print("Waiting for door bell")
        conn, address = server_socket.accept()  # accept new connection

        print("Ding dong!")
        handleDoorBell()

        conn.close()  # close the connection


def handleDoorBell():

    conn = http.client.HTTPSConnection(auth_domain);
    conn.request('POST', '/oauth/device/code', json.dumps({'client_id': auth_client_id, 'scope': 'openid profile', 'audience': auth_audience}), {"content-type": "application/json"})
    code_request = conn.getresponse()
    deviceConfig = json.loads(code_request.read())

    printDeviceConfig(deviceConfig)

    twilio_config_conn = http.client.HTTPSConnection(twilio_config_domain)
    twilio_config_conn.request('GET', twilio_config)
    twilio_config_request = twilio_config_conn.getresponse()
    twilio_config_data = json.loads(twilio_config_request.read())
    twilio_client = Client(twilio_sid, twilio_token)

    message = twilio_client.messages.create(
        body="Hi " + twilio_config_data[0]['name'] + ". Unlock your door with this URL: " + deviceConfig['verification_uri_complete'],
        from_='DOOR',
        to=twilio_config_data[0]['number']
    )
    print('SMS sent to ' + twilio_config_data[0]['name'])

    try:
        tokens = getToken(deviceConfig);
        id_token = jwt.decode(tokens["id_token"], auth_pubkey, audience=auth_client_id, algorithms=['RS256'])
        access_token = jwt.decode(tokens["access_token"], auth_pubkey, audience=auth_audience)

        printTokenPayload(id_token)
        printTokenPayload(access_token)

        # CALC SECONDS TO TOKEN EXPIRY
        timeNow=datetime.datetime.now().replace(microsecond=0)
        timeExp=datetime.datetime.fromtimestamp(access_token['exp'])
        timeRemaining=timeExp-timeNow

        # PRINT SUCCESS MESSAGE
        print('Door 1 can be unlocked until ' + timeExp.strftime('%a %d %B at %H:%M:%S') + ' (' + str(timeRemaining.total_seconds()) + ' seconds remaining)')

        unlockDoor()


    # IF TOKEN EXPIRED
    except jwt.exceptions.ExpiredSignatureError:

        # DECODE TOKEN WITHOUT VERIFICATION
        access_token = jwt.decode(tokens["access_token"], verify=False)
        printTokenPayload(access_token)

        # HOW LONG AGO DID IT EXPIRE?
        timeNow=datetime.datetime.now().replace(microsecond=0)
        timeExp=datetime.datetime.fromtimestamp(access_token['exp'])
        timeAgo=timeNow-timeExp

        # PRINT ERROR MESSAGE
        print('Access denied - token expired at ' + timeExp.strftime('%a %d %B at %H:%M:%S') + ' (' + str(timeAgo.total_seconds()) + ' seconds ago)')

        lockDoor()
        pass

    except jwt.exceptions.DecodeError:
        print('Card content did not look like a JWT')
        pass

    except MemoryError:
        pass




def getToken(deviceConfig):
    time.sleep(deviceConfig["interval"])

    print(emoji.emojize('\n:eyes:'))

    conn = http.client.HTTPSConnection(auth_domain);
    conn.request('POST', '/oauth/token', json.dumps({'grant_type': 'urn:ietf:params:oauth:grant-type:device_code', 'device_code': deviceConfig["device_code"], 'client_id': auth_client_id}), {"content-type": "application/json"})
    token_request = conn.getresponse()
    tokens = json.loads(token_request.read())

    if 'error' in tokens:

        if tokens["error"] == 'authorization_pending':
            # User has yet to authorize device code - recurse and try again
            print(emoji.emojize(':thumbs_down:'))
            return getToken(deviceConfig)

        if tokens["error"] == 'expired_token':
            # The device code has expired - return empty json object
            print(emoji.emojize(':thumbs_down:'))
            return "{}".json()

    if 'id_token' in tokens and 'access_token' in tokens:
        # Return tokens
        print(emoji.emojize(':thumbs_up:'))
        return tokens






def printDeviceConfig(deviceConfig):
        print('+-----------------------------------------------------------------------------------------------------+')
        print('| DEVICE CONFIG                                                                                       |')
        print(str.ljust('|               DEVICE CODE: ' + deviceConfig['device_code'],               102, ' ') + '|')
        print(str.ljust('|                  INTERVAL: ' + str(deviceConfig['interval']),             102, ' ') + '|')
        print(str.ljust('|                EXPIRES IN: ' + str(deviceConfig['expires_in']),           102, ' ') + '|')
        print(str.ljust('|          VERIFICATION URI: ' + deviceConfig['verification_uri'],          102, ' ') + '|')
        print(str.ljust('| VERIFICATION URI COMPLETE: ' + deviceConfig['verification_uri_complete'], 102, ' ') + '|')
        print(str.ljust('|                 USER CODE: ' + deviceConfig['user_code'],                 102, ' ') + '|')
        print('+-----------------------------------------------------------------------------------------------------+')

def printTokenPayload(token_payload):
        # SHOW TOKEN PAYLOAD
        print('+---------------------------------------------------------------------------------------------------+')
        print('| TOKEN:                                                                                            |')
        if( 'sub' in token_payload):
            print(str.ljust('|      SUB: ' + token_payload['sub'],                     100, ' ') +                 '|')
        if( 'name' in token_payload):
            print(str.ljust('|     NAME: ' + token_payload['name'],                    100, ' ') +                 '|')
        if( 'nickname' in token_payload):
            print(str.ljust('| NICKNAME: ' + token_payload['nickname'],                100, ' ') +                 '|')
        if( 'iat' in token_payload):
            timeIat=datetime.datetime.fromtimestamp(token_payload['iat'])
            print(str.ljust('|      IAT: ' + timeIat.strftime('%a %d %B at %H:%M:%S'), 100, ' ') +                 '|')
        if( 'exp' in token_payload):
            timeExp=datetime.datetime.fromtimestamp(token_payload['exp'])
            print(str.ljust('|      EXP: ' + timeExp.strftime('%a %d %B at %H:%M:%S'), 100, ' ') +                 '|')
        if( 'aud' in token_payload):
            print(str.ljust('|      AUD: ' + str(token_payload['aud']),                100, ' ') +                 '|')
        if( 'iss' in token_payload):
            print(str.ljust('|      ISS: ' + token_payload['iss'],                     100, ' ') +                 '|')
        if( 'azp' in token_payload):
            print(str.ljust('|      AZP: ' + token_payload['azp'],                     100, ' ') +                 '|')
        if( 'scope' in token_payload):
            print(str.ljust('|    SCOPE: ' + token_payload['scope'],                   100, ' ') +                 '|')
        print('+---------------------------------------------------------------------------------------------------+')

def lockDoor():
    global DoorLocked
    if(not DoorLocked):
        DoorLocked = True
        print(emoji.emojize(":lock: :lock: :lock:  LOCK DOOR  :lock: :lock: :lock:", use_aliases=True))
        GPIO.setmode(GPIO.BOARD)               # Set the board mode to numbers pins by physical location
        GPIO.setup(ServoPin, GPIO.OUT)         # Set Servo Pin mode as output
        ServoPosition.start(ServoLockPosition)
        time.sleep(0.1)
        GPIO.cleanup()

def unlockDoor():
    global DoorLocked
    if(DoorLocked):
        DoorLocked = False
        print(emoji.emojize(":unlock: :unlock: :unlock: UNLOCK DOOR :unlock: :unlock: :unlock:", use_aliases=True))
        GPIO.setmode(GPIO.BOARD)               # Set the board mode to numbers pins by physical location
        GPIO.setup(ServoPin, GPIO.OUT)         # Set Servo Pin mode as output
        ServoPosition.start(ServoUnlockPosition)
        time.sleep(0.1)
        GPIO.cleanup()

        # LOCK DOOR AFTER 5 SECONDS
        time.sleep(1)
        print('Door 1 locking in 4 seconds')
        time.sleep(1)
        print('Door 1 locking in 3 seconds')
        time.sleep(1)
        print('Door 1 locking in 2 seconds')
        time.sleep(1)
        print('Door 1 locking in 1 seconds')
        time.sleep(1)
        lockDoor()
        time.sleep(1)



if __name__ == '__main__':     # Program start from here
    try:
        waitForDoorBell()

    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        GPIO.cleanup()