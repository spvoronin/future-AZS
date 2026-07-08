void readSensors() {
  //DHT11
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (!isnan(h) && !isnan(t)) {   //проверка на число
    currentData.airHumidity = h;  // Записали влажность воздуха
    currentData.airTemp = t;      // Записали температуру воздуха
  }
  
  // temp fuel
  currentData.fuelTemp = 20.5;  // Сюда пойдет код для термопары
  int rawFuel = analogRead(FUEL_PIN);
  currentData.fuelLevel = map(rawFuel, 0, 4095, 0, 100);
  currentData.fuelLevel = constrain(currentData.fuelLevel, 0, 100);  //ограничитель

  // 4. Чтение датчика тока ACS712
  currentData.current_mA = acs.mA_DC();
  // Программный шумодав: если показания прыгают в пределах ±10 мА холостого хода, принудительно пишем 0
  if (abs(currentData.current_mA) < 150) {
    currentData.current_mA = 0;
  }
}

// Функция обновления живых данных на экране
void updateDynamicData() {
  tft.setTextColor(ST7735_BLACK, ST7735_WHITE);
  tft.setTextSize(1);

  // Вывод температуры воздуха (напротив "Air Temp:")
  tft.setCursor(y_data, x_start);
  tft.print(currentData.airTemp, 1);  // 1 знак после запятой
  tft.print("C  ");

  // Вывод влажности воздуха (напротив "Air Hum:")
  tft.setCursor(y_data, x_start + shift);
  tft.print(currentData.airHumidity, 1);
  tft.print("%   ");

  // Вывод температуры топлива с будущей термопары (напротив "Fuel Temp:")
  tft.setCursor(y_data, x_start + (shift * 2));
  tft.print(currentData.fuelTemp, 1);
  tft.print("C  ");

  // Вывод уровня топлива (напротив "Fuel Level:")
  tft.setCursor(y_data, x_start + (shift * 3));
  tft.print(currentData.fuelLevel);
  tft.print("%   ");

  // 5. Ток с ACS712
  tft.setCursor(y_data, x_start + (shift * 4));
  tft.print(currentData.current_mA, 1);
  tft.print("mA  ");
  //Serial.println(currentData.current_mA);

  // 6. Пламя
  tft.setCursor(y_data, x_start + (shift * 5));
  bool flame_tft = map(currentData.flame, 0, 4095, 0, 1);
  tft.print(flame_tft);

  // 7. Газ
  tft.setCursor(y_data, x_start + (shift * 6));
  bool gaz_tft = map(currentData.gaz, 0, 4095, 0, 1);
  tft.print(gaz_tft);
}

void sendTelemetryMQTT(String time_timestamp) {
  // Выделяем память под JSON-документ (300 байт с запасом)
  StaticJsonDocument<300> doc;

  // Заполняем по твоему шаблону
  doc["key"] = "info_about_sensor_SAF";
  doc["uuid"] = SECRET_DEVICE_UUID;
  doc["timestamp"] = time_timestamp;
  doc["electric_current"] = currentData.current_mA;
  doc["flame"] = currentData.flame;
  doc["gas"] = currentData.gaz;
  doc["ambient_humidity"] = currentData.airHumidity;
  doc["ambient_temperature"] = currentData.airTemp;
  doc["tank_temperature"] = currentData.fuelTemp;
  doc["water_level"] = currentData.fuelLevel;

  // Конвертируем JSON в текстовую строку
  String jsonString;
  serializeJson(doc, jsonString);

  // Выводим в Serial для контроля
  Serial.print("Отправка пакета: ");
  Serial.println(jsonString);

  // Если связь с брокером есть - публикуем в топик из secrets.h
  if (client.connected()) {
    client.publish(SECRET_TOPIC_PUB, jsonString.c_str());
  }
}