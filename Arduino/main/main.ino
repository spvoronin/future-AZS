#include <Arduino.h>
#include <Adafruit_GFX.h>     // Базовая графическая библиотека
#include <Adafruit_ST7735.h>  // Библиотека для нашего дисплея ST7735
#include <SPI.h>
#include <DHT.h>
#include <ACS712.h>

#include "foto.h"
//   #include "Cl_timestamp.h"  // для timestamp

// Цвета
#define RED_L 0xE8C6
#define B_RED_L 0x9800

const int brightness = 255;  // Яркость
const int x_start = 25;      //начальная точка тектса по x
const int shift = 14;        //регулируемый межстрочный интервал

// Пины
#define TFT_CS 5
#define TFT_RST 4
#define TFT_DC 2
#define TFT_LED 21
#define DHT_PIN 12
#define FUEL_PIN 34     // Аналоговый пин для уровня топлива (ADC1)
#define CURRENT_PIN 35  // Аналоговый пин для датчика тока ACS712 (ADC1)
#define RELAY_PIN 15

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
DHT dht(DHT_PIN, DHT11);
ACS712 acs(CURRENT_PIN, 3.3, 4095, 33.77);
timeSt test_send_time;

struct SensorData {
  float airTemp = 0.0;      // Температура воздуха
  float airHumidity = 0.0;  // Влажность воздуха
  float fuelTemp = 0.0;     // Температура топлива
  int fuelLevel = 0;        // Уровень топлива в %
  float current_mA = 0.0;   //ток
  int flame = 0;
  int gaz = 0;
};
SensorData currentData;

unsigned long lastUpdate = 0;
const unsigned long INTERVAL = 1000;

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(FUEL_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);

  acs.autoMidPoint();

  analogWrite(TFT_LED, brightness);
  tft.initR(INITR_BLACKTAB);
  tft.setRotation(1);
  tft.fillScreen(ST7735_WHITE);

  tft.drawRGBBitmap(0, 0, SAF, IMG_WIDTH, IMG_HEIGHT);


  tft.setTextColor(B_RED_L);
  tft.setTextSize(1);

  tft.setCursor(2, x_start);
  tft.print("Air Temp:");

  tft.setCursor(2, x_start + shift);
  tft.print("Air Hum:");

  tft.setCursor(2, x_start + (shift * 2));
  tft.print("Fuel Temp:");

  tft.setCursor(2, x_start + shift * 3);
  tft.print("Fuel Level:");

  tft.setCursor(2, x_start + shift * 4);
  tft.print("Current:");

  tft.setCursor(2, x_start + shift * 5);
  tft.print("Flame:");

  tft.setCursor(2, x_start + shift * 6);
  tft.print("Gaz:");

   //test_send_time.timeSetting("pool.ntp.org", 3 * 3600, 0);  // для timestamp | GMT+3 (Москва) = 3 * 3600 секунд, Летнее время (0, если не используется)
}

void loop() {
  if (millis() - lastUpdate >= INTERVAL) {
    lastUpdate = millis();
    //est_send_time.timeStam();  // обновление
    //String time = String(test_send_time.timeS)
    readSensors();
    updateDynamicData();
  }
}