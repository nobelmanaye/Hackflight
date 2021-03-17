#!/usr/bin/env python3
'''
Main script for  Hackflight GCS

Copyright (C) Simon D. Levy 2021

MIT License
'''

DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 600

SPLASH_LOCATION = 430,260

BACKGROUND_COLOR = 'white'

CONNECTION_DELAY_MSEC  = 4000

USB_UPDATE_MSEC = 200

from comms import Comms
from serial.tools.list_ports import comports
import os
import tkcompat as tk

import msppg

from imu import IMU
from motors import Motors
from receiver import Receiver
from resources import resource_path

# GCS class runs the show =========================================================================================

#####################################################################
import struct
import sys

def _CRC8(data):

    crc = 0x00
   
    for c in data:

        crc ^= ord(c) if sys.version[0] == '2' else c

    return crc

def serialize_SET_MOTOR_NORMAL(m1, m2, m3, m4):
    '''
    Serializes the contents of a message of type SET_MOTOR_NORMAL.
    '''
    message_buffer = struct.pack('ffff', m1, m2, m3, m4)

    msg = [len(message_buffer), 215] + list(message_buffer)
    return bytes([ord('$'), ord('M'), ord('<')] + msg + [_CRC8(msg)])
#####################################################################


class GCS(msppg.Parser):

    def __init__(self):

        msppg.Parser.__init__(self)

        # No communications or arming yet
        self.comms = None
        self.armed = False
        self.gotimu = False

        # Do basic Tk initialization
        self.root = tk.Tk()
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.resizable(False, False)
        self.root.title('Hackflight Ground Control Station')
        left = (self.root.winfo_screenwidth() - DISPLAY_WIDTH) / 2
        top = (self.root.winfo_screenheight() - DISPLAY_HEIGHT) / 2
        self.root.geometry('%dx%d+%d+%d' % (DISPLAY_WIDTH, DISPLAY_HEIGHT, left, top))
        self.frame = tk.Frame(self.root)

        # Too much hassle on Windows
        if 'nt' != os.name:
            self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage('icon.xbm'))

        self.root.protocol('WM_DELETE_WINDOW', self.quit)

        # Create panes for two rows of widgets
        self.pane1 = self._add_pane()
        self.pane2 = self._add_pane()

        # Add a buttons
        self.button_connect = self._add_button('Connect', self.pane1, self._connect_callback)
        self.button_imu  = self._add_button('IMU',  self.pane2, self._imu_callback)
        self.button_motors = self._add_button('Motors', self.pane2, self._motors_button_callback)
        self.button_receiver = self._add_button('Receiver', self.pane2, self._receiver_button_callback)
        #self.button_messages = self._add_button('Messages', self.pane2, self._messages_button_callback)
        #self.button_maps = self._add_button('Maps', self.pane2, self._maps_button_callback, disabled=False)

        # Prepare for adding ports as they are detected by our timer task
        self.portsvar = tk.StringVar(self.root)
        self.portsmenu = None
        self.connected = False
        self.ports = []

        # Finalize Tk stuff
        self.frame.pack()
        self.canvas = tk.Canvas(self.root, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, background='black')
        self.canvas.pack()


        # Set up a text label for reporting errors
        errmsg = 'No response from board.  Possible reasons:\n\n' + \
                 '    * You connected to the wrong port.\n\n' + \
                 '    * Firmware uses serial receiver\n' + \
                 '      (DSMX, SBUS), but receiver is\n' + \
                 '      not connected.'
        self.error_label = tk.Label(self.canvas, text=errmsg, bg='black', fg='red', font=(None,24), justify=tk.LEFT)
        self.hide(self.error_label)

        # Add widgets for motor-testing dialog; hide them immediately
        self.motors = Motors(self)
        self.motors.stop()

        # Create receiver dialog
        self.receiver = Receiver(self)

        # Create messages dialog
        #self.messages = Messages(self)

        # Create IMU dialog
        self.imu = IMU(self)
        self._schedule_connection_task()

        # Create a maps dialog
        #self.maps = Maps(self, yoffset=-30)

        # Create a splash image
        self.splashimage = tk.PhotoImage(file=resource_path('splash.gif'))
        self._show_splash()

        # Set up parser's request strings
        self.attitude_request = msppg.serialize_ATTITUDE_RADIANS_Request()
        self.rc_request = msppg.serialize_RC_NORMAL_Request()

        # No messages yet
        self.roll_pitch_yaw = [0]*3
        self.rxchannels = [0]*6

        # A hack to support display in IMU dialog
        self.active_axis = 0

    def quit(self):
        self.motors.stop()
        self.root.destroy()

    def hide(self, widget):

        widget.place(x=-9999)

    def getChannels(self):

        return self.rxchannels

    def getRollPitchYaw(self):

        # configure button to show connected
        self._enable_buttons()
        self.button_connect['text'] = 'Disconnect'
        self._enable_button(self.button_connect)

        return self.roll_pitch_yaw

    def checkArmed(self):

        if self.armed:

            self._show_armed(self.root)
            self._show_armed(self.pane1)
            self._show_armed(self.pane2)

            self._disable_button(self.button_motors)

        else:

            self._show_disarmed(self.root)
            self._show_disarmed(self.pane1)
            self._show_disarmed(self.pane2)

    def scheduleTask(self, delay_msec, task):

        self.root.after(delay_msec, task)

    def handle_RC_NORMAL(self, c1, c2, c3, c4, c5, c6):

        # Display throttle as [0,1], other channels as [-1,+1]
        self.rxchannels = c1/2.+.5, c2, c3, c4, c5, c6

        # As soon as we handle the callback from one request, send another request, if receiver dialog is running
        if self.receiver.running:
            self._send_rc_request()

        #self.messages.setCurrentMessage('Receiver: %04d %04d %04d %04d %04d' % (c1, c2, c3, c4, c5))

    def handle_ATTITUDE_RADIANS(self, x, y, z):

        self.roll_pitch_yaw = x, y, z  

        self.gotimu = True

        #self.messages.setCurrentMessage('Roll/Pitch/Yaw: %+3.3f %+3.3f %+3.3f' % self.roll_pitch_yaw)

        # As soon as we handle the callback from one request, send another request, if IMU dialog is running
        if self.imu.running:
            self._send_attitude_request()

    def _add_pane(self):

        pane = tk.PanedWindow(self.frame, bg=BACKGROUND_COLOR)
        pane.pack(fill=tk.BOTH, expand=1)
        return pane

    def _add_button(self, label, parent, callback, disabled=True):

        button = tk.Button(parent, text=label, command=callback)
        button.pack(side=tk.LEFT)
        button.config(state = 'disabled' if disabled else 'normal')
        return button

    # Callback for IMU button
    def _imu_callback(self):

        self._clear()

        self.motors.stop()
        self.receiver.stop()
        #self.messages.stop()
        #self.maps.stop()

        self._send_attitude_request()
        self.imu.start()

    def _start(self):

        self._send_attitude_request()
        self.imu.start()

        self.gotimu = False
        self.hide(self.error_label)
        self.scheduleTask(CONNECTION_DELAY_MSEC, self._checkimu)

    def _checkimu(self):

        if not self.gotimu:

            self.imu.stop()
            self.error_label.place(x=50, y=50)
            self._disable_button(self.button_imu)
            self._disable_button(self.button_motors)
            self._disable_button(self.button_receiver)

    # Sends Attitude request to FC
    def _send_attitude_request(self):

        self.comms.send_request(self.attitude_request)

    # Sends RC request to FC
    def _send_rc_request(self):

        self.comms.send_request(self.rc_request)

    # Callback for Motors button
    def _motors_button_callback(self):

        self._clear()

        self.imu.stop()
        self.receiver.stop()
        #self.messages.stop()
        #self.maps.stop()
        self.motors.start()

    def _clear(self):

        self.canvas.delete(tk.ALL)

    # Callback for Receiver button
    def _receiver_button_callback(self):

        self._clear()

        self.imu.stop()
        self.motors.stop()
        #self.messages.stop()
        #self.maps.stop()

        self._send_rc_request()
        self.receiver.start()

    # Callback for Messages button
    def _messages_button_callback(self):

        self._clear()

        self.imu.stop()
        self.motors.stop()
        #self.maps.stop()
        self.receiver.stop()

        self.messages.start()

    def _getting_messages(self):

        return self.button_connect['text'] == 'Disconnect'

    # Callback for Maps button
    def _maps_button_callback(self):

        self._clear()

        if self._getting_messages():

            self.receiver.stop()
            self.messages.stop()
            self.imu.stop()
            self.motors.stop()

        #self.maps.start()

    # Callback for Connect / Disconnect button
    def _connect_callback(self):

        if self.connected:

            self.imu.stop()
            #self.maps.stop()
            self.motors.stop()
            #self.messages.stop()
            self.receiver.stop()

            if not self.comms is None:

                self.comms.stop()

            self._clear()

            self._disable_buttons()

            self.button_connect['text'] = 'Connect'

            self.hide(self.error_label)

            self._show_splash()

        else:

            #self.maps.stop()

            self.comms = Comms(self)
            self.comms.start()

            self.button_connect['text'] = 'Connecting ...'
            self._disable_button(self.button_connect)

            self._hide_splash()

            self.scheduleTask(CONNECTION_DELAY_MSEC, self._start)

        self.connected = not self.connected

    # Gets available ports
    def _getports(self):

        allports = comports()

        ports = []

        for port in allports:
            
            portname = port[0]

            if 'usbmodem' in portname or 'ttyACM' in portname or 'ttyUSB' in portname or 'COM' in portname:
                if not portname in ['COM1', 'COM2']:
                    ports.append(portname)

        return ports

    # Checks for changes in port status (hot-plugging USB cables)
    def _connection_task(self):

        ports = self._getports()

        if ports != self.ports:

            if self.portsmenu is None:

                self.portsmenu = tk.OptionMenu(self.pane1, self.portsvar, *ports)

            else:

                for port in ports:

                    self.portsmenu['menu'].add_command(label=port)

            self.portsmenu.pack(side=tk.LEFT)

            # Disconnected
            if ports == []:

                self.portsmenu['menu'].delete(0, 'end')
                self.portsvar.set('') 
                self._disable_button(self.button_connect)
                self._disable_buttons()

            # Connected
            else:
                self.portsvar.set(ports[0]) # default value
                self._enable_button(self.button_connect)

            self.ports = ports

        self._schedule_connection_task()

    # Mutually recursive with above
    def _schedule_connection_task(self):

        self.root.after(USB_UPDATE_MSEC, self._connection_task)

    def _disable_buttons(self):

        self._disable_button(self.button_imu)
        self._disable_button(self.button_motors)
        self._disable_button(self.button_receiver)
        #self._disable_button(self.button_messages)

    def _enable_buttons(self):

        self._enable_button(self.button_imu)
        self._enable_button(self.button_motors)
        self._enable_button(self.button_receiver)
        #self._enable_button(self.button_messages)

    def _enable_button(self, button):

        button['state'] = 'normal'

    def _disable_button(self, button):

        button['state'] = 'disabled'

    def sendMotorMessage(self, index, percent):

        values = [0]*4
        values[index-1] = percent / 100.
        self.comms.send_message(serialize_SET_MOTOR_NORMAL, values)

    def _show_splash(self):

        self.splash = self.canvas.create_image(SPLASH_LOCATION, image=self.splashimage)

    def _hide_splash(self):

        self.canvas.delete(self.splash)

    def _show_armed(self, widget):

        widget.configure(bg='red')

    def _show_disarmed(self, widget):

        widget.configure(bg=BACKGROUND_COLOR)

        if self._getting_messages():

            self._enable_button(self.button_motors)

    def _handle_calibrate_response(self):

        self.imu.showCalibrated()

    def _handle_params_response(self, pitchroll_kp_percent, yaw_kp_percent):

        # Only handle parms from firmware on a fresh connection
        if self.newconnect:

            self.imu.setParams(pitchroll_kp_percent, yaw_kp_percent)

        self.newconnect = False

    def _handle_arm_status(self, armed):

        self.armed = armed

        #self.messages.setCurrentMessage('ArmStatus: %s' % ('ARMED' if armed else 'Disarmed'))

    def _handle_battery_status(self, volts, amps):

        return
        #self.messages.setCurrentMessage('BatteryStatus: %3.3f volts, %3.3f amps' % (volts, amps))

# Main ==============================================================================================================

if __name__ == "__main__":

    gcs = GCS()

    tk.mainloop()
