#include <Arduino.h>
#include <Adafruit_GFX.h>     // Базовая графическая библиотека
#include <Adafruit_ST7735.h>  // Библиотека для нашего дисплея ST7735
#include <SPI.h>
#include <DHT.h>
#include <ACS712.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "foto.h"
#include "secrets.h"
#include "Cl_timestamp.h"  // для timestamp

const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;
const char* mqtt_server = SECRET_MQTT_SERVER;
const int mqtt_port = SECRET_MQTT_PORT;
const char* mqtt_user = SECRET_MQTT_USER;
const char* mqtt_pass = SECRET_MQTT_PASS;
const char* mqtt_topic_pub = SECRET_TOPIC_PUB;

// Цвета
#define RED_L 0xE8C6
#define B_RED_L 0x9800

const int brightness = 255;  // Яркость
const int x_start = 45;      //начальная точка тектса по x
const int shift = 14;        //регулируемый межстрочный интервал

// Пины
#define TFT_CS 5
#define TFT_RST 4
#define TFT_DC 2
#define TFT_LED 21
#define DHT_PIN 12
#define FUEL_PIN 34     // Аналоговый пин для уровня топлива (ADC1)
#define CURRENT_PIN 35  // Аналоговый пин для датчика тока ACS712 (ADC1)
#define FLAME_PIN 32    
#define GAZ_PIN 33      
#define RELAY_PIN 15

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
DHT dht(DHT_PIN, DHT11);
ACS712 acs(CURRENT_PIN, 3.3, 4095, 367);

WiFiClient espClient;
PubSubClient client(espClient);
timeSt test_send_time;

struct SensorData {
  float airTemp = 0.0;      // Температура воздуха
  float airHumidity = 0.0;  // Влажность воздуха
  float fuelTemp = 0.0;     // Температура топлива
  int fuelLevel = 0;        // Уровень топлива в %
  float current_mA = 0.0;   //ток
  bool flame = false;       //пламя
  int gaz = 0;              //газ
};
SensorData currentData;

unsigned long lastUpdate = 0;
const unsigned long INTERVAL = 1000;

void setup() {
  Serial.begin(115200);
  dht.begin();
 
  pinMode(FUEL_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);
  pinMode(FLAME_PIN, INPUT);
  pinMode(GAZ_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  acs.autoMidPoint();

  setup_wifi();
  test_send_time.timeSetting();
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
}

void loop() {
  // Поддержание связи с брокером
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  if (millis() - lastUpdate >= INTERVAL) {
    lastUpdate = millis();

    test_send_time.timeStam();  // обновление
    String time_timestamp = String(test_send_time.timeS);

    readSensors();
    updateDynamicData();

    sendTelemetryMQTT(time_timestamp);
  }
}