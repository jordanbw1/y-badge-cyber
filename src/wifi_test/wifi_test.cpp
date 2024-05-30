#include "wifi_test.h"
#include "ybadge.h"

const char* ssid = "";
const char* password =  "";
const char* serverUrl = "http://{{YOUR_URL_HERE}}/";
int knobVal;
void wifi_init() {
    pinMode(BUTTON2_PIN, INPUT);
    pinMode(SWITCH1_PIN, INPUT);
    pinMode(SWITCH2_PIN, INPUT);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        printf("Connecting to WiFi..\n");
    }
    printf("Connected to the WiFi network\n");
    knobVal = knob_get();
    
}

void send_data(String jsonData, String endpoint) {
    HTTPClient http;
    String fullUrl = serverUrl + endpoint;
    http.begin(fullUrl);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonData);
    http.end();
}

void send_button_info() {
    if (knobVal != knob_get()) {
        String jsonData = "{\"data\":\"Knob at " + String(knob_get()) + "%\"}";
        send_data(jsonData, "knob");
        knobVal = knob_get();
    }

    bool pressed = false;
    static int buttonState = 0;
    for (int i = 1; i <= 3; i++) {
        if (buttons_get(i)) {
            pressed = true;
            String jsonData = "{\"data\":\"Button " + String(i) + " pressed\"}";
            send_data(jsonData,"button");
            buttonState = i;
            while(buttons_get(i)) {}
        }
    }
    if (!pressed && buttonState != 0) {
        String jsonData = "{\"data\":\"Nothing pressed\"}";
        send_data(jsonData,"button");
        buttonState = 0;
    }


    static int switchState = 0;

    if (switches_get(1) && switches_get(2)) {
        if (switchState != 3) {
            String jsonData = "{\"data\":\"Both switches on\"}";
            send_data(jsonData, "switch");
            switchState = 3;
        }
    } else if (switches_get(2)) {
        if (switchState != 2) {
            String jsonData = "{\"data\":\"Switch 2 on\"}";
            send_data(jsonData, "switch");
            switchState = 2;
        }
    } else if (switches_get(1)) {
        if (switchState != 1) {
            String jsonData = "{\"data\":\"Switch 1 on\"}";
            send_data(jsonData, "switch");
            switchState = 1;
        }
    } else {
        if (switchState != 0) {
            String jsonData = "{\"data\":\"Both switches off\"}";
            send_data(jsonData, "switch");
            switchState = 0;
        }
    }

}

