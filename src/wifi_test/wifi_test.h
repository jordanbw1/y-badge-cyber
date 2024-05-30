#ifndef WIFI_TEST_H
#define WIFI_TEST_H
#include "HTTPClient.h"
#include <WiFi.h>




void wifi_init();
void send_data(String httpRequestData,String endpoint);
void send_button_info();


#endif 

