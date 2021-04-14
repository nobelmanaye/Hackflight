/*
   Test DSMX => SBUS translation

   Copyright (c) 2021 Simon D. Levy

   MIT License
 */

#include <DSMRX.h>
#include <SBUS.h>

DSM2048 rx;

SBUS sbus = SBUS(Serial2);

static float val;
static int8_t dir;


void serialEvent1(void)
{
    while (Serial1.available()) {
        rx.handleSerialEvent(Serial1.read(), micros());
    }
}

void setup(void)
{
    val = -1;
    dir = +1;

    Serial1.begin(115000);

    sbus.begin();
}

void loop(void)
{
    static float outvals[16] = {};

    if (rx.timedOut(micros())) {
        Serial.println("*** TIMED OUT ***");
    }

    else if (rx.gotNewFrame()) {

        float values[8];

        rx.getChannelValuesNormalized(values, 8);

        for (int k=0; k<4; ++k) {
            outvals[k] = values[k];
            Serial.print("Ch. ");
            Serial.print(k+1);
            Serial.print(": ");
            Serial.print(values[k]);
            Serial.print("    ");
        }

        Serial.println();

    }

    // outvals[3] = val;

    sbus.writeCal(outvals);

/*

    val += dir * .005;

    if (val >= +1) {
        dir = -1;
    }

    if (val <= -1) {
        dir = +1;
    }

    delay(10);
    */
}

