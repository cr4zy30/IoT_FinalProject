#include <WiFi.h>                // Use WiFi.h for ESP32
#include <PubSubClient.h>

//#define LIGHT_SENSOR_PIN 27      // ESP32 has ADC pins like 34, 35, 36, etc. (check your pinout)

const int LIGHT_SENSOR_PIN = 34;

// Replace with your WiFi credentials
const char *ssid = "Tsvetkovi";
const char *password = "19650413";

// MQTT Broker IP address
const char* mqtt_server = "192.168.50.194";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  
  // Read the input on analog pin (value between 0 and 4095 for ESP32)
  int analog_value = analogRead(LIGHT_SENSOR_PIN);
  Serial.print("Analog Value = ");
  Serial.println(analog_value);   // The raw analog reading

  if (!client.loop()) {
    client.connect("vanieriot");
  }

  // Check light condition and publish to MQTT
  if (analog_value < 401) {  // ESP32 ADC range is 0-4095, so set the threshold accordingly
    client.publish("photoresistor/light", "True");
  } else {
    client.publish("photoresistor/light", "False");
  }

  delay(5000);  // Wait for 5 seconds before reading again
}
