/*
   Mixer subclass for X-configuration quadcopters following the MultiWii numbering convention:

    4cw   2ccw
       \ /
        ^
       / \
    3ccw  1cw
 
   Copyright (c) 2018 Simon D. Levy

   MIT License
 */

#pragma once

#include "actuators/mixers_new/quad_new.hpp"
#include "motor_new.hpp"

namespace hf {

    class NewMixerQuadXMW : public NewQuadMixer {

        public:

            NewMixerQuadXMW(NewMotor * motor1, NewMotor * motor2, NewMotor * motor3, NewMotor * motor4) 
                : NewQuadMixer(motor1, motor2, motor3, motor4)
            {
                //                     Th  RR  PF  YR
                motorDirections[0] = { +1, -1, +1, -1 };    // 1 right rear
                motorDirections[1] = { +1, -1, -1, +1 };    // 2 right front
                motorDirections[2] = { +1, +1, +1, +1 };    // 3 left rear
                motorDirections[3] = { +1, +1, -1, -1 };    // 4 left front
            }

    }; // class NewMixerQuadXMW

} // namespace
