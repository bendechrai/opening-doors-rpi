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
from config import *

ServoPin = 32
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ServoPin, GPIO.OUT)
Servo = GPIO.PWM(ServoPin, 25)
Servo.start(0)
DoorLocked = True

server_socket = socket.socket()

def waitForDoorBell():

    host = '192.168.2.10'
    port = 5000  # initiate port no above 1024
    server_socket.bind((host, port))  # bind host address and port together
    server_socket.listen(1)

    while True:
        print("Waiting for door bell")
        conn, address = server_socket.accept()  # accept new connection

        with conn:
            data = conn.recv(1024).split()
            if data[1] == b'/doorbell':
                print("Ding dong!")
                handleDoorBell()
            if data[1] == b'/lock':
                print("Lock!")
                lockDoor()
            if data[1] == b'/unlock':
                print("Unlock!")
                unlockDoor()

        conn.close()  # close the connection


def handleDoorBell():

    conn = http.client.HTTPSConnection(auth_domain);
    conn.request('POST', '/oauth/device/code', json.dumps({'client_id': auth_client_id, 'scope': 'openid profile', 'audience': auth_audience}), {"content-type": "application/json"})
    code_request = conn.getresponse()
    deviceConfig = json.loads(code_request.read())

    printDeviceConfig(deviceConfig)

    jsonbin_conn = http.client.HTTPSConnection(jsonbin_domain)
    jsonbin_conn.request('GET', jsonbin_request, '', { "X-Master-key": jsonbin_master_key })
    jsonbin_response = jsonbin_conn.getresponse()
    jsonbin_data = json.loads(jsonbin_response.read())

    twilio_client = Client(twilio_sid, twilio_token)

    # SEND MESSAGE TO LAST PERSON ON LIST
    message = twilio_client.messages.create(
        body="Hi " + jsonbin_data['record']['name'] + ". Unlock your door with this URL: " + deviceConfig['verification_uri_complete'],
        from_='DOOR',
        to=jsonbin_data['record']['number']
    )
    print('Unlock URL sent to the last person to SMS us!')

    # SEND MESSAGE TO BEN TOO, JUST IN CASE
    message = twilio_client.messages.create(
        body="As a backup, here's the unlock URL: " + deviceConfig['verification_uri_complete'],
        from_='DOOR',
        to='+61415127120'
    )

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
        SetAngle(90)

def unlockDoor():
    global DoorLocked
    if(DoorLocked):
        DoorLocked = False
        print(emoji.emojize(":unlock: :unlock: :unlock: UNLOCK DOOR :unlock: :unlock: :unlock:", use_aliases=True))
        SetAngle(0)

def SetAngle(angle):
    duty = angle / 34 + 3
    GPIO.output(ServoPin, True)
    Servo.ChangeDutyCycle(duty)
    time.sleep(0.2)
    GPIO.output(ServoPin, False)
    Servo.ChangeDutyCycle(0)

if __name__ == '__main__':     # Program start from here
    try:
        waitForDoorBell()

    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        GPIO.cleanup()
        if server_socket:
            server_socket.close()

