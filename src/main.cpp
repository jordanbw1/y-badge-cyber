#include <Audio.h>
#include "Arduino.h"
#include "SD.h"
#include "FS.h"
#include "Wire.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_I2CDevice.h>
#include "ybadge.h"
#include "light_show/light_show.h"
#include "wifi_test/wifi_test.h"


void setup() {
    wifi_init();
    // light_show_init();
    // Serial.println("Setup");
}

void loop() {
    // Serial.println("Looping");
    // void light_show_loop();
    send_button_info();
}
