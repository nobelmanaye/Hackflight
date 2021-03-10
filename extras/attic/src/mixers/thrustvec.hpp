/*
   Mixer subclass for thrust vectoring

   Copyright (c) 2020 Simon D. Levy

   This file is part of Hackflight.

   Hackflight is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Hackflight is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MEReceiverHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with Hackflight.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include "board.hpp"
#include "datatypes.hpp"
#include "mixer.hpp"

namespace hf {

    class MixerThrustVector : public Mixer {

        public:

            MixerThrustVector(void) 
                : Mixer(4)
            {
                //                     Th   RR   PF  YR
                motorDirections[0] = { +1,  0,   0, +1 };   // rotor 1
                motorDirections[1] = { +1,  0,   0, -1 };   // rotor 2
                motorDirections[2] = {  0, +1,   0,  0 };   // servo 1
                motorDirections[3] = {  0,  0 , +1,  0 };   // servo 2
             }

        protected:

            virtual float constrainMotorValue(uint8_t index, float value) override
            {
                return index < 2 ? Mixer::constrainMotorValue(index, value) : value;
            }

    };

} // namespace
