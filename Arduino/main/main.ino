#include <Arduino.h>
#include <Adafruit_GFX.h>     // Базовая графическая библиотека
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <DHT.h>
#include <ACS712.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

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

//создание объектов
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
DHT dht(DHT_PIN, DHT11);
ACS712 acs(CURRENT_PIN, 3.3, 4095, 185);

OneWire oneWire(DS18B20_PIN);          // Настраиваем шину 1-Wire на нашем пине
DallasTemperature dsSensors(&oneWire);

WiFiClient espClient;
PubSubClient client(espClient);
timeSt test_send_time;

SensorData currentData; //создание объекта структуры

// Таймер для обновления экрана и чтения датчиков
unsigned long lastDisplayUpdate = 0;
unsigned long lastMQTTUpdate = 0;

//для кнопки
bool lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 300;

void setup() {
  Serial.begin(115200);
  dht.begin();
  dsSensors.begin();

  pinMode(FUEL_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);
  pinMode(FLAME_PIN, INPUT);
  pinMode(GAZ_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUT_PIN, INPUT_PULLUP);
  digitalWrite(RELAY_PIN, LOW);
  pinMode(ZUM_PIN, OUTPUT);
  noTone(ZUM_PIN);

  setup_wifi();
  test_send_time.timeSetting();
  client.setCallback(callback);
  client.setServer(SECRET_MQTT_SERVER, SECRET_MQTT_PORT);

  analogWrite(TFT_BL, brightness);
  
  tft.init(240, 320);           
  tft.setRotation(2); // Поворот экрана
  
  // В библиотеке ST7789 константы цветов называются ST77XX_...
  tft.fillScreen(ST77XX_WHITE); 

  tft.drawRGBBitmap(0, 0, vertical_SAF, IMG_WIDTH, IMG_HEIGHT);
  
  tft.setTextColor(ST77XX_RED);
  tft.setTextSize(2);

  tft.setCursor(y_start, x_start); tft.print("Air Temp:");
  tft.setCursor(y_start, x_start + shift); tft.print("Air Hum:");
  tft.setCursor(y_start, x_start + (shift * 2)); tft.print("Fuel Temp:");
  tft.setCursor(y_start, x_start + shift * 3); tft.print("Fuel Level:");
  tft.setCursor(y_start, x_start + shift * 4); tft.print("Current:");
  tft.setCursor(y_start, x_start + shift * 5); tft.print("Flame:");
  tft.setCursor(y_start, x_start + shift * 6); tft.print("Gas:");

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

    test_send_time.timeStam();
    String time_timestamp = String(test_send_time.timeS); //
    sendTelemetryMQTT(time_timestamp);
  }

  bool currentButtonState = digitalRead(BUT_PIN);

  // Проверяем переход с HIGH на LOW И контролируем, прошло ли достаточно времени с прошлого клика
  if (currentButtonState == LOW && lastButtonState == HIGH && (millis() - lastDebounceTime >= DEBOUNCE_DELAY)) {
    lastDebounceTime = millis(); // Сбрасываем таймер
    if (client.connected()) {
      client.publish("BV/SAF/cam/request", "photo");
      Serial.println("Отправлено: photo");
    }
  }
  lastButtonState = currentButtonState;
}