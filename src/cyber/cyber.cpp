#include "cyber.h"

const String ssid = "";
const String password =  "";
const String serverUrl = "http://{{YOUR_SERVER_URL_HERE}}/";

String app_identifier = "";
String app_password = "";

void cyber_wifi_init() {
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to the WiFi network");

    // Get identifier and password from the server
    while (app_identifier == "" || app_password == "") {
        delay(500);
        getCredentials();
    }
}

void cyber_color_init() {
    // Implement your LED color initialization logic here
}

void getCredentials() {
    printf("Getting credentials from the server\n");
    HTTPClient http;
    http.begin(serverUrl + "/get_credentials");
    int httpResponseCode = http.GET();
    if (httpResponseCode > 0) {
        String payload = http.getString();
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, payload);
        app_identifier = String(doc["identifier"].as<const char*>());
        app_password = String(doc["password"].as<const char*>());
    }
    http.end();
}

void pollForCommands() {
    HTTPClient http;
    http.begin(serverUrl + "/poll_commands");;

    int httpResponseCode = http.GET();
    if (httpResponseCode == 200) {
        String response = http.getString();
        // Process the received commands
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        String command = doc["command"].as<String>();
        printf("Received command: %s\n", command.c_str());
        if (command == "change_led_color") {
            int r = doc["r"].as<int>();
            int g = doc["g"].as<int>();
            int b = doc["b"].as<int>();
            // Implement your LED color change logic here
        }
    }
    http.end();
}
