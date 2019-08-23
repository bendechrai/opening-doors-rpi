#!/usr/bin/env python

import requests
import time
import jwt
#import RPi.GPIO as GPIO

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

code_request = requests.post('https://bendechrai.auth0.com/oauth/device/code', data={'client_id': auth_client_id, 'scope': 'openid profile', 'audience': auth_audience})
deviceConfig = code_request.json()

print("------------------------------")
print("Log in at " + deviceConfig["verification_uri_complete"]);
print("------------------------------")

def getToken(deviceConfig):
  time.sleep(deviceConfig["interval"])
  token_request = requests.post('https://bendechrai.auth0.com/oauth/token', data={'grant_type': 'urn:ietf:params:oauth:grant-type:device_code', 'device_code': deviceConfig["device_code"], 'client_id': auth_client_id})
  token = token_request.json()

  if 'error' in token:

    if token["error"] == 'authorization_pending':
      # User has yet to authorize device code - recurse and try again
      return getToken(deviceConfig)

    if token["error"] == 'expired_token':
      # The device code has expired - return empty json object
      return "{}".json()

  if 'id_token' in token and 'access_token' in token:
    # Return token
    return token

token = getToken(deviceConfig);
id_token = jwt.decode(token["id_token"], auth_pubkey, audience=auth_client_id)
access_token = jwt.decode(token["access_token"], auth_pubkey, audience=auth_audience)

print(id_token)
print(access_token)


# ServoPin = 32
# ServoUnlockPosition = 5
# ServoLockPosition = 10
# 
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(ServoPin, GPIO.OUT)
# ServoPosition = GPIO.PWM(ServoPin, 50)
# ServoPosition.start(ServoLockPosition)


#             print('Door 1 can be unlocked until ' + timeExp.strftime('%a %d %B at %H:%M:%S') + ' (' + str(timeRemaining.total_seconds()) + ' seconds remaining)')
#             if(DoorLocked):
#                 DoorLocked = False
#                 print("Unlock Door")
#                 ServoPosition.ChangeDutyCycle(ServoUnlockPosition)
#                 print("Wait 5 seconds (let someone open the door)")
#                 time.sleep(5)
# 
#         except jwt.exceptions.ExpiredSignatureError:
#             print('Access denied')
#             if(not DoorLocked):
#                 DoorLocked = True
#                 print("Lock Door")
#                 ServoPosition.ChangeDutyCycle(ServoLockPosition)
#             pass
# 
#         except nxppy.SelectError:
#             if(not DoorLocked):
#                 DoorLocked = True
#                 print("Lock Door")
#                 ServoPosition.ChangeDutyCycle(ServoLockPosition)
#             pass
# 
#         except jwt.exceptions.DecodeError:
#             print('Card content did not look like a JWT')
#             pass
# 
#         except MemoryError:
#             pass
# 
#         print('Waiting')
#         time.sleep(0.5)
# 
# 
# def destroy():
#     GPIO.cleanup()
# 
# 
# 
# def getNFCPayload(data):
# 
#     # Remove the NFC tag header and length from the data - store them even though we ignore them
#     printIfDebug("# Remove the NFC tag header and length from the data - store them even though we ignore them")
#     printIfDebug(list(data))
#     header = ord(data[0])
#     length = ord(data[1])
#     printIfDebug("Header: " + str(header))
#     printIfDebug("Length: " + str(length))
# 
#     # NDEF Message is the data from char 3 onwards
#     printIfDebug("# NDEF Message is the data from char 3 onwards")
#     ndef_message = data[2:]
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
#     # Remove the NDEF header from the message
#     printIfDebug("# Remove the NDEF header from the message")
#     ndef_header = ord(ndef_message[0])
#     ndef_message = ndef_message[1:]
#     printIfDebug("NDEF Header: " + str(ndef_header))
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
#     # Remove the NDEF Type Length from the message
#     printIfDebug("# Remove the NDEF Type Length from the message")
#     #ndef_type_length = ord(ndef_message[0])
#     ndef_type_length = 1
#     ndef_message = ndef_message[1:]
#     printIfDebug("NDEF Type Length: " + str(ndef_type_length))
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
# 
#     # Remove the Payload Length from the message
#     printIfDebug("# Remove the Payload Length from the message")
#     # NDEF Header bit 4 is the SR flag. 1 = PAYLOAD LENGTH field is 1 byte. 0 = PAYLOAD Length field is 4 bytes.
#     if(ndef_header & 16 == 0):
#         ndef_message = ndef_message[2:] # For some reason, non SR lengths have two extra bytes before the length. @TODO why?
#         payload_length = 0
#         payload_length += ord(ndef_message[0]) * 256 * 256 * 256
#         payload_length += ord(ndef_message[1]) * 256 * 256
#         payload_length += ord(ndef_message[2]) * 256
#         payload_length += ord(ndef_message[3])
#         ndef_message = ndef_message[4:]
#     else:
#         payload_length = ord(ndef_message[0])
#         ndef_message = ndef_message[1:]
#     printIfDebug("Payload Length: " + str(payload_length))
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
#     # Remove ID Length from the message, if IL flag (bit 3) is set
#     printIfDebug("# Remove ID Length from the message, if IL flag (bit 3) is set")
#     if(ndef_header & 8 == 8):
#         ndef_id_length = ord(ndef_message[0])
#         ndef_message = ndef_message[1:]
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
#     # Remove Record Type from the message
#     printIfDebug("# Remove Record Type from the message")
#     ndef_type = ndef_message[:ndef_type_length]
#     ndef_message = ndef_message[ndef_type_length:]
#     printIfDebug("NDEF Type: " + ndef_type)
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
#     # Remove Payload from the message
#     payload = ndef_message[:payload_length]
#     ndef_message = ndef_message[payload_length:]
#     printIfDebug("Payload: " + payload)
#     printIfDebug("NDEF Message")
#     printIfDebug(list(ndef_message))
# 
#     # Extract language and token from payload
#     payload_encoding = ord(payload[0:1])
#     payload_lang = payload[1:3]
#     payload = payload[3:payload_length]
#     printIfDebug("Payload Encoding: " + str(payload_encoding))
#     printIfDebug("Payload Language: " + payload_lang)
#     printIfDebug("Payload: " + payload)
# 
#     return payload
# 
# 
# 
# def printIfDebug(output):
#     if(debug):
#         print(output)
# 
# if __name__ == '__main__':     # Program start from here
#     try:
#         loop()
#     except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
#         destroy()
