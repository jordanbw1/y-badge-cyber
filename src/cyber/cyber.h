#ifndef CYBER_H
#define CYBER_H
#include "ybadge.h"
#include "HTTPClient.h"
#include <WiFi.h>
#include <ArduinoJson.h>
#include "colors.h"

void cyber_init();
void cyber_loop();
void cyber_credentials_init();
void cyber_wifi_init();
void cyber_color_init();
void getCredentials();
void pollForCommands();


#endif 

