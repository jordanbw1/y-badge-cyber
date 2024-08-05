#include "cyber.h"

const String ssid = "BYU-WiFi";
const String serverUrl = "http://ecen192.byu.edu/";
const int MAX_ATTEMPTS = 5;
const std::string RICKROLL_FILENAME = "/rickroll.wav";

boolean display_password = false;
String ip_address = "";
String app_password = "";
// Following used for polling
unsigned long previousMillis = 0;    // Store the last time the poll was done
const long interval = 2000;          // Interval at which to poll (milliseconds)


void cyber_init() {
    screen_init(); // Initialize the screen
    display_text("Connecting Wifi...");
    cyber_wifi_init(); // Connect to WiFi
    display_text("Getting Credentials...");
    cyber_credentials_init(); // Get IP address from the server
    display_text("Starting LEDs...");
    cyber_color_init(); // Start up the LEDs
}

void cyber_loop() {
    unsigned long currentMillis = millis();
    // Wait for 1 second to poll for commands
    if (currentMillis - previousMillis >= interval) {
        // Save the last time the poll was done
        previousMillis = currentMillis;
    pollForCommands(); // Poll for commands from the server
    }
    // Loop the rest as normal
    screen_loop(ip_address, app_password, display_password); // Display the IP address and password
    Yboard.loop_speaker(); // Loop the speaker (for rickroll)
}

void cyber_wifi_init() {
    // Connect to WiFi
    WiFi.begin(ssid);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to the WiFi network");
}

void cyber_credentials_init() {
    // Get IP address from the server
    while (ip_address == "") {
        delay(500);
        getCredentials();
    }
    Serial.println("IP address: " + ip_address);
}

void cyber_color_init() {
    Serial.begin(115200);
    pinMode(BUTTON1_PIN,INPUT);
    pinMode(BUTTON2_PIN,INPUT);
    pinMode(SWITCH1_PIN,INPUT);
    pinMode(SWITCH2_PIN,INPUT);
    leds_init();
    timer_init();
    all_leds_set_color(255, 255, 255);
}

void getCredentials() {
    printf("Getting credentials from the server\n");
    HTTPClient http;
    http.begin(serverUrl + "/get_credentials");
    int attempts = 0;
    while (true) {
        int httpResponseCode = http.GET();
        if (httpResponseCode > 0) {
            String payload = http.getString();
            DynamicJsonDocument doc(1024);
            deserializeJson(doc, payload);
            if (doc.containsKey("ip_address") && doc.containsKey("password")) {
                ip_address = String(doc["ip_address"].as<const char*>());
                app_password = String(doc["password"].as<const char*>());
                printf("IP Address: %s\n", ip_address.c_str());
                printf("App password: %s\n", app_password.c_str());
                break; // Exit the loop if successful
            } else {
                printf("Error: Server response does not contain 'ip_address' or 'password'\n");
                display_text("Response missing info");
                delay(5000); // Wait for 5 seconds before retrying
            }
        } else {
            printf("Error getting credentials: HTTP request failed with error code %d\n", httpResponseCode);
            display_text("HTTP error: " + String(httpResponseCode));
            delay(5000); // Wait for 5 seconds before retrying
        }
        attempts++;
        if (attempts >= MAX_ATTEMPTS) {
            printf("Exceeded maximum number of attempts. Aborting.\n");
            break;
        }
    }
    http.end();
}

void pollForCommands() {
    HTTPClient http;
    http.begin(serverUrl + "/poll_commands");

    int httpResponseCode = http.GET();
    if (httpResponseCode == 200) {
        String response = http.getString();
        // Process the received commands
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        String command = doc["command"].as<String>();
        printf("Received command: %s\n", command.c_str());
        // Check the command and respond accordingly
        if (command == "change_led_color") {
            int r = doc["r"].as<int>();
            int g = doc["g"].as<int>();
            int b = doc["b"].as<int>();
            printf("Changing LED color to (%d, %d, %d)\n", r, g, b);
            // Implement your LED color change logic here
            all_leds_set_color(r, g, b);
        }
        else if (command == "change_password") {
            String new_password = doc["new_password"].as<String>();
            printf("Changing password to %s\n", new_password.c_str());
            // Implement your password change logic here
            app_password = new_password;
        }
        else if (command == "display_password") {
            display_password = true;
            Serial.println("Display password set to true.");
        }
        else if (command == "hide_password") {
            display_password = false;
            Serial.println("Display password set to false.");
        }
        else if (command == "rickroll") {
            // Implement your rickroll logic here
            printf("RickRolling...\n");
            // Play sound
            YAudio::stop_speaker();
            YAudio::play_sound_file(RICKROLL_FILENAME);
        }
        else {
            printf("Unknown command: %s\n", command.c_str());
        }
    }
    else {
        printf("Error polling: HTTP request failed with error code %d\n", httpResponseCode);
    }
    // End http connection
    http.end();
}

// Tell the server that the command was executed
void confirmCommandExecuted(String command) {
    HTTPClient http;
    String fullUrl = serverUrl + "confirm_command";
    fullUrl += "?command=" + command;
    printf("Calling URL: %s\n", fullUrl.c_str());
    http.begin(fullUrl);
    int httpResponseCode = http.GET();
    // If it fails get fail reason
    // if (httpResponseCode != 200) {
    //     String response = http.getString();
    //     printf("Error confirming command execution: HTTP request failed with error code %d\n", httpResponseCode);
    //     printf("Response: %s\n", http.errorToString(httpResponseCode));
    // }
    // End the connection
    http.end();
    // If successful print confirmation
    // if (httpResponseCode == 200) {
    //     printf("Command execution confirmed\n");
    // }
}
