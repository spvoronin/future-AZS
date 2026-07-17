#define RL_RESISTOR 1000.0    // Сопротивление резистора нагрузки на плате модуля (обычно 1 кОм = 1000 Ом)
#define R0_CLEAN_AIR 10000.0  // Сопротивление датчика в чистом воздухе (примерно 10 кОм = 10000 Ом)
#define MQ2_A_COEFF 574.25    // Коэффициент 'a' из даташита для сжиженного газа (LPG)
#define MQ2_B_COEFF -2.222    // Коэффициент 'b' из даташита для сжиженного газа (LPG)

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

  currentData.gaz = getGasPPM();
  if (currentData.gaz > 9999) {
    currentData.gaz = 0;
  }

  //zummer
  if (currentData.flame || (millis() > 60000 && currentData.gaz > 600)) {
    tone(ZUM_PIN, 1000);
  } else {
    noTone(ZUM_PIN);
  }

  int rawFlame = analogRead(FLAME_PIN);
  if (rawFlame < 1500) {
    currentData.flame = true;
  } else {
    currentData.flame = false;
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

  // Вывод температуры топлива с термопары (напротив "Fuel Temp:")
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

  if (currentData.flame) {
    tft.setTextColor(ST77XX_RED, ST77XX_WHITE);
    tft.print("ALARM");
  } else {
    tft.setTextColor(ST77XX_BLACK, ST77XX_WHITE);
    tft.print("SAFE ");
  }

  // 7. Газ
  tft.setTextColor(ST77XX_BLACK, ST77XX_WHITE);
  tft.setCursor(y_data, x_start + (shift * 6));
  //int gaz_tft = map(currentData.gaz, 0, 4095, 0, 100);
  tft.print(currentData.gaz);
  tft.print("ppm   ");
}

float getGasPPM() {  //перевод показаний газоанализатора в ppm
  // 1. Считываем сырое значение АЦП (для ESP32 это диапазон 0...4095)
  int rawADC = analogRead(GAZ_PIN);

  // 2. Переводим АЦП в Вольты. У ESP32 опорное напряжение 3.3В
  float voltage = (float)rawADC * (3.3 / 4095.0);

  // Защита от деления на ноль, если датчик отключен или пин притянут к земле
  if (voltage < 0.1) {
    return 0.0;
  }

  // 3. Вычисляем текущее сопротивление датчика Rs по формуле делителя напряжения
  // Rs = ((Vcc - Vout) * Rl) / Vout
  float Rs = ((3.3 - voltage) * RL_RESISTOR) / voltage;

  // 4. Находим отношение Rs к R0 (сопротивлению в чистом воздухе)
  float ratio = Rs / R0_CLEAN_AIR;

  // 5. Вычисляем итоговое значение PPM по степенной функции pow(основание, степень)
  float ppm = MQ2_A_COEFF * pow(ratio, MQ2_B_COEFF);

  return ppm;
}

String convertPlateToLatin(String input) {  //декодирование номера машины
  String result = "";

  for (size_t i = 0; i < input.length(); i++) {
    unsigned char c = input[i];

    // Русские буквы в UTF-8 кодируются двумя байтами. Первый байт всегда 0xD0 или 0xD1.
    if (c == 0xD0 && i + 1 < input.length()) {
      unsigned char next = input[i + 1];
      i++;  // Пропускаем второй байт, так как мы его сейчас обработаем

      switch (next) {
        // ЗАГЛАВНЫЕ РУССКИЕ БУКВЫ -> ЛАТИНСКИЕ ОРИГИНАЛЫ
        case 0x90: result += 'A'; break;  // А
        case 0x92: result += 'B'; break;  // В
        case 0x95: result += 'E'; break;  // Е
        case 0x9A: result += 'K'; break;  // К
        case 0x9C: result += 'M'; break;  // М
        case 0x9D: result += 'H'; break;  // Н
        case 0x9E: result += 'O'; break;  // О
        case 0xA0: result += 'P'; break;  // Р
        case 0xA1: result += 'C'; break;  // С
        case 0xA2: result += 'T'; break;  // Т
        case 0xA3: result += 'Y'; break;  // У
        case 0xA5:
          result += 'X';
          break;  // Х

        // Строчные русские буквы (на случай, если пришлют маленькими)
        case 0xB0: result += 'A'; break;  // а
        case 0xB2: result += 'B'; break;  // в
        case 0xB5: result += 'E'; break;  // е
        case 0xBA: result += 'K'; break;  // к
        case 0xBC: result += 'M'; break;  // м
        case 0xBD: result += 'H'; break;  // н
        case 0xBE: result += 'O'; break;  // о

        default: result += '?'; break;  // Если прилетела русская буква, которой нет в номерах (например, Б, Г, Д)
      }
    } else if (c == 0xD1 && i + 1 < input.length()) {
      unsigned char next = input[i + 1];
      i++;  // Пропускаем второй байт

      switch (next) {
        // Строчные буквы из диапазона 0xD1
        case 0x80: result += 'P'; break;  // р
        case 0x81: result += 'C'; break;  // с
        case 0x82: result += 'T'; break;  // т
        case 0x83: result += 'Y'; break;  // у
        case 0x85: result += 'X'; break;  // х

        default: result += '?'; break;
      }
    } else {
      // Все остальные символы (цифры, пробелы, дефисы и английские буквы) оставляем без изменений
      result += (char)c;
    }
  }
  return result;
}