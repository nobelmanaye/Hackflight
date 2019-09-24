/*
   Spektrum DSMX support for Arduino flight controllers

   This file is part of Hackflight.

   Hackflight is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Hackflight is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with Hackflight.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include "receiver.hpp"
#include <DSMRX.h>

static DSM2048 _rx;

// Support different UARTs

static HardwareSerial * _hardwareSerial;

static void handleEvent(void)
{
    while (_hardwareSerial->available()) {
        _rx.handleSerialEvent(_hardwareSerial->read(), micros());
    }
}

void serialEvent1(void)
{
    handleEvent();
}

void serialEvent2(void)
{
    handleEvent();
}

void serialEvent3(void)
{
    handleEvent();
}

namespace hf {

    class DSMX_Receiver : public Receiver {

         protected:

            void begin(void)
            {
                _hardwareSerial->begin(115200);
            }

            bool gotNewFrame(void)
            {
                return _rx.gotNewFrame();
            }

            void readRawvals(void)
            {
                _rx.getChannelValuesNormalized(rawvals, MAXCHAN);
            }

            bool lostSignal(void)
            {
                return _rx.timedOut(micros());
            }

        public:

            DSMX_Receiver(const uint8_t channelMap[6], HardwareSerial * hardwareSerial=&Serial1) 
                :  Receiver(channelMap) 
            { 
                _hardwareSerial = hardwareSerial;
            }

    }; // class DSMX_Receiver

} // namespace hf
