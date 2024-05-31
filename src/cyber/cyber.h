#ifndef CYBER_H
#define CYBER_H
#include "HTTPClient.h"
#include <WiFi.h>
#include <ArduinoJson.h>


void cyber_wifi_init();
void cyber_color_init();
void getCredentials();
void pollForCommands();


#endif 

