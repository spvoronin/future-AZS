#pragma once
#include <Arduino.h>

// === НАСТРОЙКИ ПИНОВ ===
#define TFT_CS 5
#define TFT_RST 4
#define TFT_DC 2
#define TFT_BL 21
#define DHT_PIN 14
#define FUEL_PIN 34     // Аналоговый пин для уровня топлива (ADC1)
#define CURRENT_PIN 35  // Аналоговый пин для датчика тока ACS712 (ADC1)
#define FLAME_PIN 32
#define GAZ_PIN 33
#define RELAY_PIN 27
#define DS18B20_PIN 26
#define ZUM_PIN 25
#define BUT_PIN 13

// === НАСТРОЙКИ ЦВЕТОВ И ИНТЕРФЕЙСА ДИСПЛЕЯ ===
#define RED_L 0xE8C6            //красный лукойл
#define ILI9341_RED_L_B 0x9800  //тёмно-красный
const int brightness = 255;     // яркость
const int x_start = 100;        //начальная точка тектса по x
const int shift = 20;           //регулируемый межстрочный интервал
const int y_data = 150;         //положение данных влево/вправо
const int y_start = 10;         //начало надписей

// === НАСТРОЙКИ ТАЙМЕРОВ (ИНТЕРВАЛЫ) ===
const unsigned long DISPLAY_INTERVAL = 1000;  // вывод на экран, опрос датчиков
const unsigned long MQTT_INTERVAL = 5000;     // отправка на сервер

// === сколько времени номер будет отображаться на экране
// 1 минута = 60000 мс | 3 минуты = 180000 мс | 5 минут = 300000 мс
#define CAM_RESPONSE_TIMEOUT 180000

// === СТРУКТУРА И ДАТЧИКИ ===
struct SensorData {
  float airTemp = 0.0;
  float airHumidity = 0.0;
  float fuelTemp = 0.0;
  int fuelLevel = 0;
  float current_mA = 0.0;
  bool flame = false;
  int gaz = 0;
  bool relay = false;
};

const int h_calb = 0;  //разница для калибровки влажности DHT11