#!/usr/bin/env python
# -*- coding: <encoding unicode > -*-

import nxppy
import json
import time
import datetime
import jwt
import emoji

mifare = nxppy.Mifare()

def loop():
    while True:
        try:

            # READ NFC CARD
            uid = mifare.select()
            data = mifare.read()
            print(data)

        except nxppy.SelectError:
            pass

        except MemoryError:
            pass

        print('...')
        time.sleep(0.5)

    loop()

def destroy():
    print("End")

if __name__ == '__main__':     # Program start from here
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        destroy()
