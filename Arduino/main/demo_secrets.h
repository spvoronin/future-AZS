//переменуйте этот файл в secrets.h и введите ваши данные
#pragma once

// Настройки Wi-Fi
const char* SECRET_SSID = "Название вашей сети WiFi";
const char* SECRET_PASS = "Пароль от вашего WiFi";

// Настройки MQTT брокера
const char* SECRET_MQTT_SERVER = "ваш MQTT сервер";
const int SECRET_MQTT_PORT = 12345; //порт
const char* SECRET_MQTT_USER = "имя устройства";
const char* SECRET_MQTT_PASS = "пароль";

// Топики
const char* SECRET_TOPIC_PUB = "топик";
const char* SECRET_DEVICE_UUID = "ваш uuid";