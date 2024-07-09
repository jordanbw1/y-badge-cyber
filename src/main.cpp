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
#include "yboard.h"


void setup() {
    Yboard.setup();  // Y-Board
    cyber_init();
}

void loop() {
    cyber_loop();
}
