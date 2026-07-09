#include <Arduino.h>
#include <Adafruit_GFX.h>     // Базовая графическая библиотека
#include <Adafruit_ST7735.h>  // Библиотека для нашего дисплея ST7735
#include <SPI.h>
#include <DHT.h>
#include <ACS712.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

//подгрузка внутренних файлов
#include "config.h"
#include "foto.h"
#include "secrets.h"
#include "Cl_timestamp.h"  // для timestamp


//подгрузка данных из secrets.h
const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;
const char* mqtt_server = SECRET_MQTT_SERVER;
const int mqtt_port = SECRET_MQTT_PORT;
const char* mqtt_user = SECRET_MQTT_USER;
const char* mqtt_pass = SECRET_MQTT_PASS;
const char* mqtt_topic_pub = SECRET_TOPIC_PUB;

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
DHT dht(DHT_PIN, DHT11);
ACS712 acs(CURRENT_PIN, 3.3, 4095, 185);

WiFiClient espClient;
PubSubClient client(espClient);
timeSt test_send_time;

SensorData currentData; //создание объекта структуры

// Таймер для обновления экрана и чтения датчиков
unsigned long lastDisplayUpdate = 0;
unsigned long lastMQTTUpdate = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
 
  pinMode(FUEL_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);
  pinMode(FLAME_PIN, INPUT);
  pinMode(GAZ_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  setup_wifi();
  test_send_time.timeSetting();
  client.setCallback(callback);
  client.setServer(SECRET_MQTT_SERVER, SECRET_MQTT_PORT);

  analogWrite(TFT_LED, brightness);
  tft.initR(INITR_BLACKTAB);
  tft.setRotation(2);
  tft.fillScreen(ST7735_WHITE);

  tft.drawRGBBitmap(0, 0, vertical_SAF, IMG_WIDTH, IMG_HEIGHT);

  tft.setTextColor(B_RED_L);
  tft.setTextSize(1);

  tft.setCursor(2, x_start); tft.print("Air Temp:");
  tft.setCursor(2, x_start + shift); tft.print("Air Hum:");
  tft.setCursor(2, x_start + (shift * 2)); tft.print("Fuel Temp:");
  tft.setCursor(2, x_start + shift * 3); tft.print("Fuel Level:");
  tft.setCursor(2, x_start + shift * 4); tft.print("Current:");
  tft.setCursor(2, x_start + shift * 5); tft.print("Flame:");
  tft.setCursor(2, x_start + shift * 6); tft.print("Gaz:");
  
  acs.autoMidPoint();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  if (millis() - lastDisplayUpdate >= DISPLAY_INTERVAL) {
    lastDisplayUpdate = millis();

    readSensors();
    updateDynamicData(); 
  }

  if (millis() - lastMQTTUpdate >= MQTT_INTERVAL) {
    lastMQTTUpdate = millis();

    test_send_time.timeStam(); //
    String time_timestamp = String(test_send_time.timeS); //
    sendTelemetryMQTT(time_timestamp); //
  }
}