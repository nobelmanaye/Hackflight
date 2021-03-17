#!/usr/bin/env python3
'''
Dependencies: numpy, matplotlib, https://github.com/simondlevy/RealtimePlotter

Copyright (C) 2021 Simon D. Levy

MIT License
'''


import serial
from realtime_plot import RealtimePlotter
import numpy as np
from threading import Thread
from sys import argv, stdout

# Change these to suit your needs
PORT = '/dev/ttyACM0'
BAUD = 115200

NTICKS = 10

class SerialPlotter(RealtimePlotter):

    def __init__(self):

        ranges = [(-1,5), (-5,+5), (-5,+5)]

        RealtimePlotter.__init__(self, 
                ranges, 
                show_yvals=True,
                ylabels=['Altitude', 'Variometer', 'FirstDiff'],
                window_name='Altitude Estimation',
                styles=['b', 'r', 'g'])

        self.tick = 0
        self.vals = None

    def getValues(self):

         return self.vals

def _update(port, plotter):

    while True:

        plotter.vals = [float(s) for s in port.readline().decode()[:-1].split()]

        plotter.tick += 1

if __name__ == '__main__':

    port = argv[1] if len(argv) > 1 else PORT

    try:
        port = serial.Serial(port, BAUD)
    except serial.SerialException:
        print('Unable to open device on port %s' % PORT)
        exit(1)

    plotter = SerialPlotter()

    thread = Thread(target=_update, args = (port, plotter))
    thread.daemon = True
    thread.start()

    plotter.start()
