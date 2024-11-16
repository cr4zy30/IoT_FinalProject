#include <WiFi.h>
#include <PubSubClient.h>

const int LIGHT_SENSOR_PIN = 34;
const char *ssid = "Tsvetkovi";
const char *password = "19650413";
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
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  int analog_value = analogRead(LIGHT_SENSOR_PIN);
  Serial.print("Analog Value = ");
  Serial.println(analog_value);

  int light_percentage = map(analog_value, 0, 4095, 0, 100);
  char percentage_str[5];
  snprintf(percentage_str, sizeof(percentage_str), "%d", light_percentage);

  client.publish("photoresistor/light_intensity", percentage_str);
  client.publish("photoresistor/light", analog_value < 401 ? "True" : "False");

  delay(5000);
}
