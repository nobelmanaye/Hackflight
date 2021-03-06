/*
   Butterfly implementation of Hackflight Board routines

   Copyright (c) 2018 Simon D. Levy

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

#include <Wire.h>
#include "boards/realboards/arduino.hpp"

namespace hf {

    class Butterfly : public ArduinoBoard {

         protected:

            virtual uint8_t serialTelemetryAvailable(void) override
            {
                return Serial2.available();
            }

            virtual uint8_t serialTelemetryRead(void) override
            {
                return Serial2.read();
            }

            virtual void serialTelemetryWrite(uint8_t c) override
            {
                Serial2.write(c);
            }

         public:

            Butterfly(void) 
                : ArduinoBoard(13, true) // red LED, active low
            {
                // Start telemetry on Serial2
                Serial2.begin(115200);

                // Hang a bit 
                delay(100);

                // Start I^2C
                Wire.begin();

                // Hang a bit
                delay(100);
            }

    }; // class Butterfly

} // namespace hf
