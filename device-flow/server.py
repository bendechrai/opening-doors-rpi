#!/usr/bin/env python

import string
import json
import httplib
import time
import datetime
import jwt
import RPi.GPIO as GPIO
import emoji

ServoPin = 32
ServoLockPosition = 5
ServoUnlockPosition = 10.5

auth_client_id = "ZLN1lbika9cy8BnAyJSmE354yPGZpkK8"
auth_audience='opensesame://door1/'
auth_pubkey='''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuVyX3zIoJ1/5L0zx7rRZ
45EAXUViadzFyUO3Evy80164QQGyDqnkSHdZLXGtSimh4BExLoWs9GZemcFfhAmp
ER1C2kJ/ZevNBmW3sYxsNmDd6a/ehDieN+0pap+4qS6S80oW/yH5lyrPLD1v4+G2
1gQoAO7XCe9h2rswj1423ZQCgBac4MyjOKroVfjGWzPQYKkFw8MDmPV4RWuOFDoW
rR5nhdKd0CnJOLoq04JvSnr3uoDWjhZZHXpI/vLasVSmE2WEK86k3iclDpe5VdjU
d2zSczJfTWNwplMEENe7DD1Ri9CtG2+V0FNQ0W0YK/o4UxLW1Yg5jz13ISuigwVI
kQIDAQAB
-----END PUBLIC KEY-----
'''

GPIO.setmode(GPIO.BOARD)               # Set the board mode to numbers pins by physical location
GPIO.setup(ServoPin, GPIO.OUT)         # Set Servo Pin mode as output
ServoPosition = GPIO.PWM(ServoPin, 50) # Set PWM to 50Hz
ServoPosition.start(ServoLockPosition) # Default servo to locked position
GPIO.cleanup()
DoorLocked = True

def loop():

    conn = httplib.HTTPSConnection('bendechrai.auth0.com');
    conn.request('POST', '/oauth/device/code', json.dumps({'client_id': auth_client_id, 'scope': 'openid profile', 'audience': auth_audience}), {"content-type": "application/json"})
    code_request = conn.getresponse()
    deviceConfig = json.loads(code_request.read())

    printDeviceConfig(deviceConfig)

    try:
        tokens = getToken(deviceConfig);
        id_token = jwt.decode(tokens["id_token"], auth_pubkey, audience=auth_client_id)
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

    conn = httplib.HTTPSConnection('bendechrai.auth0.com');
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
        print(string.ljust('|               DEVICE CODE: ' + deviceConfig['device_code'],               102, ' ') + '|')
        print(string.ljust('|                  INTERVAL: ' + str(deviceConfig['interval']),             102, ' ') + '|')
        print(string.ljust('|                EXPIRES IN: ' + str(deviceConfig['expires_in']),           102, ' ') + '|')
        print(string.ljust('|          VERIFICATION URI: ' + deviceConfig['verification_uri'],          102, ' ') + '|')
        print(string.ljust('| VERIFICATION URI COMPLETE: ' + deviceConfig['verification_uri_complete'], 102, ' ') + '|')
        print(string.ljust('|                 USER CODE: ' + deviceConfig['user_code'],                 102, ' ') + '|')
        print('+-----------------------------------------------------------------------------------------------------+')

def printTokenPayload(token_payload):
        # SHOW TOKEN PAYLOAD
        print('+---------------------------------------------------------------------------------------------------+')
        print('| TOKEN:                                                                                            |')
        if( 'sub' in token_payload):
            print(string.ljust('|      SUB: ' + token_payload['sub'],                     100, ' ') +                 '|')
        if( 'name' in token_payload):
            print(string.ljust('|     NAME: ' + token_payload['name'],                    100, ' ') +                 '|')
        if( 'nickname' in token_payload):
            print(string.ljust('| NICKNAME: ' + token_payload['nickname'],                100, ' ') +                 '|')
        if( 'iat' in token_payload):
            timeIat=datetime.datetime.fromtimestamp(token_payload['iat'])
            print(string.ljust('|      IAT: ' + timeIat.strftime('%a %d %B at %H:%M:%S'), 100, ' ') +                 '|')
        if( 'exp' in token_payload):
            timeExp=datetime.datetime.fromtimestamp(token_payload['exp'])
            print(string.ljust('|      EXP: ' + timeExp.strftime('%a %d %B at %H:%M:%S'), 100, ' ') +                 '|')
        if( 'aud' in token_payload):
            print(string.ljust('|      AUD: ' + str(token_payload['aud']),                100, ' ') +                 '|')
        if( 'iss' in token_payload):
            print(string.ljust('|      ISS: ' + token_payload['iss'],                     100, ' ') +                 '|')
        if( 'azp' in token_payload):
            print(string.ljust('|      AZP: ' + token_payload['azp'],                     100, ' ') +                 '|')
        if( 'scope' in token_payload):
            print(string.ljust('|    SCOPE: ' + token_payload['scope'],                   100, ' ') +                 '|')
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
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        GPIO.cleanup()
