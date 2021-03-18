/*
   ESP8266 support for Arduino flight controllers

   Copyright (c) 2021 Simon D. Levy

   MIT License
 */

#include<ESP8266WiFi.h>
#include "mspparser.hpp"

namespace hf {

    class ESP8266_Receiver : public Receiver, public MspParser {

        private:

            char _ssid[100] = {0};
            char _passwd[100] = {0};

            WiFiServer _server = WiFiServer(80);
            WiFiClient _client;

            bool _haveClient = false;
            bool _hadClient = false;
            bool _gotMessage = false;
            float _sixvals[6] = {0};

        protected:

            void begin(void)
            {
                WiFi.mode(WIFI_AP);
                if (strlen(_passwd) > 0) {
                    WiFi.softAP(_ssid, _passwd, 1, 1);
                }
                else {
                    WiFi.softAP(_ssid); // no password
                }
                _server.begin();
                _haveClient = false;
                _hadClient = false;
                _gotMessage = false;
                memset(_sixvals, 0, 6*sizeof(float));

                MspParser::begin();
            }

            bool gotNewFrame(void)
            {
                if (_haveClient) {

                    if (_client.connected()) {

                        bool retval = false;

                        while (_client.available()) {
                            _gotMessage = false;
                            MspParser::parse(_client.read());
                            if (_gotMessage) {
                                retval = true;
                            }
                        }

                        return retval;
                    }

                    else {
                        _haveClient = false;
                    }
                }

                else {
                    _client = _server.available();
                    if (_client) {
                        _haveClient = true;
                        _hadClient = true;
                    } 
                    else {
                    }
                }

                return false; 
            }

            void readRawvals(void)
            {
                memset(rawvals, 0, MAXCHAN*sizeof(float));
                memcpy(rawvals, _sixvals, 6*sizeof(float));
            }

            bool lostSignal(void)
            {
                return _hadClient && !_haveClient;
            }

            virtual void handle_SET_RC_NORMAL(float  c1, float  c2, float  c3, float  c4, float  c5, float  c6) override
            {
                _gotMessage = true;
                _sixvals[0] = c1;
                _sixvals[1] = c2;
                _sixvals[2] = c3;
                _sixvals[3] = c4;
                _sixvals[4] = c5;
                _sixvals[5] = c6;
            }

         public:

        ESP8266_Receiver(const uint8_t channelMap[6], const float demandScale, const char * ssid, const char * passwd="") 
            : Receiver(channelMap, demandScale) 
        { 
            strcpy(_ssid, ssid);
            strcpy(_passwd, passwd);
        }

    }; // class ESP8266_Receiver

} // namespace hf
