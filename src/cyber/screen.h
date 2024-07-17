#ifndef SCREEN_H
#define SCREEN_H
#include "ybadge.h"
#include "HTTPClient.h"
#include <WiFi.h>
#include <ArduinoJson.h>
#include "colors.h"
#include <Adafruit_GFX.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>

void screen_init();
void screen_loop(String ip_address, String app_password, bool display_password=false);
void display_info(String ip_address, String app_password, bool display_password=false);
void display_text(String text);
void draw_text(String text, int x=0, int y=0);

// Screen Constants
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SCREEN_TITLE_HEIGHT 16
#define SCREEN_BODY_HEIGHT 48

// Screen Orientation
#define ZERO_DEG 0
#define NINETY_DEG 1
#define ONE_EIGHTY_DEG 2
#define TWO_SEVENTY_DEG 3

// Screen Brightness
#define BRIGHTNESS_DAMPER 0.8 // 0 is brightest
#define REFRESH_RATE 50       // Measured in ms

// Colors
#define OFF 0
#define ON 1

// On-Screen Info
#define TEXT_WIDTH 5
#define TEXT_HEIGHT 8

#endif 

