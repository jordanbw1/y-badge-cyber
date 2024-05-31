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
#include "cyber/cyber.h"


void setup() {
    cyber_wifi_init();
}

void loop() {
    pollForCommands();
    delay(1000); // Adjust polling interval as needed
}
