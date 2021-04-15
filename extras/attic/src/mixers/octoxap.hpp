/*
   Mixer subclass for X-configuration octocopters following the ArduPilot numbering convention:

        5CCW   1CW
                  
    7CW           3CCW
                   
             ^      
                   
    6CW           8CCW
                   
        2CCW   4CW
 
   Copyright (C) 2021 Simon D. Levy

   MIT License
 */

#pragma once

#include <RFT_motor.hpp>

#include "mixer.hpp"

namespace hf {

    class MixerOctoXAP : public Mixer {

        public:

            MixerOctoXAP(rft::Motor * motors) 
                : Mixer(motors, 8)
            {
                //                     Th  Rl  Pi  Yw
                // XXX Pitch and yaw are probably inverted!
                motorDirections[0] = { +1, -1, -1, +1 }; // 1
                motorDirections[1] = { +1, +1, +1, +1 }; // 2    
                motorDirections[2] = { +1, -1, -1, -1 }; // 3 
                motorDirections[3] = { +1, -1, +1, -1 }; // 4 
                motorDirections[4] = { +1, +1, -1, -1 }; // 5 
                motorDirections[5] = { +1, +1, +1, -1 }; // 6 
                motorDirections[6] = { +1, +1, -1, +1 }; // 7  
                motorDirections[7] = { +1, -1, +1, +1 }; // 8 
            }
    };

} // namespac6
