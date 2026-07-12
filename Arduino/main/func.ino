void readSensors() {
  //DHT11
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (!isnan(h) && !isnan(t)) {    // проверка на число
    h = h - h_calb;                //калибровка
    h = constrain(h, 0.0, 100.0);  //ограничение

    currentData.airHumidity = h;
    currentData.airTemp = t;
  }

  /// 2. Т топлива
  dsSensors.requestTemperatures();
  float tempFuel = dsSensors.getTempCByIndex(0);
  if (tempFuel != DEVICE_DISCONNECTED_C) {
    currentData.fuelTemp = tempFuel;
  } else {
    //Serial.println("Ошибка: Датчик DS18B20 не найден или отключен");
  }

  //3. Уровень топлива
  int rawFuel = analogRead(FUEL_PIN);
  currentData.fuelLevel = map(rawFuel, 0, 4095, 0, 100);
  currentData.fuelLevel = constrain(currentData.fuelLevel, 0, 100);  //ограничитель

  // 4. Чтение датчика тока ACS712
  //currentData.current_mA = acs.mA_DC();
  //Программный шумодав : если показания прыгают в пределах ±10 мА холостого хода, принудительно пишем 0
  //if (abs(currentData.current_mA) < 150||abs(currentData.current_mA) < 0) {
  //  currentData.current_mA = 0;
  //}

  currentData.gaz = analogRead(GAZ_PIN);  // Считываем аналоговое значение (0 - 4095)

  // В чистом воздухе датчик обычно выдает в районе 400-800
  // Если значение больше 1300 - это явный газ или дым
  if (currentData.gaz > 1300) {
    tone(ZUM_PIN, 1000); 
  } else {
    noTone(ZUM_PIN);
  }
}

// Функция обновления живых данных на экране
void updateDynamicData() {
  tft.setTextColor(ST77XX_BLACK, ST77XX_WHITE);
  tft.setTextSize(2);

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
  int gaz_tft = map(currentData.gaz, 0, 4095, 0, 100);
  tft.print(gaz_tft);
  tft.print("%   ");
}