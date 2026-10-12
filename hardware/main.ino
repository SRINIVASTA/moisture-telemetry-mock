#include <WiFi.h>
#include <PubSubClient.h> 

#define MOISTURE_PIN 34  
const int DRY_THRESHOLD = 20;
const int WET_THRESHOLD = 80;

const char* mqtt_server = "://hivemq.com"; 
const char* mqtt_topic = "sfic2026/krishitwin/moisture"; 

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  pinMode(MOISTURE_PIN, INPUT);

  Serial.print("Connecting to Virtual Wi-Fi...");
  WiFi.begin("Wokwi-GUEST", "", 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Linked!");
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    while (!client.connected()) {
      Serial.print("Connecting to MQTT Broker...");
      if (client.connect("ESP32_KrishiTwin_Client")) {
        Serial.println("Connected!");
      } else {
        delay(2000);
      }
    }
  }
  client.loop();

  int raw_value = analogRead(MOISTURE_PIN);
  int moisture_percent = map(raw_value, 0, 4095, 0, 100);

  char msg[50];
  snprintf(msg, 50, "%d", moisture_percent);
  client.publish(mqtt_topic, msg);
  
  Serial.print("📡 Data transmitted: ");
  Serial.print(msg);
  Serial.println("%");

  delay(1000); 
}
