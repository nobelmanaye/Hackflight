#!/usr/bin/env python3
'''
Uses MSPPG to request and handle attitude messages from flight controller

Copyright (C) Simon D. Levy 2021

MIT License
'''

from msp import Parser
import serial
from time import sleep
from sys import stdout
import argparse
import struct

class AttitudeParser(Parser):

    def dispatchMessage(self):

        if self.message_id == 121:
            self.handle_RC_NORMAL(*struct.unpack('=ffffff', self.message_buffer))

        if self.message_id == 122:
            self.handle_ATTITUDE_RADIANS(*struct.unpack('=fff', self.message_buffer))

    @staticmethod
    def serialize_ATTITUDE_RADIANS_Request():
        msg = '$M<' + chr(0) + chr(122) + chr(122)
        return bytes(msg, 'utf-8')

    def handle_ATTITUDE_RADIANS(self, roll, pitch, yaw):

        print('%+3.3f %+3.3f %+3.3f' % (roll, pitch, yaw))
        stdout.flush()
        port.write(request)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(dest='com_port', help='COM port')

    # Parse and print the results
    args = parser.parse_args()

    parser = AttitudeParser()
    request = AttitudeParser.serialize_ATTITUDE_RADIANS_Request()
    port = serial.Serial(args.com_port, 115200)

    # Connecting causes reboot on ESP32
    sleep(1)

    port.write(request)

    while True:

        try:

            parser.parse(port.read(1))

        except KeyboardInterrupt:

            break

