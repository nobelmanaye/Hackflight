/*
   Simple linear algebra support
   
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

#include <string.h>
#include <debugger.hpp>

namespace hf {

    class Matrix {

        private:

            // avoid dynamic memory allocation
            static const uint8_t MAXSIZE = 10;

            uint8_t _rows = 0;
            uint8_t _cols0;

            float _vals[MAXSIZE][MAXSIZE];

        public:

            Matrix(uint8_t rows, uint8_t cols) 
            {
                _rows = rows;
                _cols = cols;
                memset(_vals, 0, rows*cols*sizeof(float));
            }

            float get(uint8_t j, uint8_t k)
            {
                return _vals[j][k];
            }

            float set(uint8_t j, uint8_t k, float val)
            {
                _vals[j][k] = val;
            }

            void dump(void)
            {
                for (uint8_t j=0; j<_rows; ++j) {
                    for (uint8_t k=0; k<_cols; ++k) {
                        Debugger::printf("%+2.2f ", _vals[j][k]);
                    }
                    Debugger::printf("\n");
                }
            }

            static void trans(Matrix & a, Matrix & at)
            {
                for (uint8_t j=0; j<a._rows; ++j) {
                    for (uint8_t k=0; k<a._cols; ++k) {
                        at._vals[k][j] = a._vals[j][k];
                    }
                }
            }

            static void mult(Matrix & a, Matrix & b, Matrix & c)
            {
                for(uint8_t i=0; i<a._rows; ++i) {
                    for(uint8_t j=0; j<b._cols; ++j) {
                        c._vals[i][j] = 0;
                        for(uint8_t k=0; k<a._cols; ++k) {
                            c._vals[i][j] += a._vals[i][k] *b._vals[k][j];
                        }
                    }
                }
            }

    };  // class Matrix

} // namespace hf
